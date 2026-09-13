#!/usr/bin/env node
/**
 * CwClient ↔ Cw_WebUi 镜像工具。
 *
 * 镜像集（`mirror.manifest.json` 的 `entries`）必须与源端**逐字节相同** —— 这正是
 * 「镜像同步失败时可以直接整体替换」的前提：目标端不需要任何翻译步骤，源端就是它的备份。
 * 因此本文件里的复制一律走字节级 API（`readFileSync` / `writeFileSync`），
 * **绝不**经过任何会规范化行尾的文本入口（`read_text`/`write_text` 那类）。
 *
 *   node scripts/mirror.mjs --check           # 只报漂移，不改盘；有漂移则退出码 1
 *   node scripts/mirror.mjs --apply           # 源 → 目标，逐字节整份覆盖
 *   node scripts/mirror.mjs --apply --prune   # 顺带删掉源侧已不存在的镜像文件
 *
 * 本工具对源端**只读**（只 `readFileSync`），所以源端的 `git status` 在任何操作后都必须为空。
 */
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const CLIENT_ROOT = path.resolve(HERE, '..')

function readManifest() {
  const raw = fs.readFileSync(path.join(CLIENT_ROOT, 'mirror.manifest.json'), 'utf8')
  const manifest = JSON.parse(raw)
  return {
    sourceRoot: path.resolve(CLIENT_ROOT, manifest.source),
    entries: manifest.entries,
    scanRoots: manifest.scanRoots,
  }
}

function walk(dir) {
  const acc = []
  if (!fs.existsSync(dir)) return acc
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) acc.push(...walk(full))
    else acc.push(full)
  }
  return acc
}

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
}

/** 镜像集内**未被清单收录**的文件。两端都查：源端漏收 = 新页面没被镜像；目标端多出 = 违规本地改动。 */
function uncovered(root, entries, scanRoots) {
  const listed = new Set(entries)
  const found = []
  for (const sub of scanRoots) {
    for (const full of walk(path.join(root, sub))) {
      const rel = path.relative(root, full).split(path.sep).join('/')
      if (!listed.has(rel)) found.push(rel)
    }
  }
  return found.sort()
}

function statusOf(rel, sourceRoot) {
  const src = path.join(sourceRoot, rel)
  const dst = path.join(CLIENT_ROOT, rel)
  if (!fs.existsSync(src)) return 'NO_SOURCE'
  if (!fs.existsSync(dst)) return 'MISSING'
  return sha256(src) === sha256(dst) ? 'SAME' : 'DRIFTED'
}

function reportDifferences(rows) {
  const bad = rows.filter((row) => row.status !== 'SAME')
  for (const row of bad) console.log(`  ${row.status.padEnd(9)} ${row.rel}`)
  return bad
}

/** 两端各自的「未收录文件」，逐条打印后并成 bad 行。 */
function collectExtras(roots, entries, scanRoots) {
  const rows = []
  for (const [tag, root] of roots) {
    const found = uncovered(root, entries, scanRoots)
    if (!found.length) continue
    console.log(`  ${tag} (${found.length}) —— 未收录进清单，无法镜像:`)
    for (const rel of found) console.log(`    ${rel}`)
    rows.push(...found.map((rel) => ({ rel, status: tag })))
  }
  return rows
}

function check() {
  const { sourceRoot, entries, scanRoots } = readManifest()
  const rows = entries.map((rel) => ({ rel, status: statusOf(rel, sourceRoot) }))
  const bad = reportDifferences(rows)
  const same = rows.filter((row) => row.status === 'SAME').length
  console.log(`--check: ${entries.length} entries, ${same} SAME, ${entries.length - same} drifted`)
  bad.push(
    ...collectExtras(
      [
        ['EXTRA_SOURCE', sourceRoot],
        ['EXTRA_TARGET', CLIENT_ROOT],
      ],
      entries,
      scanRoots
    )
  )
  if (bad.length === 0) console.log('OK: mirror is byte-identical to Cw_WebUi')
  return bad.length === 0 ? 0 : 1
}

function copyOne(rel, sourceRoot) {
  const src = path.join(sourceRoot, rel)
  const dst = path.join(CLIENT_ROOT, rel)
  if (!fs.existsSync(src)) return 'NO_SOURCE'
  const before = fs.existsSync(dst) ? sha256(dst) : null
  const after = sha256(src)
  if (before === after) return 'SAME'
  fs.mkdirSync(path.dirname(dst), { recursive: true })
  fs.writeFileSync(dst, fs.readFileSync(src))
  return before === null ? 'ADDED' : 'UPDATED'
}

function pruneExtras(entries, scanRoots) {
  let removed = 0
  for (const rel of uncovered(CLIENT_ROOT, entries, scanRoots)) {
    fs.rmSync(path.join(CLIENT_ROOT, rel))
    console.log(`  PRUNED    ${rel}`)
    removed++
  }
  return removed
}

function apply(prune) {
  const { sourceRoot, entries, scanRoots } = readManifest()
  const counts = { ADDED: 0, UPDATED: 0, SAME: 0, NO_SOURCE: 0 }
  for (const rel of entries) {
    const action = copyOne(rel, sourceRoot)
    counts[action]++
    if (action !== 'SAME') console.log(`  ${action.padEnd(9)} ${rel}`)
  }
  const pruned = prune ? pruneExtras(entries, scanRoots) : 0
  console.log(
    `--apply: ${entries.length} entries — ADDED ${counts.ADDED}, UPDATED ${counts.UPDATED}, ` +
      `UNCHANGED ${counts.SAME}, PRUNED ${pruned}, NO_SOURCE ${counts.NO_SOURCE}`
  )
  return counts.NO_SOURCE === 0 ? 0 : 1
}

const argv = process.argv.slice(2)
process.exit(argv.includes('--apply') ? apply(argv.includes('--prune')) : check())

#!/usr/bin/env node
/**
 * 开发态编排：起 Vite dev server → 把它的 URL 交给 Electron 主进程。
 *
 * 不引 `concurrently` / `wait-on`：Vite 有 Node API，`await server.listen()` 返回时端口已经在听，
 * 不存在「先起 electron 但 dev server 还没就绪」的竞态，也就不需要轮询等待的依赖。
 * 这也是本项目客户端侧新增依赖只有 `electron`(+打包期 `electron-builder`) 的原因之一。
 */
import { spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { createServer } from 'vite'
import electronPath from 'electron'

/** 必须是后端 CORS 白名单里的端口（见 electron/static-server.cjs 与 README）。 */
const DEV_PORT = 5173
/** `root` 用 fileURLToPath 而不是 URL.pathname：后者在 Windows 上会给出 `/E:/...` 这种非法路径。 */
const CLIENT_ROOT = fileURLToPath(new URL('..', import.meta.url))

const server = await createServer({
  root: CLIENT_ROOT,
  server: { port: DEV_PORT, strictPort: true },
})
await server.listen()
server.printUrls()

const url = server.resolvedUrls?.local?.[0]
if (!url) {
  console.error('[dev] Vite dev server 没有返回本地 URL，无法确定加载地址')
  await server.close()
  process.exit(1)
}
console.log(`[dev] 启动 Electron，加载 ${url}`)

// `npm run dev -- --remote-debugging-port=9333` 之类的额外参数原样转给 Electron。
const child = spawn(electronPath, ['.', ...process.argv.slice(2)], {
  stdio: 'inherit',
  cwd: CLIENT_ROOT,
  env: { ...process.env, VITE_DEV_SERVER_URL: url },
})

let closing = false
async function shutdown(code) {
  if (closing) return
  closing = true
  await server.close()
  process.exit(code ?? 0)
}

child.on('close', (code) => shutdown(code))
process.on('SIGINT', () => {
  child.kill()
  shutdown(0)
})

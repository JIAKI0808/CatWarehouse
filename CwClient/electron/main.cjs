'use strict'
/**
 * Electron 主进程：开窗口，并把渲染层指到正确的 URL。
 *
 *   dev  —— `VITE_DEV_SERVER_URL` 由 `scripts/dev.mjs` 注入（Vite dev server，端口 5173）
 *   prod —— 起回环静态服务器指向 `dist/`（端口 5173 或 5175，见 static-server.cjs 的说明）
 *
 * 主进程用 CommonJS（`.cjs` 后缀）：`package.json` 必须是 `"type": "module"`（Vite 配置与
 * `scripts/*.mjs` 需要），而 `.cjs` 后缀可以无视该字段，从而避开「Electron 主进程 ESM 支持」
 * 这一版本相关的不确定性。
 */
const fs = require('node:fs')
const path = require('node:path')
const { app, BrowserWindow, dialog, shell } = require('electron')
const { startStaticServer } = require('./static-server.cjs')

const DIST = path.join(__dirname, '..', 'dist')
const DEV_URL = process.env.VITE_DEV_SERVER_URL
/** 后端 CORS 白名单（CwServer/core/config.py:8）里的两个源，端口顺序即优先级。 */
const CORS_PORTS = [5173, 5175]

let staticServer = null

function createWindow(url) {
  const win = new BrowserWindow({
    width: 1360,
    height: 860,
    minWidth: 1024,
    minHeight: 640,
    title: 'CatWareHouse',
    show: false,
    backgroundColor: '#1a1a1a',
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true },
  })
  win.once('ready-to-show', () => win.show())
  // 站外链接交给系统浏览器，不在应用窗口里顶掉界面。
  win.webContents.setWindowOpenHandler(({ url: target }) => {
    if (/^https?:/i.test(target)) shell.openExternal(target)
    return { action: 'deny' }
  })
  win.loadURL(url).catch((err) => {
    dialog.showErrorBox('CatWareHouse 渲染层加载失败', `${url}\n\n${err && err.message ? err.message : err}`)
    app.quit()
  })
  return win
}

async function resolveAppUrl() {
  if (DEV_URL) return DEV_URL
  if (!fs.existsSync(path.join(DIST, 'index.html'))) {
    throw new Error('未找到 dist/index.html —— 生产态请先执行 `npm run build`，或用 `npm run dev` 起开发态。')
  }
  const started = await startStaticServer(DIST, CORS_PORTS)
  staticServer = started.server
  staticServer.on('error', (err) => console.error('[static-server]', err))
  return `http://localhost:${started.port}/`
}

app.whenReady().then(async () => {
  try {
    createWindow(await resolveAppUrl())
  } catch (err) {
    dialog.showErrorBox('CatWareHouse 启动失败', String((err && err.message) || err))
    app.quit()
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    resolveAppUrl().then(createWindow).catch((err) => console.error('[activate]', err))
  }
})

app.on('before-quit', () => {
  if (staticServer) staticServer.close()
})

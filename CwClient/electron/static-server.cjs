'use strict'
/**
 * 回环静态服务器：把 `dist/` 用 `http://localhost:<port>/` 暴露出来。
 *
 * 为什么非要起一个 HTTP 服务器，而不是 `win.loadFile()`：网页端 `src/router/index.ts` 用的是
 * `createWebHistory`，在 `file://` 下 `history.pushState` 会因 origin 为 `null` 抛 SecurityError。
 * 而**端口不能随便挑** —— 后端 CORS 白名单只认 `http://localhost:5173` / `5175`
 * （`CwServer/core/config.py:8`），所以只有这两个端口能让渲染层带着合法的 Origin 去调后端。
 * 详见 README「为什么是 5173/5175」。
 */
const fs = require('node:fs')
const http = require('node:http')
const path = require('node:path')

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
}

/**
 * 解析请求路径。返回绝对文件路径，或 `null` 表示该 404。
 *
 * 两条规则，别合并：
 *   带扩展名（`/assets/x.js`）→ 命中就给文件，**没命中就是 404**。回退成 index.html 会让
 *   浏览器拿到一份 HTML 却按 JS 解析，报出的语法错误与真正的原因（资产缺失）毫无关系。
 *   不带扩展名（`/analytics`）→ 回退 index.html，前端路由才能刷新存活。
 */
function resolveFile(root, requestUrl) {
  const base = path.resolve(root)
  const urlPath = decodeURIComponent(String(requestUrl || '/').split('?')[0])
  // 先按 posix 归一化再拼接：`..` 会被折叠在虚拟根之内，所以拼接结果不可能逃出 base。
  const safePath = path.posix.normalize('/' + urlPath)
  const target = path.join(base, safePath)
  if (path.extname(safePath)) {
    return fs.existsSync(target) && fs.statSync(target).isFile() ? target : null
  }
  return path.join(base, 'index.html')
}

function createHandler(root) {
  return (req, res) => {
    const file = resolveFile(root, req.url)
    if (file === null) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
      res.end('Not Found')
      return
    }
    fs.readFile(file, (err, body) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
        res.end('Not Found')
        return
      }
      const type = MIME[path.extname(file).toLowerCase()] || 'application/octet-stream'
      res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' })
      res.end(body)
    })
  }
}

/** 只绑 127.0.0.1：不需要局域网可访问，也就不必开防火墙口子。 */
function listenOn(server, port) {
  return new Promise((resolve, reject) => {
    const onError = (err) => {
      server.removeListener('listening', onListening)
      reject(err)
    }
    const onListening = () => {
      server.removeListener('error', onError)
      resolve(port)
    }
    server.once('error', onError)
    server.once('listening', onListening)
    server.listen(port, '127.0.0.1')
  })
}

/** 依次尝试 `ports`，返回第一个绑上的端口。顺序即优先级，不静默降级到白名单外的端口。 */
async function startStaticServer(root, ports) {
  const server = http.createServer(createHandler(root))
  for (const port of ports) {
    try {
      return { server, port: await listenOn(server, port) }
    } catch (err) {
      if (err.code !== 'EADDRINUSE') throw err
    }
  }
  throw new Error(
    `端口 ${ports.join(' / ')} 都被占用。后端 CORS 白名单只接受这两个端口，` +
      `请先关掉占用它们的程序（通常是 Cw_WebUi 的 npm run dev），再启动客户端。`
  )
}

module.exports = { startStaticServer }

import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// 与 Cw_WebUi/vite.config.ts 结构相同，但**故意不放进镜像集**（见 README「为什么构建配置不镜像」）：
// 网页端实际生效的是它那份 `vite.config.js`（Vite 的配置文件解析顺序里 .js 先于 .ts），
// 镜像 .ts 会得到「镜像的是不生效的那份」这种最难查的漂移。这里保持同构、由客户端自己拥有。
//
// dev server 的端口/严格模式由 scripts/dev.mjs 在 createServer 时注入，不写进本文件 ——
// 端口必须是 5173/5175，因为后端 CORS 白名单只认这两个值（见 README）。
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})

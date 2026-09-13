# CwClient — CatWareHouse 桌面客户端

Electron + Vue 3 + Naive UI 的桌面客户端，后端接口与 [`Cw_WebUi`](../Cw_WebUi) 完全一致。

它的渲染层**不是「参考网页端重写」的**，而是网页端 `src/` 的**逐字节镜像**。
这样做的目的只有一个：**网页端改了哪个页面，客户端一条命令就能跟上；哪天镜像机制不好使了，
把文件整份覆盖回去就行，不需要任何翻译步骤。**

## 快速开始

```bash
npm install

# 开发态：起 Vite dev server(5173) + Electron 窗口
npm run dev
# 需要调试端口之类时，额外参数原样转给 Electron：
#   npm run dev -- --remote-debugging-port=9333

# 生产态：先构建，再起客户端（客户端内置回环静态服务器托管 dist/）
npm run build
npm start

# 打包（本轮只交付配置，未执行）
npm i -D electron-builder   # ← 打包前必需，见下
npm run pack:win            # 产出 release/CatWareHouse-0.1.0-setup.exe
npm run pack:dir            # 只出免安装目录，便于快速验证
```

**为什么 `electron-builder` 不在 `devDependencies` 里**：它依赖的 `app-builder-bin`
是约 45 MB 的 Go 辅助二进制，而本机到 registry 的吞吐实测只有约 10 KB/s（单个 tarball
耗时 200–450 秒），装它会让整个 `npm install` 从 57 秒变成数小时。配置
（`electron-builder.yml`）已经写好，打包时按上面那一行临时装上即可。

`electron` 被**钉死在 `28.3.3`**（不是 `^`）：该版本的二进制已经在本机
`%LOCALAPPDATA%/electron/Cache` 里，安装时直接命中缓存、不下载 107 MB。
缓存键的算法是 `sha256(下载 URL 去掉文件名后的目录部分)`（`@electron/get` 的
`Cache.getCacheDirectory`），`ef33c1c1…` 正好等于
`sha256("https://github.com/electron/electron/releases/download/v28.3.3")` —— 已核对。
换版本就等于换缓存键，会退化成一次大体积下载。

## 目录结构：镜像集 vs 客户端自有

| 归属 | 内容 | 规则 |
| --- | --- | --- |
| **镜像集** | `index.html`、`src/**`（48 个文件） | 与 `Cw_WebUi` **逐字节相同**，由 `mirror:apply` 维护，**禁止手工编辑** |
| **客户端自有** | `electron/`、`scripts/`、`mirror.manifest.json`、`vite.config.ts`、`tsconfig*.json`、`package.json` / `package-lock.json`、`electron-builder.yml`、`.gitignore`、`README.md`、`plan.md` | 客户端自己的代码，随便改 |

镜像清单在 `mirror.manifest.json`（49 条），由 `scripts/mirror.mjs` 校验与执行。

## 镜像工作流

改网页端之后，客户端这样跟上：

```bash
npm run mirror:check     # 逐文件比 sha256，报 SAME / DRIFTED / MISSING / NO_SOURCE / EXTRA_SOURCE / EXTRA_TARGET
npm run mirror:apply     # 源 → 目标，逐字节整份覆盖
npm run mirror:prune     # 同上，并删掉源端已不存在的镜像文件
```

`mirror:check` 在有漂移时**退出码 1**，所以它可以直接当 CI 闸门用。

它报的六种状态：

| 状态 | 含义 | 怎么办 |
| --- | --- | --- |
| `SAME` | 逐字节相同 | 无 |
| `DRIFTED` | 目标被本地改过 | `mirror:apply` 覆盖回去（**你在客户端对镜像文件的任何改动都会被冲掉**） |
| `MISSING` | 目标缺失 | `mirror:apply` |
| `NO_SOURCE` | 清单里的路径源端没有（源端删了文件） | 从清单里删掉该条。**`--prune` 处理不了它** —— 源端已经没这个文件了，prune 只删「目标端多出来的」 |
| `EXTRA_SOURCE` | 源端 `src/` 有文件没进清单（**网页端新增了页面**） | 把路径加进 `mirror.manifest.json`，再 `mirror:apply` |
| `EXTRA_TARGET` | 客户端 `src/` 有文件不在清单里 | 说明有人往镜像目录里塞了客户端专属文件；挪出去，或（确认要长期保留就）加进清单 |

> `EXTRA_SOURCE` 是这套机制里最有价值的一条：网页端**新增页面**时它会主动喊出来，
> 而不是安静地漏掉。反过来，`EXTRA_TARGET` 是对「往镜像目录里塞私有代码」的防线 ——
> 一旦破了，下次 `mirror:apply` 就会把它删掉。

### 镜像同步失败时：直接替换

因为镜像文件与源端逐字节相同，「替换」不需要任何转换：

```bash
# 1) 先看差在哪（不改盘）
npm run mirror:check

# 2) 整份覆盖。源端（Cw_WebUi）本身就是备份，客户端这边不需要额外备份
npm run mirror:apply -- --prune

# 3) 复核
npm run mirror:check    # 必须 49 SAME / exit 0
npm run type-check      # 必须**恰好** 18 个错（见下节：这是比对，不是通过）
```

`--prune` 会把目标端多出来的镜像文件删掉，所以它同时也是「把镜像目录重置成源端的样子」。
**它只动 `src/` 下的文件**（`scanRoots`），不会碰 `electron/`、`scripts/` 或任何构建配置。

### 行尾（CRLF）——「昨天全绿今天冒 DRIFTED」时先看这里

本机 `git config core.autocrlf` 是 `true`（仓库里存 LF，检出时写 CRLF），而镜像比的是
**磁盘字节**。三条实测事实：

1. **新 clone 是安全的**：git 会把 `Cw_WebUi/src` 与 `CwClient/src` **两边都**物化成 CRLF ——
   转换是对称的。实测在一个全新 clone 里跑 `mirror:check`：`49 SAME / exit 0`，
   两侧各 48/48 个文件含 CRLF。
2. **只有一侧被重新物化时会报 DRIFTED**：实测删掉 `CwClient/src/env.d.ts` 再
   `git checkout --` 它 —— git 给它写了 CRLF，而源端仍是 LF → `1 drifted / exit 1`。
   注意这是**被报出来的**，不是静默损坏。（反过来，`git checkout -- src` 对「stat 看起来干净」
   的文件会被 git 跳过、行尾不变 —— 所以这个坑不会在日常操作里随便触发。）
3. **恢复就是上面手册里那一条**：`npm run mirror:apply` → 实测 `UPDATED 1` → 回到 `49 SAME`。

所以看到漂移先怀疑行尾、先跑 `mirror:apply`，别先去改代码。

**为什么不加 `.gitattributes` 把客户端钉成 LF**：那会让第 1 种情况**变糟** ——
源端被物化成 CRLF、客户端被钉在 LF，49 条立刻全红。
真正对称的修法是根目录 `.gitattributes` 同时管住两侧，**不在本轮授权范围内**（只动 `CwClient/`）。

## `type-check` 为什么有 18 个错（而且是设计的一部分）

```
npm run type-check    # vue-tsc --build --force → 恰好 18 个错，exit 2
npm run build         # vite build → exit 0，出 dist/。**不经过** type-check
npm run build:strict  # 串上 type-check 的版本，会因那 18 个错而失败
```

那 18 个错**全是网页端既有的**，镜像逐字节继承过来。已实测：把客户端与网页端的
`vue-tsc` 输出逐行比对，**18 条完全相同** —— 同文件、同行列、同错误码、同消息、同顺序。

这带来一个必须讲清的性质：**只要客户端还是逐字节镜像，它就不可能比网页端更「类型干净」。**
想在客户端修掉这些错，就得改镜像文件，那正是镜像机制要防的事。
所以 `type-check` 在这里的用途是**比对**而不是**通过**：它的正确结果是「恰好等于网页端的那 18 条」，
多一条都说明客户端的依赖版本或 tsconfig 被我改动了，那是真问题。

`build` 因此**不串** `type-check`（串了就永远失败）。这也解释了为什么
`npm run build` 能出产物、`npm run build:strict` 不能。

## 为什么端口只能是 5173 / 5175

`CwServer/core/config.py:8` 的 CORS 白名单写死了两个源：

```python
CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5175"]
```

而渲染层对后端发的是**预检跨域请求**（`Content-Type: application/json` 触发 preflight）。
于是：

- 生产态由 `electron/static-server.cjs` 起一个只绑 `127.0.0.1` 的静态服务器托管 `dist/`，
  端口**依次尝试 5173 → 5175**，让页面的 Origin 正好落在白名单里；
- 两个端口都被占用时**弹错误框退出**，不静默换端口 —— 换成别的端口虽然窗口能开，
  但所有请求会被 CORS 拒，那比直接起不来更难排查；
- 开发态用 Vite dev server，默认就是 5173，且 `strictPort: true`（占不到就报错，
  不会悄悄挪到 5174 去）。

**另一个被排除的方案**：用 `app://` 自定义协议加载，靠 `webRequest.onHeadersReceived`
注入 CORS 响应头。它能让 `router` 保持原样，但**对预检请求无效** —— `OPTIONS` 预检不会
经过 `onHeadersReceived`，所以 POST/PUT/DELETE 照样被拒。回环服务器方案没有这个盲区。

## 为什么构建配置（`vite.config` / `tsconfig`）不镜像

它们在客户端是**同构但自有**的。原因是网页端那边有一对容易误读的文件：

`Cw_WebUi` 里 `vite.config.js` 与 `vite.config.ts` 同时存在。**那个 `.js` 不是人写的**，
它是 `vue-tsc --build` 的产物 —— `tsconfig.node.json` 从 `@tsconfig/node22` 继承来的
`composite: true` 没有配 `noEmit`，于是 `include: ["vite.config.*"]` 把 `vite.config.ts`
编译成了紧挨着的 `vite.config.js`。而 Vite 的配置解析顺序是 **`.js` 先于 `.ts`**，
所以网页端实际生效的是那份**编译产物**。（旁证：`Cw_WebUi/.gitignore` 里单独写了一行
`vite.config.js` —— 正因为它是产物而不是源码。实测：在客户端删掉该文件再跑一次
`vue-tsc --build`，它会重新出现。）

这对客户端有两个后果：

1. 镜像 `vite.config.ts` 会让客户端复制出同样的「源码 + 产物」二元结构，而产物在
   `.gitignore` 里、**镜像机制管不到它** —— 于是镜像集里会出现一个不被 `mirror:check`
   覆盖、却真实生效的文件。**真正生效的东西必须是被检查的东西**，否则这个镜像就是假的安全感；
2. 更麻烦的是客户端**自己也会**生成同名 `.js` 去遮蔽自己的 `.ts` —— 改完 `vite.config.ts`
   直接 `npm run dev`（这条路径不经过 type-check）就会用上过期的 `.js`。

所以客户端在 `tsconfig.node.json` 里显式加了 `"noEmit": true`（TS 5.8 允许在 `composite`
下 noEmit，已实测：加了之后 `vite.config.js` 不再生成），从根上取消这个文件，
只保留一份自己的 `vite.config.ts`。**这也是 `tsconfig` 与网页端唯一的差异。**

## 渲染层做了什么适配

**没有。** 镜像集里没有一个字节是客户端专属的。所有 Electron 相关的处理都在
`electron/` 与 `scripts/` 这两个客户端自有目录里：

| 网页端用法 | 在 Electron 里为什么不用改 |
| --- | --- |
| `localStorage`（服务器地址、主题） | 渲染进程有完整的 localStorage，照常持久化 |
| `window.matchMedia('(prefers-color-scheme: dark)')` | Chromium 支持，跟随系统深色 |
| `Ctrl+N` / `Ctrl+F` / `Esc` 全局快捷键 | 渲染进程的 keydown 监听照常工作 |
| 导出数据用 `URL.createObjectURL` + `a.download` | Electron 默认弹「另存为」对话框，功能天然可用 |
| 开场动画（gsap + `document.querySelectorAll`） | 标准 DOM，无需改 |

唯一一个**必须**在客户端侧解决的是加载方式：`src/router/index.ts` 用的是
`createWebHistory`，在 `file://` 下 `history.pushState` 会因 origin 为 `null` 抛 SecurityError。
回环静态服务器（见上）绕开了它，代价是那个端口约束。

## 已知边界

- **未执行 `electron-builder` 打包**：配置（`electron-builder.yml`）与命令已就绪，但没有产出安装包
  （原因见「快速开始」里关于 `app-builder-bin` 的说明）。
- **未授权改动后端**：CORS 白名单没动，所以客户端被硬绑定在 5173/5175 上。想让客户端用任意端口，
  需要把 `app://` 或 `http://localhost:*` 加进 `CwServer/core/config.py` 的白名单。
- **未做端到端后端联调**：冒烟时本机后端（`:11222`）没有运行，所以「客户端 → 后端」这条数据链路
  没有被真正跑过。已验证到的是它的**前提**：窗口从一个 Origin 恰好落在白名单里的
  `http://localhost:5173` 加载（这条断言直接从 `CwServer/core/config.py` 读白名单来比对，
  不是写死副本）。要真跑通，起后端后再 `npm start` 即可。
- **18 个既有类型错误随镜像继承**（见上一节），不是本客户端引入的，也不打算在客户端修。
- **无 UI 截图级回归**：开场动画（gsap）与 naive-ui 过渡会让截图对比不稳定 ——
  「一个会抖的闸门比没有闸门更糟」。验收以可判定的事实为准：
  `mirror:check`、`vite build`、真实起窗 + CDP 读页面状态。

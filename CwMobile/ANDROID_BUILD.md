# CatWarehouse 移动端 — 安卓打包 / 真机运行

`CwMobile/` 是 CatWarehouse 的移动端（Vue 3 + Vant 4 + Capacitor 7）。工程已接好
Capacitor，并已生成 `android/` 原生工程与最新 web 资源。下面说明如何预览与打出 APK。

> 说明：APK 打包需 **JDK 21**（Capacitor 7 的 `capacitor-android` 以 Java 21 编译；
> 用 JDK 17 会报 `无效的源发行版: 21`）+ Android SDK（Platform 35）。H5 预览无需任何 SDK。

---

## 1. 后端地址说明（重要）

网页/移动端默认服务器地址是 `http://localhost:11222`（可在 App「设置 → 服务器配置」修改，
持久化在 localStorage）。

| 场景 | 服务器地址应填 |
| --- | --- |
| 电脑浏览器预览 / 模拟器同机运行 | 保持默认 `localhost` |
| **安卓真机**（手机与电脑同一局域网） | 电脑的局域网 IP，如 `192.168.1.100`（端口不变 11222） |

- 手机连的是 WiFi 而非电脑热点时，需确保 CwServer 所在电脑防火墙放行该端口。
- 后端是明文 HTTP。安卓 WebView 从 `https://localhost` 加载页面，默认会拦截明文 HTTP 请求，
  因此已在
  `android/app/src/main/AndroidManifest.xml` 的 `<application>` 上开启
  `android:usesCleartextTraffic="true"`（仅个人局域网工具场景；若日后后端上 HTTPS 可移除）。

---

## 2. 一键真机打包（Android APK）

前置：Node ≥ 20、npm，已 `npm install`。打包机需 **JDK 21** + Android SDK（`local.properties` 写好 `sdk.dir`，或用 `ANDROID_HOME` 指向 SDK）。

```bash
# ① 构建 web 产物（内部先跑 vue-tsc 类型检查，再 vite build）
npm run build

# ② 把 web 产物与配置同步进 android 原生工程（首次会自动执行 cap add android）
npm run cap:sync          # 等价 npm run build && npx cap sync android

# ③ 编译 Debug APK（需 JDK 21 / Android SDK；在项目根即可，gradlew 在 android/ 内）
cd android
./gradlew assembleDebug    # Windows 用 gradlew.bat assembleDebug
cd ..
```

产物路径：`android/app/build/outputs/apk/debug/app-debug.apk`，传到手机安装即可。
（手机会提示“未知来源”，允许安装即可；这是自签名 Debug 包。）

### Android Studio 方式（可视化，推荐首次）
1. Android Studio → `Open` 选择本目录下的 `CwMobile/android/`，等待 Gradle 同步。
2. 若提示缺 SDK，在 `android/local.properties` 写一行
   `sdk.dir=C\:\\Users\\<你的用户名>\\AppData\\Local\\Android\\Sdk`（按实际路径）。
3. 工具栏 `Run ▶` 选一台真机 / 模拟器即可安装运行（模拟器服务器地址填 `10.0.2.2` 可访问宿主机）。

---

## 3. 无需打包的快速预览（浏览器 / 手机浏览器）

```bash
npm install
npm run dev          # Vite dev server，默认打印局域网地址（如 http://192.168.31.194:5173）
```

- 本机浏览器直接打开打印出的地址。
- 手机浏览器打开 `http://<电脑局域网IP>:5173`，进「设置 → 服务器配置」把地址改成后端 IP 即可使用。
  （此路径走浏览器，无打包产物；数据功能与 APK 内一致。）

---

## 4. 其它命令

```bash
npm run type-check   # 仅 vue-tsc 类型检查
npm run cap:add:android  # 已执行过；重建 android 平台用（谨慎，会覆盖 android/ 内改动）
npx cap open android # 已装 Android Studio 时直接打开原生工程
```

---

## 5. 常见问题

- **`assembleDebug` 报 “SDK location not found”**：新建 `android/local.properties` 写入
  `sdk.dir=<Android SDK 绝对路径>`（Windows 反斜杠需转义，见上）。
- **App 里所有请求报错 / 连不上后端**：确认「设置 → 服务器配置」的地址是本机可访问的后端；
  真机务必填局域网 IP 而非 `localhost`。
- **首次安装 Android Studio 的机器**：SDK Manager 里装 `Platform 35` 与 `Build-Tools`（同步时会自动提示）。
- **构建日志有 “chunk larger than 500 kB” 警告**：仅为体积提示，不影响运行，可忽略。

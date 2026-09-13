const config = {
    appId: 'com.catwarehouse.mobile',
    appName: 'CatWarehouse',
    webDir: 'dist',
    android: {
        // WebView 从 https://localhost 页面请求 http://局域网后端属于混合内容，
        // 默认会被拦截(与 usesCleartextTraffic 无关)，必须显式放行。
        allowMixedContent: true,
    },
    server: {
        androidScheme: 'https',
    },
    plugins: {
        // WebView 跨域请求后端会触发 CORS 预检，而后端白名单不含 App 的
        // origin(https://localhost)。启用 CapacitorHttp 后 fetch/XHR 走 native
        // OkHttp，绕过浏览器 CORS 与预检，纯移动端解决，无需改后端。
        CapacitorHttp: {
            enabled: true,
        },
    },
};
export default config;

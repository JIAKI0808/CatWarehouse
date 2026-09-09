import { showToast, showFailToast } from 'vant'

/**
 * 移动端轻提示适配：网页端 store 原从 naive-ui 引入 useMessage()，
 * 移动端统一替换为 Vant 版，保持调用签名一致（useMessage().error(...)）。
 */
export interface MessageApi {
  error(content: string): void
  success(content: string): void
  warning(content: string): void
}

export function useMessage(): MessageApi {
  function error(content: string) {
    showFailToast(content)
  }
  function success(content: string) {
    showToast(content)
  }
  function warning(content: string) {
    showToast(content)
  }
  return { error, success, warning }
}

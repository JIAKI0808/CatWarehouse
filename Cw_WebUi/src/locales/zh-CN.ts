/**
 * 简体中文语言包（默认语言）。
 *
 * ## 两个分区，两种来源
 *
 * - `app.*` —— **界面文案**，由本文件（也就是前端）拥有。
 *   必须在后端尚未应答时就能渲染：离线 / 连不上服务端是本应用的**正常状态**
 *   （设置页专门有「测试连接」就是这个原因）。做成远程依赖等于给首屏加一个失败点。
 * - `backend.*` —— **后端自己产生的文案**的对照表，键就是后端返回的 `detail` 原文。
 *   后端目录在 `CwServer/locales/zh-CN.json`，**两边必须保持一致**。
 *   用 `translateBackendMessage()` 查询，查不到就原样显示，绝不显示空串。
 *
 * ## 为什么导出 `MessageSchema`
 *
 * `MessageSchema` 由本文件推导，`en-US.ts` 用它约束自己 ——
 * **漏翻一个键会在 `vue-tsc` 阶段直接报错**，而不是等到界面上显示出一串 key。
 */

const zhCN = {
  app: {
    nav: {
      inventory: '库存',
      analytics: '数据分析',
      ledger: '账本',
      pricing: '售价管理',
      settings: '设置',
    },
  },
  backend: {
    'Category not found': '分类不存在',
    'SubCategory not found': '子分类不存在',
    'Item not found': '物品不存在',
    'Tag not found': '标签不存在',
    'Notification not found': '通知不存在',
    'Budget not found': '预算不存在',
    'Ledger item not found': '账目不存在',
    'Recurring bill not found': '定时账单不存在',
    'Pricing not found': '售价记录不存在',
    'Pricing category not found': '售价分类不存在',
    'Pricing sub-category not found': '售价子分类不存在',
    'empty file': '上传的文件为空',
    '科学的管理每一颗螺丝钉': '科学的管理每一颗螺丝钉',
  },
}

export type MessageSchema = typeof zhCN
export default zhCN

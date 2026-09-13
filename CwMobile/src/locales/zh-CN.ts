/**
 * 简体中文语言包（移动端，默认语言）。
 *
 * ## 与网页端的关系：**刻意各存一份**
 *
 * `CwMobile` 不是网页端的镜像（镜像只覆盖 `Cw_WebUi → CwClient`），它有自己的构建与发布节奏。
 * 两端文案**大部分相同、但并不完全一致**（列表 Tab 就叫「数据」「售价」，网页端叫
 * 「数据分析」「售价管理」），硬共享一份反而要开一堆「移动端特例」的开关。
 * 因此这里独立一份。代价是公共文案要改两处 —— 与 `ocr/` 和 `voice/` 各自留一份
 * `UpstreamRejectedError` 是同一个取舍：**用少量重复换两端互不牵制**。
 *
 * ## 两个分区
 *
 * - `app.*` —— **界面文案**，由本文件（移动端）拥有。必须在后端尚未应答时就能渲染。
 * - `backend.*` —— **后端自己产生的文案**的对照表，键就是后端返回的 `detail` 原文。
 *   后端目录在 `CwServer/locales/zh-CN.json`，**两边必须保持一致**。
 *   用 `translateBackendMessage()` 查询，查不到原样显示，绝不显示空串。
 *
 * ## 为什么导出 `MessageSchema`
 *
 * `en-US.ts` 用它约束自己 —— **漏翻一个键会在 `vue-tsc` 阶段直接报错**。
 */

const zhCN = {
  app: {
    nav: {
      inventory: '库存',
      analytics: '数据',
      ledger: '账本',
      pricing: '售价',
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

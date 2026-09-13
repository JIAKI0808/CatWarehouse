/**
 * 计量单位字典。
 *
 * ## 它解决的是什么
 *
 * `SubCategory.unit` 是自由文本，而新建表单把默认值写死成 `'个'`（本仓库共 12 处）。
 * 两件坏事：**自由文本没约束**（「斤」「市斤」「500g」混在同一列），
 * 以及**默认值是语言相关的**（见 `plan.md` §C12 —— 跟着界面语言翻译会让同一张表里中英混杂）。
 *
 * 这个 store 把默认值改成「**字典的第一项**」：默认值仍然存在，
 * 但它来自后端而不是散落在 12 个文件里。
 *
 * ## 为什么是「选或自由输入」而不是枚举
 *
 * 把 `unit` 改成枚举代码需要一次**数据迁移**（现有行的 `'个'` 要变成 `'piece'`），
 * 而 `unit` 还会被 OCR / 语音两条写入路径碰到 —— 那是项目级的决定，不在本环内。
 * 所以字典只作**建议**：表单用 `NSelect` 的 `filterable + tag`，
 * 用户既能从字典挑，也能输入字典里没有的单位。
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { unitApi } from '@/services/api'

/**
 * 离线兜底值 —— **与接入字典之前的行为逐字相同**。
 * 服务器不可达时表单默认值仍是 `个`，界面不产生任何可见变化。
 */
export const FALLBACK_UNIT = '个'

export const useUnitStore = defineStore('units', () => {
  const units = ref<string[]>([])

  /** 表单默认单位。字典拿到之前 / 拿不到时，退回接入前的那个写死值。 */
  const defaultUnit = computed(() => units.value[0] ?? FALLBACK_UNIT)

  async function fetchUnits() {
    try {
      const list = await unitApi.getAll()
      if (Array.isArray(list) && list.length) units.value = list
    } catch {
      // 保持空数组 ⇒ defaultUnit 走离兜底，与接入前一致
    }
  }

  return { units, defaultUnit, fetchUnits }
})

/**
 * 计量单位字典（移动端）。
 *
 * 与 `Cw_WebUi/src/stores/units.ts` **同构的一份** —— 移动端不参与镜像，
 * 是独立构建的应用，各自留一份（与两端语言包、currency store 同一取舍）。
 *
 * ## 它解决的是什么
 *
 * `SubCategory.unit` 是自由文本，新建表单把默认值写死成 `'个'`（本仓库共 12 处）。
 * **自由文本没约束**（「斤」「市斤」「500g」混在同一列），且**默认值是语言相关的**
 * （见 `plan.md` §C12）。这里把默认值改成「**字典的第一项**」——
 * 默认值仍然存在，但它来自后端而不是散落在各文件里。
 *
 * ## 为什么是「选或自由输入」而不是枚举
 *
 * 改成枚举代码需要一次**数据迁移**，而 `unit` 还会被 OCR / 语音两条写入路径碰到 ——
 * 项目级的决定，不在本环内。所以字典只作**建议**。
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { unitApi } from '@/services/api'

/** 离线兜底值 —— **与接入字典之前的行为逐字相同**。 */
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
      // 保持空数组 ⇒ defaultUnit 走离线兜底，与接入前一致
    }
  }

  return { units, defaultUnit, fetchUnits }
})

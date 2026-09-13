/**
 * store 行为骨架 —— 结构型（装饰器 / 适配器）+ 行为型（模板方法 / 策略）。
 *
 * 这三个函数是各 store 里反复出现的那套骨架的**唯一实现**：
 *
 *   loading = true → try 调 api → catch(useMessage().error(e.message || '文案')) → finally loading = false
 *
 * 以及「增 / 改 / 删成功后如何改列表」的固定次序。它们只依赖
 * `@/composables/useMessage`（既有的 Vant 适配器）和下面这个最小接口，
 * 不认识任何具体资源 —— 于是 store 与「失败怎么提示」「新项插在哪」这些策略解耦。
 *
 * 注意：这里导入的是 `@/composables/useMessage`（Vant 版），不是 naive-ui。
 */

import type { Ref } from 'vue'
import { useMessage } from '@/composables/useMessage'
import type { WriteApi } from '@/services/api'

// `WriteApi` 只此一处定义（`services/api.ts` 是它的产出者），这里用 `import type`
// 引入：类型导入在编译期被完全抹掉，所以既不产生运行时依赖，也不会把 `vant`
// 带进 `services/api.ts`（那里刻意保持不依赖任何 UI 库）。

/**
 * 结构型·装饰器：给任意 async 动作叠加「失败提示 + 吞掉异常」。
 *
 * 失败时返回 `undefined` —— 与既有实现完全一致（原来的 `catch` 里不写 return，
 * 函数自然返回 `undefined`）。不要改成 `throw`，调用方没有一处准备接异常。
 */
export function withMessage<T, A extends unknown[]>(
  message: string,
  action: (...args: A) => Promise<T>
): (...args: A) => Promise<T | undefined> {
  return async (...args: A) => {
    try {
      return await action(...args)
    } catch (e: any) {
      useMessage().error(e.message || message)
      return undefined
    }
  }
}

/**
 * 结构型·适配器 + 行为型·模板方法：把「取一个列表」的动作适配成 store 真正
 * 需要的那对东西 —— 列表 ref 与 loading 生命周期。
 *
 * 失败时**保持原列表不变**（既有的 `catch` 不赋值），且 `loading` 必定回落
 * （走 `finally`，即使 `run` 抛出的不是 Error 也一样）。
 */
export function fetchInto<T, A extends unknown[]>(spec: {
  list: Ref<T[]>
  loading: Ref<boolean>
  message: string
  run: (...args: A) => Promise<T[]>
}): (...args: A) => Promise<void> {
  return async (...args: A) => {
    spec.loading.value = true
    try {
      spec.list.value = await spec.run(...args)
    } catch (e: any) {
      useMessage().error(e.message || spec.message)
    } finally {
      spec.loading.value = false
    }
  }
}

/**
 * 创建型·工厂 + 行为型·模板方法：由「列表 ref + api + 文案」生产 create/update/remove。
 *
 * 差异点被显式化成参数（策略），而不是复制整段实现：
 * - `insert`：新项进末尾（`push`）还是开头（`unshift`）。默认 `push`；
 *   全仓库只有账单用 `unshift`（按时间倒序）。
 * - `onRemoved`：删除成功后是否顺带清理别的状态。分类与子分类要清 `selectedId`。
 *
 * 返回值语义与既有实现逐字一致：成功返回实体，失败返回 `undefined`；
 * `update` 只在该 id 确实存在时就地替换，找不到**什么都不做**（既有的 `-1` 守卫）。
 */
export function writeActions<T extends { id: number }, C, U>(spec: {
  list: Ref<T[]>
  api: WriteApi<T, C, U>
  messages: { create: string; update: string; remove: string }
  insert?: 'push' | 'unshift'
  onRemoved?: (id: number) => void
}) {
  const insertAt: 'push' | 'unshift' = spec.insert === 'unshift' ? 'unshift' : 'push'

  const create = withMessage(spec.messages.create, async (data: C) => {
    const item = await spec.api.create(data)
    spec.list.value[insertAt](item)
    return item
  })

  const update = withMessage(spec.messages.update, async (id: number, data: U) => {
    const item = await spec.api.update(id, data)
    const index = spec.list.value.findIndex((x) => x.id === id)
    if (index !== -1) spec.list.value[index] = item
    return item
  })

  const remove = withMessage(spec.messages.remove, async (id: number) => {
    await spec.api.delete(id)
    spec.list.value = spec.list.value.filter((x) => x.id !== id)
    // 先改列表、再清关联状态 —— 与既有实现的次序一致。
    spec.onRemoved?.(id)
  })

  return { create, update, remove }
}

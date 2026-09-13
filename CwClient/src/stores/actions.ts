/**
 * store 动作的三个零件。
 *
 * 改造前每个 store 都把 `try / catch / useMessage().error(e.message || '文案')` 抄了
 * 一遍：11 个 store 共 **58 处**，其中「取列表」「新建」「更新」「删除」四个骨架
 * 在 7 个 store 里逐字同构。这里给的是**骨架**，不是「通用 store 工厂」——
 * 每个 store 的返回面、额外状态、自定义动作都留在自己文件里，
 * 因为那些恰恰是它们彼此不同的地方。
 *
 * 三个零件各自有真实使用者，没有一个是「先建好等人用」：
 *   - `withMessage`   23 处（写操作骨架内部 21 + tag 的两个条目标签操作）
 *   - `fetchInto`      9 处（7 个 store 的列表 + notification + alert）
 *   - `writeActions`   7 处
 */

import { useMessage } from 'naive-ui'
import type { Ref } from 'vue'
import { translate } from '@/i18n'
import type { WriteApi } from '@/services/api'

/**
 * 三个零件现在收的是**语言包的 key**，不是写死的中文。
 *
 * 为什么是 key 而不是「直接传 `translate(key)` 的结果」：
 * store 是单例，配置对象在**首次创建 store 时**求值一次。若那时就把中文取成常量，
 * 用户切语言后这些兜底文案会停留在旧语言、直到刷新页面。
 * 传 key、在**出错那一刻**才查表，就没有这个问题。
 */

/**
 * 结构型：装饰器 —— 把「出错就提示」包在动作外面，不改动作本身。
 *
 * 失败时返回 `undefined`，与原实现里 catch 分支隐式返回 undefined 完全一致。
 * 注意**不覆盖**那些失败时有自己兜底值的动作（`tag.getItemTags` 返回 `[]`、
 * `recurring.generate` 返回 `0`）—— 它们的兜底值不同，混进来就会改变行为。
 */
export function withMessage<T, A extends unknown[]>(
  messageKey: string,
  action: (...args: A) => Promise<T>
): (...args: A) => Promise<T | undefined> {
  return async (...args: A) => {
    try {
      return await action(...args)
    } catch (e: any) {
      useMessage().error(e.message || translate(messageKey))
      return undefined
    }
  }
}

/**
 * 行为型：模板方法 —— 「置 loading → 取数 → 赋值 → 出错提示 → 复位 loading」五步固定。
 *
 * 返回的函数与传入的 `run` **参数表一致**（`A` 由 `run` 推出来），所以
 * `fetchAll()`、`fetchAll(month?)`、`fetchBySubCategory(id)` 都能用同一个骨架，
 * 且各自的签名逐字不变。
 *
 * 动作名不在这里定 —— 各 store 叫 `fetchAll` / `fetchBySubCategory` / `fetchByCategory`，
 * 由调用方赋值时命名，因为那也是它对外接口的一部分。
 */
export function fetchInto<T, A extends unknown[]>(spec: {
  list: Ref<T[]>
  loading: Ref<boolean>
  messageKey: string
  run: (...args: A) => Promise<T[]>
}): (...args: A) => Promise<void> {
  return async (...args: A) => {
    spec.loading.value = true
    try {
      spec.list.value = await spec.run(...args)
    } catch (e: any) {
      useMessage().error(e.message || translate(spec.messageKey))
    } finally {
      spec.loading.value = false
    }
  }
}

/**
 * 行为型：模板方法 —— `create` / `update` / `remove` 三个写动作的骨架。
 *
 * 两处差异用**策略**注入，而不是抹平（抹平就是行为变化）：
 *   - `insert`：新建的条目插到列表**头**还是**尾**。既有实现里只有 `ledger` 用 `unshift`，
 *     其余 6 个 store 一律 `push`。
 *   - `onRemoved`：删除之后的额外清理。只有 `category` 会顺手清掉 `selectedId`。
 */
export function writeActions<T extends { id: number }, C, U>(spec: {
  list: Ref<T[]>
  api: WriteApi<T, C, U>
  messageKeys: { create: string; update: string; remove: string }
  insert?: 'push' | 'unshift'
  onRemoved?: (id: number) => void
}) {
  const insertAt = spec.insert === 'unshift' ? 'unshift' : 'push'

  const create = withMessage(spec.messageKeys.create, async (data: C) => {
    const item = await spec.api.create(data)
    spec.list.value[insertAt](item)
    return item
  })

  const update = withMessage(spec.messageKeys.update, async (id: number, data: U) => {
    const item = await spec.api.update(id, data)
    const index = spec.list.value.findIndex((x) => x.id === id)
    if (index !== -1) spec.list.value[index] = item
    return item
  })

  const remove = withMessage(spec.messageKeys.remove, async (id: number) => {
    await spec.api.delete(id)
    spec.list.value = spec.list.value.filter((x) => x.id !== id)
    spec.onRemoved?.(id)
  })

  return { create, update, remove }
}

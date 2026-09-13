/**
 * English (US) message pack (mobile).
 *
 * Annotated with `MessageSchema` so TypeScript rejects this file if it is missing any
 * key that `zh-CN.ts` defines — a forgotten translation becomes a compile error rather
 * than a raw key rendered in the UI.
 *
 * `backend.*` keys are the **verbatim strings the server puts in `detail`** — do not
 * "tidy" them. Source of truth: `CwServer/locales/en-US.json`.
 */
import type { MessageSchema } from './zh-CN'

const enUS: MessageSchema = {
  app: {
    nav: {
      inventory: 'Stock',
      analytics: 'Charts',
      ledger: 'Ledger',
      pricing: 'Pricing',
      settings: 'Settings',
    },
  },
  backend: {
    'Category not found': 'Category not found',
    'SubCategory not found': 'Sub-category not found',
    'Item not found': 'Item not found',
    'Tag not found': 'Tag not found',
    'Notification not found': 'Notification not found',
    'Budget not found': 'Budget not found',
    'Ledger item not found': 'Ledger entry not found',
    'Recurring bill not found': 'Recurring bill not found',
    'Pricing not found': 'Pricing record not found',
    'Pricing category not found': 'Pricing category not found',
    'Pricing sub-category not found': 'Pricing sub-category not found',
    'empty file': 'The uploaded file is empty',
    '科学的管理每一颗螺丝钉': 'Keep every last screw in order',
  },
}

export default enUS

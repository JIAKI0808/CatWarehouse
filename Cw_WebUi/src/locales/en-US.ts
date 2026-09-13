/**
 * English (US) message pack.
 *
 * Annotated with `MessageSchema` on purpose: TypeScript then rejects this file if it
 * is missing any key that `zh-CN.ts` defines. A forgotten translation becomes a
 * compile error instead of a raw key rendered in the UI.
 *
 * `backend.*` keys are the **verbatim strings the server puts in `detail`** — do not
 * "tidy" them (e.g. `SubCategory not found` has no hyphen). They are matched exactly
 * against the response, and the source of truth is `CwServer/locales/en-US.json`.
 */
import type { MessageSchema } from './zh-CN'

const enUS: MessageSchema = {
  app: {
    nav: {
      inventory: 'Inventory',
      analytics: 'Analytics',
      ledger: 'Ledger',
      pricing: 'Pricing',
      settings: 'Settings',
    },
    settingsPage: {
      language: 'Language',
      languageNote: 'Applies immediately; kept on this device when the server is unreachable',
      languageSyncFailed: 'Switched on this device, but could not sync to the server',
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

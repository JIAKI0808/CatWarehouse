<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { NIcon, NBadge, NPopover, NList, NListItem, NButton, NTag } from 'naive-ui'
import { WalletOutline, NotificationsOutline, SunnyOutline, MoonOutline } from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'
import { useNotificationStore } from '@/stores/notification'
import { useAlertStore } from '@/stores/alert'

const { t } = useI18n()

const props = defineProps<{ isDark: boolean }>()
const emit = defineEmits<{ (e: 'toggle-theme'): void }>()

const notificationStore = useNotificationStore()
const alertStore = useAlertStore()

const totalCount = computed(() => notificationStore.unreadCount + alertStore.alertCount)

onMounted(() => {
  notificationStore.fetchAll()
  notificationStore.check()
  alertStore.fetchAlerts()
})
</script>

<template>
  <div class="h-8 bg-blue-500 border-b flex items-center justify-between px-4 select-none">
    <div class="flex items-center gap-1">
      <NIcon :size="16" class="text-white mr-1">
        <WalletOutline />
      </NIcon>
      <span class="text-xs font-medium text-white">CatWareHouse</span>
    </div>
    <div class="flex items-center gap-2">
      <NButton quaternary size="tiny" class="text-white" @click="emit('toggle-theme')">
        <template #icon>
          <NIcon :size="16" class="text-white">
            <MoonOutline v-if="!props.isDark" />
            <SunnyOutline v-else />
          </NIcon>
        </template>
      </NButton>
      <NPopover trigger="click" placement="bottom-end">
        <template #trigger>
          <NBadge :value="totalCount" :max="99">
            <NButton quaternary size="tiny" class="text-white">
              <template #icon><NIcon :size="16" class="text-white"><NotificationsOutline /></NIcon></template>
            </NButton>
          </NBadge>
        </template>
        <div style="width: 300px; max-height: 400px; overflow-y: auto">
          <div v-if="alertStore.alerts.length" class="mb-2">
            <div class="text-xs font-semibold text-gray-500 mb-1">
              {{ t('app.notify.stockAlerts') }}
            </div>
            <NList bordered>
              <NListItem v-for="a in alertStore.alerts" :key="a.id">
                <div class="flex items-center gap-2">
                  <NTag type="warning" size="small">{{ t('app.notify.lowStock') }}</NTag>
                  <span class="text-sm flex-1">{{ a.message }}</span>
                </div>
              </NListItem>
            </NList>
          </div>
          <div v-if="notificationStore.items.length">
            <div class="text-xs font-semibold text-gray-500 mb-1">
              {{ t('app.notify.systemNotifications') }}
            </div>
            <NList bordered>
              <NListItem v-for="n in notificationStore.items" :key="n.id">
                <div class="flex items-start gap-2">
                  <div class="flex-1">
                    <div class="text-sm" :class="n.is_read ? 'text-gray-400' : ''">{{ n.message }}</div>
                    <div class="text-xs text-gray-400 mt-1">{{ new Date(n.created_at).toLocaleString() }}</div>
                  </div>
                  <NButton v-if="!n.is_read" size="tiny" quaternary @click="notificationStore.markRead(n.id)">
                    {{ t('app.notify.markRead') }}
                  </NButton>
                </div>
              </NListItem>
            </NList>
          </div>
          <div
            v-if="!alertStore.alerts.length && !notificationStore.items.length"
            class="text-center text-gray-400 py-4"
          >
            {{ t('app.notify.empty') }}
          </div>
        </div>
      </NPopover>
    </div>
  </div>
</template>

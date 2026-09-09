<script setup lang="ts">
import { watch } from 'vue'
import { useAlertStore } from '@/stores/alert'
import { useNotificationStore } from '@/stores/notification'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: 'update:visible', value: boolean): void }>()

const alertStore = useAlertStore()
const notificationStore = useNotificationStore()

watch(
  () => props.visible,
  (val) => {
    if (val) refresh()
  }
)

function refresh() {
  alertStore.fetchAlerts()
  notificationStore.check()
  notificationStore.fetchAll()
}

function markRead(id: number) {
  notificationStore.markRead(id)
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <van-popup
    :show="visible"
    position="bottom"
    round
    :style="{ maxHeight: '72%' }"
    @update:show="emit('update:visible', $event)"
  >
    <div class="notify">
      <div class="notify-title">消息中心</div>
      <div class="notify-body">
        <div v-if="alertStore.alerts.length" class="section">
          <div class="section-label">库存预警</div>
          <div v-for="a in alertStore.alerts" :key="a.id" class="alert-row">
            <van-tag type="warning">低库存</van-tag>
            <span class="alert-msg">{{ a.message }}</span>
          </div>
        </div>

        <div v-if="notificationStore.items.length" class="section">
          <div class="section-label">系统通知</div>
          <div
            v-for="n in notificationStore.items"
            :key="n.id"
            class="note-row"
            :class="{ read: n.is_read }"
          >
            <div class="note-main">
              <div class="note-msg">{{ n.message }}</div>
              <div class="note-time">{{ formatTime(n.created_at) }}</div>
            </div>
            <van-button
              v-if="!n.is_read"
              size="mini"
              plain
              type="primary"
              @click="markRead(n.id)"
            >
              已读
            </van-button>
          </div>
        </div>

        <van-empty
          v-if="!alertStore.alerts.length && !notificationStore.items.length"
          description="暂无通知"
        />
      </div>
    </div>
  </van-popup>
</template>

<style scoped>
.notify {
  display: flex;
  flex-direction: column;
  max-height: 68vh;
}

.notify-title {
  padding: 16px;
  text-align: center;
  font-weight: 600;
}

.notify-body {
  overflow-y: auto;
  padding: 0 16px 24px;
}

.section-label {
  color: #969799;
  font-size: 13px;
  margin: 8px 0;
}

.alert-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
}

.alert-msg {
  flex: 1;
  font-size: 14px;
}

.note-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 0;
  border-bottom: 1px solid #f2f3f5;
}

.note-main {
  flex: 1;
  min-width: 0;
}

.note-msg {
  font-size: 14px;
}

.note-row.read .note-msg {
  color: #969799;
}

.note-time {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}
</style>

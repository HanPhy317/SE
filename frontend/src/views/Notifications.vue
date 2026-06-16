<template>
  <div>
    <NavTabs />

    <div class="page-header">
      <div>
        <h2>消息通知</h2>
        <p class="notification-subtitle">{{ unreadCount }} 条未读</p>
      </div>
      <div class="notification-actions">
        <button class="btn btn-ghost btn-sm" @click="markAll" :disabled="notifications.length === 0">全部已读</button>
        <button class="btn btn-danger btn-sm" @click="clearAll" :disabled="notifications.length === 0">清空</button>
      </div>
    </div>

    <div v-if="notifications.length === 0" class="empty-state">
      <span class="icon">🔔</span>
      <p>暂无通知</p>
    </div>

    <div
      v-for="item in notifications"
      :key="item.id"
      class="notification-card"
      :class="{ unread: !item.read }"
    >
      <div class="notification-main">
        <div class="notification-title">
          <span class="notification-dot" v-if="!item.read"></span>
          <span>{{ eventLabel(item.type) }}</span>
        </div>
        <p class="notification-message">{{ item.message }}</p>
        <div class="notification-meta">
          <span v-if="item.order_no">订单 {{ item.order_no }}</span>
          <span>{{ fmtDate(item.received_at) }}</span>
        </div>
      </div>
      <div class="notification-card-actions">
        <router-link
          v-if="item.order_id"
          class="btn btn-outline btn-sm"
          :to="'/orders/' + item.order_id"
          @click="markOne(item.id)"
        >
          查看订单
        </router-link>
        <button v-if="!item.read" class="btn btn-ghost btn-sm" @click="markOne(item.id)">已读</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import NavTabs from '../components/NavTabs.vue'
import {
  clearNotifications,
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '../services/notifications'

const notifications = ref([])
const unreadCount = computed(() => notifications.value.filter((item) => !item.read).length)

function loadNotifications() {
  notifications.value = getNotifications()
}

function markOne(id) {
  markNotificationRead(id)
  loadNotifications()
}

function markAll() {
  markAllNotificationsRead()
  loadNotifications()
}

function clearAll() {
  if (!confirm('确认清空所有通知？')) return
  clearNotifications()
  loadNotifications()
}

function eventLabel(type) {
  return {
    order_created: '新订单',
    order_accepted: '订单已接单',
    order_status_changed: '状态更新',
    order_cancelled: '订单已取消',
    order_completed: '订单已完成',
  }[type] || '订单通知'
}

function fmtDate(d) {
  return d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'
}

onMounted(() => {
  loadNotifications()
  window.addEventListener('notification-store-updated', loadNotifications)
})
onUnmounted(() => window.removeEventListener('notification-store-updated', loadNotifications))
</script>

<template>
  <div>
    <NavTabs />

    <!-- Rider Stats -->
    <div class="rider-stats" v-if="userStore.userInfo?.rider">
      <div class="stat-card"><span class="v">{{ completed }}</span><span class="l">已完成</span></div>
      <div class="stat-card"><span class="v">{{ userStore.userInfo?.rider?.service_area || '-' }}</span><span class="l">服务区域</span></div>
      <div class="stat-card"><span class="v">{{ avgRating }}</span><span class="l">平均评分</span></div>
      <div class="stat-card"><span class="v">{{ praiseRate }}</span><span class="l">好评率</span></div>
    </div>

    <!-- Available orders -->
    <div class="section-header"><h3>🔥 可接订单</h3><span class="count-badge">{{ pendingOrders.length }}</span></div>
    <div v-if="pendingOrders.length === 0" class="empty-state"><span class="icon">📭</span><p>暂无订单</p></div>
    <div class="order-card pulse" v-for="o in pendingOrders" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-type">{{ typeLabel(o.order_type) }}</span>
        <span class="badge badge-pending">待接单</span>
      </div>
      <div class="order-card-body">
        <p>📍 {{ o.delivery_addr }}</p>
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
        <p>🕒 {{ fmtDate(o.created_at) }}</p>
        <div class="order-biz-info" v-if="o.biz_fields && Object.keys(o.biz_fields).length">
          <template v-if="o.order_type === 'takeout'">🍱 {{ o.biz_fields.item_desc || '' }} | 取餐: {{ o.biz_fields.pickup_addr || '' }}</template>
          <template v-else-if="o.order_type === 'express'">📦 {{ o.biz_fields.company || '' }} | 单号: {{ o.biz_fields.tracking_no || '' }}</template>
          <template v-else-if="o.order_type === 'shopping'">🛒 {{ o.biz_fields.store_name || '' }} | {{ o.biz_fields.item_name || '' }}</template>
          <template v-else-if="o.order_type === 'custom'">📝 {{ o.biz_fields.description || '' }}</template>
        </div>
      </div>
      <div class="order-card-actions">
        <router-link :to="'/rider/accept/' + o.order_id" class="btn btn-primary btn-sm">⚡ 抢单</router-link>
      </div>
    </div>

    <!-- My active orders -->
    <div class="section-header" style="margin-top:24px"><h3>🚚 我的进行中订单</h3><span class="count-badge">{{ myActive.length }}</span></div>
    <div v-if="myActive.length === 0" class="empty-state"><span class="icon">🚚</span><p>暂无订单</p></div>
    <div class="order-card" :class="'st-' + o.status" v-for="o in myActive" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-type">{{ typeLabel(o.order_type) }}</span>
        <span class="badge" :class="'badge-' + o.status">{{ statusLabel(o.status) }}</span>
      </div>
      <div class="order-card-body">
        <p>📍 {{ o.delivery_addr }}</p>
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
      </div>
      <div class="order-card-actions">
        <button class="btn btn-outline btn-sm" @click="openChat(o)">联系顾客</button>
        <button v-if="o.status === 'accepted'" class="btn btn-primary btn-sm" @click="updateStatus(o.order_id, 'delivering')">🚚 开始配送</button>
        <button v-if="o.status === 'delivering'" class="btn btn-success btn-sm" @click="updateStatus(o.order_id, 'delivered')">✅ 确认送达</button>
      </div>
    </div>

    <!-- Completed -->
    <div class="section-header" style="margin-top:24px"><h3>✅ 已完成</h3><span class="count-badge">{{ myCompleted.length }}</span></div>
    <div class="order-card st-completed" v-for="o in myCompleted" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-type">{{ typeLabel(o.order_type) }}</span>
        <span class="badge badge-completed">已完成</span>
      </div>
      <div class="order-card-body">
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
        <p>✅ {{ fmtDate(o.completed_at) }}</p>
        <p v-if="o.review" style="color:#F59E0B;font-size:0.9rem">
          ⭐ {{ o.review.rating.toFixed(0) }}分
          <span v-if="o.review.comment" style="color:var(--text-secondary);font-size:0.8rem">"{{ o.review.comment }}"</span>
        </p>
      </div>
    </div>

    <OrderChat
      v-if="chatTarget"
      :open="!!chatTarget"
      :order-id="chatTarget.order_id"
      :order-no="chatTarget.order_no"
      @close="closeChat"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/user'
import { api } from '../api'
import NavTabs from '../components/NavTabs.vue'
import OrderChat from '../components/OrderChat.vue'

const userStore = useUserStore()
const pendingOrders = ref([])
const myActive = ref([])
const myCompleted = ref([])
const chatTarget = ref(null)

const completed = computed(() => userStore.userInfo?.rider?.total_orders || 0)
const avgRating = computed(() => {
  const score = userStore.userInfo?.rider?.credit_score
  return score != null ? score.toFixed(1) : '-'
})
const praiseRate = computed(() => {
  const rate = userStore.userInfo?.rider?.praise_rate
  return rate != null ? Math.round(rate * 100) + '%' : '-'
})
async function loadData() {
  const [pRes, mRes] = await Promise.all([
    api('/orders/pending'),
    api('/orders/rider/my'),
  ])
  if (pRes.ok) pendingOrders.value = pRes.data || []
  if (mRes.ok) {
    myActive.value = mRes.data.active || []
    myCompleted.value = mRes.data.completed || []
  }
}

async function updateStatus(orderId, status) {
  const res = await api(`/orders/update_status?order_id=${orderId}&status=${status}`, { method: 'POST' })
  if (res.ok) { window.$toast('状态更新成功', 'success'); loadData() }
  else window.$toast(res.message)
}

function openChat(order) {
  chatTarget.value = order
}

function closeChat() {
  chatTarget.value = null
}

function typeLabel(t) { return { takeout: '外卖', express: '快递', shopping: '代买', custom: '自定义' }[t] || t }
function statusLabel(s) { return { accepted: '已接单', delivering: '配送中', delivered: '已送达' }[s] || s }
function fmtDate(d) { return d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-' }

function handleOrderNotification() { loadData() }

onMounted(async () => {
  window.addEventListener('order-notification', handleOrderNotification)
  await userStore.fetchProfile()
  loadData()
})
onUnmounted(() => window.removeEventListener('order-notification', handleOrderNotification))
</script>

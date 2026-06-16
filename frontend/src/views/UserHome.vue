<template>
  <div>
    <NavTabs />

    <div style="margin:15px 0;">
      <button class="btn btn-sm" @click="currentType='all'">全部</button>
      <button class="btn btn-sm" @click="currentType='takeout'">外卖</button>
      <button class="btn btn-sm" @click="currentType='express'">快递</button>
      <button class="btn btn-sm" @click="currentType='shopping'">代买</button>
      <button class="btn btn-sm" @click="currentType='custom'">自定义</button>
    </div>

    <!-- Pending -->
    <div class="section-header"><h3>待接单</h3><span class="count-badge">{{ orders.pending.length }}</span></div>
    <div v-if="orders.pending.length === 0" class="empty-state"><span class="icon">📭</span><p>暂无待接单订单</p></div>
    <div class="order-card st-pending" v-for="o in filterOrders(orders.pending)" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-type">{{ typeLabel(o.order_type) }}</span>
        <span class="badge badge-pending">待接单</span>
      </div>
      <div class="order-card-body">
        <p>📍 {{ o.delivery_addr }}</p>
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
        <p>🕒 {{ fmtDate(o.created_at) }}</p>
      </div>
      <div class="order-card-actions">
        <router-link :to="'/orders/' + o.order_id" class="btn btn-outline btn-sm">查看详情</router-link>
        <button v-if="o.rider_id" class="btn btn-outline btn-sm" @click="openChat(o)">聊天</button>
        <button class="btn btn-danger btn-sm" @click="cancelOrder(o.order_id)">取消订单</button>
      </div>
    </div>

    <!-- Active: accepted + delivering -->
    <div class="section-header" style="margin-top:24px"><h3>进行中</h3><span class="count-badge">{{ orders.active.length }}</span></div>
    <div v-if="orders.active.length === 0" class="empty-state"><span class="icon">🚚</span><p>暂无进行中订单</p></div>
    <div class="order-card" :class="'st-' + o.status" v-for="o in filterOrders(orders.active)" :key="o.order_id">
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
  <router-link
    :to="'/orders/' + o.order_id"
    class="btn btn-outline btn-sm"
  >
    查看详情
  </router-link>

  <button
    v-if="o.rider_id"
    class="btn btn-outline btn-sm"
    @click="openChat(o)"
  >
    聊天
  </button>

  <button
    v-if="o.status === 'delivered'"
    class="btn btn-success btn-sm"
    @click="confirmDelivery(o.order_id)"
  >✅ 确认收货并结算</button>
</div>
    </div>

    <!-- Delivered (waiting confirm) -->
    <div class="section-header" style="margin-top:24px" v-if="orders.delivered.length > 0">
      <h3>已送达待确认</h3><span class="count-badge">{{ orders.delivered.length }}</span>
    </div>
    <div class="order-card st-delivered" v-for="o in filterOrders(orders.delivered)" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-delivered">已送达</span>
      </div>
      <div class="order-card-body">
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
      </div>
      <div class="order-card-actions">
        <button v-if="o.rider_id" class="btn btn-outline btn-sm" @click="openChat(o)">聊天</button>
        <button class="btn btn-success btn-sm" @click="confirmDelivery(o.order_id)">✅ 确认收货并结算</button>
      </div>
    </div>

    <!-- Completed -->
    <div class="section-header" style="margin-top:24px"><h3>已完成</h3><span class="count-badge">{{ orders.completed.length }}</span></div>
    <div class="order-card st-completed" v-for="o in filterOrders(orders.completed)" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-type">{{ typeLabel(o.order_type) }}</span>
        <span class="badge badge-completed">已完成</span>
      </div>
      <div class="order-card-body">
        <p>📍 {{ o.delivery_addr }}</p>
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
        <p>✅ {{ fmtDate(o.completed_at) }}</p>
      </div>
      <div class="order-card-actions">
        <button v-if="!o.review" class="btn btn-warning btn-sm" @click="openReview(o)">⭐ 评价</button>
        <div v-else class="review-result">
          <span class="review-stars">{{ '★'.repeat(o.review.rating) }}{{ '☆'.repeat(5 - o.review.rating) }}</span>
          <p v-if="o.review.comment" class="review-comment-text">"{{ o.review.comment }}"</p>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <div v-if="reviewTarget" class="review-modal-overlay" @click.self="closeReview">
      <div class="review-modal">
        <h3>⭐ 订单评价</h3>
        <p style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:16px">订单号：{{ reviewTarget.order_no }}</p>
        <div class="star-rating">
          <span v-for="s in 5" :key="s" class="star" :class="{ active: s <= reviewRating }" @click="setRating(s)">{{ s <= reviewRating ? '★' : '☆' }}</span>
        </div>
        <textarea v-model="reviewComment" class="review-textarea" placeholder="写下你的评价（可选，最多512字）" maxlength="512" rows="3"></textarea>
        <div class="review-modal-actions">
          <button class="btn btn-ghost" @click="closeReview">取消</button>
          <button class="btn btn-warning" :disabled="reviewRating === 0 || reviewLoading" @click="submitReview">
            {{ reviewLoading ? '提交中...' : '提交评价' }}
          </button>
        </div>
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

import { reactive, ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/user'
import { api } from '../api'
import NavTabs from '../components/NavTabs.vue'
import OrderChat from '../components/OrderChat.vue'

const userStore = useUserStore()
const orders = reactive({ pending: [], active: [], delivered: [], completed: [], cancelled: [] })
const currentType = ref('all')

// Review state
const reviewTarget = ref(null)
const reviewRating = ref(0)
const reviewComment = ref('')
const reviewLoading = ref(false)
const chatTarget = ref(null)

async function loadOrders() {
  const res = await api('/orders/my')
  if (res.ok) {
    orders.pending = res.data.pending || []
    orders.active = res.data.active || []
    orders.delivered = res.data.delivered || []
    orders.completed = res.data.completed || []
    orders.cancelled = res.data.cancelled || []
  }
}

async function cancelOrder(id) {
  if (!confirm('确认取消该订单？')) return
  const res = await api(`/orders/cancel/${id}`, { method: 'POST' })
  if (res.ok) { window.$toast('订单已取消', 'success'); loadOrders() }
  else window.$toast(res.message)
}

async function confirmDelivery(id) {
  if (!confirm('确认收货？将自动结算。')) return
  const res = await api(`/orders/complete/${id}`, { method: 'POST' })
  if (res.ok) { window.$toast('结算完成！', 'success'); loadOrders() }
  else window.$toast(res.message)
}

function typeLabel(t) {
  const m = { takeout: '外卖', express: '快递', shopping: '代买', custom: '自定义' }
  return m[t] || t
}

function statusLabel(s) {
  const m = { pending: '待接单', accepted: '已接单', delivering: '配送中', delivered: '已送达', completed: '已完成' }
  return m[s] || s
}

function filterOrders(list) {
  if (currentType.value === 'all') {
    return list
  }

  return list.filter(
    o => o.order_type === currentType.value
  )
}

function fmtDate(d) { return d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-' }

function openReview(order) {
  reviewTarget.value = order
  reviewRating.value = 0
  reviewComment.value = ''
}

function closeReview() {
  reviewTarget.value = null
}

function openChat(order) {
  chatTarget.value = order
}

function closeChat() {
  chatTarget.value = null
}

function setRating(v) {
  reviewRating.value = v
}

async function submitReview() {
  if (reviewRating.value === 0) return
  reviewLoading.value = true
  const res = await api('/reviews/create', {
    method: 'POST',
    body: JSON.stringify({
      order_id: reviewTarget.value.order_id,
      rating: reviewRating.value,
      comment: reviewComment.value || null,
    }),
  })
  reviewLoading.value = false
  if (res.ok) {
    window.$toast('评价成功！', 'success')
    closeReview()
    loadOrders()
  } else {
    window.$toast(res.message)
  }
}

function handleOrderNotification() { loadOrders() }

onMounted(() => {
  window.addEventListener('order-notification', handleOrderNotification)
  loadOrders()
})
onUnmounted(() => window.removeEventListener('order-notification', handleOrderNotification))
</script>

<style scoped>
.review-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.review-modal {
  background: var(--bg-primary,#fff);
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.review-modal h3 {
  margin: 0 0 4px 0;
}
.star-rating {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 16px 0;
}
.star {
  font-size: 2rem;
  cursor: pointer;
  color: #ccc;
  transition: color 0.15s;
  user-select: none;
}
.star.active {
  color: #F59E0B;
}
.review-textarea {
  width: 100%;
  border: 1px solid var(--border-color,#ddd);
  border-radius: 8px;
  padding: 10px;
  font-size: 0.9rem;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}
.review-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}
.badge-reviewed {
  background: #D1FAE5;
  color: #065F46;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
}
.btn-warning {
  background: #F59E0B;
  color: #fff;
  border: none;
}
.btn-ghost {
  background: transparent;
  border: 1px solid var(--border-color,#ddd);
  color: var(--text-secondary,#666);
}
.review-result {
  text-align: center;
  padding: 4px 0;
}
.review-stars {
  color: #F59E0B;
  font-size: 1.1rem;
  letter-spacing: 2px;
}
.review-comment-text {
  color: var(--text-secondary,#888);
  font-size: 0.85rem;
  margin: 4px 0 0 0;
  font-style: italic;
}
</style>

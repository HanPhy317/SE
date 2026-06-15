<template>
  <div>
    <div class="page-header">
      <h2>📦 我的订单</h2>
      <div class="actions">
        <router-link to="/user/place-order" class="btn btn-primary btn-sm">➕ 发布新订单</router-link>
        <router-link v-if="userStore.userInfo?.rider" to="/rider/home" class="btn btn-outline btn-sm">🛵 骑手模式</router-link>
      </div>
    </div>

    <!-- Pending -->
    <div class="section-header"><h3>待接单</h3><span class="count-badge">{{ orders.pending.length }}</span></div>
    <div v-if="orders.pending.length === 0" class="empty-state"><span class="icon">📭</span><p>暂无待接单订单</p></div>
    <div class="order-card st-pending" v-for="o in orders.pending" :key="o.order_id">
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
        <button class="btn btn-danger btn-sm" @click="cancelOrder(o.order_id)">取消订单</button>
      </div>
    </div>

    <!-- Active: accepted + delivering -->
    <div class="section-header" style="margin-top:24px"><h3>进行中</h3><span class="count-badge">{{ orders.active.length }}</span></div>
    <div v-if="orders.active.length === 0" class="empty-state"><span class="icon">🚚</span><p>暂无进行中订单</p></div>
    <div class="order-card" :class="'st-' + o.status" v-for="o in orders.active" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-type">{{ typeLabel(o.order_type) }}</span>
        <span class="badge" :class="'badge-' + o.status">{{ statusLabel(o.status) }}</span>
      </div>
      <div class="order-card-body">
        <p>📍 {{ o.delivery_addr }}</p>
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
      </div>
      <div class="order-card-actions" v-if="o.status === 'delivered'">
        <button class="btn btn-success btn-sm" @click="confirmDelivery(o.order_id)">✅ 确认收货并结算</button>
      </div>
    </div>

    <!-- Delivered (waiting confirm) -->
    <div class="section-header" style="margin-top:24px" v-if="orders.delivered.length > 0">
      <h3>已送达待确认</h3><span class="count-badge">{{ orders.delivered.length }}</span>
    </div>
    <div class="order-card st-delivered" v-for="o in orders.delivered" :key="o.order_id">
      <div class="order-card-header">
        <span class="order-no">{{ o.order_no }}</span>
        <span class="badge badge-delivered">已送达</span>
      </div>
      <div class="order-card-body">
        <p class="order-reward">💰 ¥{{ o.reward.toFixed(2) }}</p>
      </div>
      <div class="order-card-actions">
        <button class="btn btn-success btn-sm" @click="confirmDelivery(o.order_id)">✅ 确认收货并结算</button>
      </div>
    </div>

    <!-- Completed -->
    <div class="section-header" style="margin-top:24px"><h3>已完成</h3><span class="count-badge">{{ orders.completed.length }}</span></div>
    <div class="order-card st-completed" v-for="o in orders.completed" :key="o.order_id">
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
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { api } from '../api'

const userStore = useUserStore()
const orders = reactive({ pending: [], active: [], delivered: [], completed: [], cancelled: [] })

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

function fmtDate(d) { return d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-' }

onMounted(loadOrders)
</script>

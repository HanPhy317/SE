<template>
  <div class="accept-container">
    <div class="page-header">
      <h2>⚡ 确认接单</h2>
      <router-link to="/rider/home" class="btn btn-ghost btn-sm">← 返回</router-link>
    </div>

    <div v-if="!order">
      <div class="empty-state"><span class="icon">📭</span><p>订单不存在或已删除</p></div>
      <router-link to="/rider/home" class="btn btn-ghost btn-block" style="margin-top:16px">返回大厅</router-link>
    </div>

    <template v-else>
      <!-- Detail Card -->
      <div class="order-detail-card">
        <div class="detail-header">
          <span class="reward-display">¥{{ order.reward.toFixed(2) }}</span>
          <span class="reward-label">酬劳</span>
        </div>
        <div class="detail-body">
          <div class="detail-row"><span class="dl">订单编号</span><span class="dv">{{ order.order_no }}</span></div>
          <div class="detail-row"><span class="dl">订单类型</span><span class="dv"><span class="badge badge-type">{{ typeLabel(order.order_type) }}</span></span></div>
          <div class="detail-row"><span class="dl">订单状态</span><span class="dv"><span class="badge" :class="'badge-' + order.status">{{ statusLabel(order.status) }}</span></span></div>
          <div class="detail-row"><span class="dl">配送地址</span><span class="dv">{{ order.delivery_addr }}</span></div>
          <div class="detail-row"><span class="dl">发布时间</span><span class="dv">{{ fmtDate(order.created_at) }}</span></div>
          <template v-for="(v, k) in order.biz_fields" :key="k">
            <div class="detail-row"><span class="dl">{{ k }}</span><span class="dv">{{ v }}</span></div>
          </template>
        </div>
      </div>

      <!-- Already taken -->
      <div v-if="order.status !== 'pending'" class="confirm-section">
        <div class="confirm-warn">⚠️ 该订单已被其他骑手接走，无法接单</div>
        <router-link to="/rider/home" class="btn btn-ghost btn-block">返回大厅</router-link>
      </div>

      <!-- Confirm grab -->
      <div v-else class="confirm-section">
        <div class="confirm-warn">
          <span>⚡ 确认接单后请及时完成配送任务，超时可能影响信用评分。</span>
        </div>
        <button class="grab-btn" @click="handleAccept" :disabled="loading">
          {{ loading ? '⌛ 抢单中...' : '💰 立即抢单' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const props = defineProps({ id: String })
const router = useRouter()
const order = ref(null)
const loading = ref(false)

onMounted(async () => {
  const res = await api(`/orders/${props.id}`)
  if (res.ok) order.value = res.data
})

async function handleAccept() {
  loading.value = true
  const res = await api(`/orders/accept/${props.id}`, { method: 'POST' })
  loading.value = false
  if (res.ok) {
    window.$toast('接单成功！', 'success')
    setTimeout(() => router.push('/rider/home'), 800)
  } else {
    window.$toast(res.message)
    // Refresh to get latest status
    const fres = await api(`/orders/${props.id}`)
    if (fres.ok) order.value = fres.data
  }
}

function typeLabel(t) { return { takeout: '外卖', express: '快递', shopping: '代买', custom: '自定义' }[t] || t }
function statusLabel(s) { return { pending: '待接单', accepted: '已接单', delivering: '配送中', delivered: '已送达', completed: '已完成' }[s] || s }
function fmtDate(d) { return d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-' }
</script>

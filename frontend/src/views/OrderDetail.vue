<template>
  <div>
    <div class="page-header">
      <h2>📄 订单详情</h2>
      <router-link to="/user/home" class="btn btn-ghost btn-sm">返回</router-link>
    </div>

    <div v-if="loading" class="empty-state">
      <p>加载中...</p>
    </div>

    <div v-else-if="order" class="card" style="padding:20px">
      <p><b>订单号：</b>{{ order.order_no }}</p>
      <p><b>订单类型：</b>{{ typeLabel(order.order_type) }}</p>
      <p><b>订单状态：</b>{{ statusLabel(order.status) }}</p>
      <p><b>配送地址：</b>{{ order.delivery_addr }}</p>
      <p><b>酬劳金额：</b>¥{{ order.reward.toFixed(2) }}</p>
      <p><b>创建时间：</b>{{ fmtDate(order.created_at) }}</p>
      <p v-if="order.completed_at"><b>完成时间：</b>{{ fmtDate(order.completed_at) }}</p>

      <hr style="margin:16px 0" />

      <template v-if="order.order_type === 'shopping'">
        <h3>🛒 代买信息</h3>
        <p><b>店铺名称：</b>{{ order.biz_fields?.store_name || '-' }}</p>
        <p><b>商品名称：</b>{{ order.biz_fields?.item_name || '-' }}</p>
        <p><b>预估重量：</b>{{ order.biz_fields?.item_weight || '-' }}</p>
        <p><b>购买数量：</b>{{ order.biz_fields?.quantity || '-' }}</p>
        <p><b>备注：</b>{{ order.biz_fields?.remark || '-' }}</p>
      </template>

      <template v-else-if="order.order_type === 'takeout'">
        <h3>🍱 外卖信息</h3>
        <p><b>外卖描述：</b>{{ order.biz_fields?.item_desc || '-' }}</p>
        <p><b>取餐地址：</b>{{ order.biz_fields?.pickup_addr || '-' }}</p>
        <p><b>数量：</b>{{ order.biz_fields?.quantity || '-' }}</p>
        <p><b>备注：</b>{{ order.biz_fields?.remark || '-' }}</p>
      </template>

      <template v-else-if="order.order_type === 'express'">
        <h3>📦 快递信息</h3>
        <p><b>快递公司：</b>{{ order.biz_fields?.company || '-' }}</p>
        <p><b>快递单号：</b>{{ order.biz_fields?.tracking_no || '-' }}</p>
        <p><b>取件地址：</b>{{ order.biz_fields?.pickup_addr || '-' }}</p>
      </template>

      <template v-else-if="order.order_type === 'custom'">
        <h3>📝 自定义任务</h3>
        <p><b>任务描述：</b>{{ order.biz_fields?.description || '-' }}</p>
        <p><b>截止时间：</b>{{ order.biz_fields?.deadline || '-' }}</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const loading = ref(true)
const order = ref(null)

async function loadDetail() {
  loading.value = true
  const res = await api(`/orders/${route.params.id}`)
  loading.value = false

  if (res.ok) {
    order.value = res.data
  } else {
    window.$toast(res.message)
  }
}

function typeLabel(t) {
  return { takeout: '外卖', express: '快递', shopping: '代买', custom: '自定义' }[t] || t
}

function statusLabel(s) {
  return {
    pending: '待接单',
    accepted: '已接单',
    delivering: '配送中',
    delivered: '已送达',
    completed: '已完成',
    cancelled: '已取消'
  }[s] || s
}

function fmtDate(d) {
  return d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'
}

onMounted(loadDetail)
</script>

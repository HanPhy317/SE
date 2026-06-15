<template>
  <div>
    <div class="page-header">
      <h2>➕ 发布新订单</h2>
      <router-link to="/user/home" class="btn btn-ghost btn-sm">返回</router-link>
    </div>

    <form @submit.prevent="handleSubmit" class="card" style="padding:20px">
      <div class="form-group">
        <label>订单类型</label>
        <select v-model="form.order_type" required>
          <option value="">-- 请选择 --</option>
          <option value="takeout">🍱 外卖跑腿</option>
          <option value="express">📦 快递跑腿</option>
          <option value="shopping">🛒 代买服务</option>
          <option value="custom">📝 自定义跑腿</option>
        </select>
      </div>
      <div class="form-group">
        <label>配送地址</label>
        <input v-model="form.delivery_addr" placeholder="请输入送达地址" required />
      </div>
      <div class="form-group">
        <label>酬劳金额 (元)</label>
        <input v-model.number="form.reward" type="number" placeholder="请输入酬劳" min="0.01" step="0.01" required />
      </div>

      <!-- Takeout -->
      <fieldset v-if="form.order_type === 'takeout'" style="border:2px solid var(--gray-200);border-radius:var(--radius-sm);padding:12px;margin-top:8px">
        <legend style="font-weight:700;color:var(--primary);padding:0 6px">外卖信息</legend>
        <div class="form-group"><label>外卖描述</label><input v-model="biz.item_desc" placeholder="如：一份黄焖鸡米饭" /></div>
        <div class="form-group"><label>取餐地址</label><input v-model="biz.pickup_addr" placeholder="如：三食堂二楼" /></div>
      </fieldset>

      <!-- Express -->
      <fieldset v-if="form.order_type === 'express'" style="border:2px solid var(--gray-200);border-radius:var(--radius-sm);padding:12px;margin-top:8px">
        <legend style="font-weight:700;color:var(--primary);padding:0 6px">快递信息</legend>
        <div class="form-group"><label>快递公司</label><input v-model="biz.company" placeholder="如：顺丰快递" /></div>
        <div class="form-group"><label>快递单号</label><input v-model="biz.tracking_no" placeholder="请输入快递单号" /></div>
        <div class="form-group"><label>取件地址</label><input v-model="biz.pickup_addr" placeholder="如：菜鸟驿站" /></div>
      </fieldset>

      <!-- Shopping -->
      <fieldset v-if="form.order_type === 'shopping'" style="border:2px solid var(--gray-200);border-radius:var(--radius-sm);padding:12px;margin-top:8px">
        <legend style="font-weight:700;color:var(--primary);padding:0 6px">代买信息</legend>
        <div class="form-group"><label>店铺名称</label><input v-model="biz.store_name" placeholder="如：校园超市" /></div>
        <div class="form-group"><label>商品名称</label><input v-model="biz.item_name" placeholder="如：一瓶矿泉水" /></div>
        <div class="form-group"><label>预估重量</label><input v-model="biz.item_weight" placeholder="如：500g" /></div>
      </fieldset>

      <!-- Custom -->
      <fieldset v-if="form.order_type === 'custom'" style="border:2px solid var(--gray-200);border-radius:var(--radius-sm);padding:12px;margin-top:8px">
        <legend style="font-weight:700;color:var(--primary);padding:0 6px">任务描述</legend>
        <div class="form-group"><label>详细描述</label><textarea v-model="biz.description" rows="3" placeholder="请描述你的跑腿任务"></textarea></div>
        <div class="form-group"><label>截止时间</label><input v-model="biz.deadline" type="datetime-local" /></div>
      </fieldset>

      <button type="submit" class="btn btn-primary btn-block" style="margin-top:16px" :disabled="loading">
        {{ loading ? '提交中...' : '发布订单' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const loading = ref(false)
const form = reactive({ order_type: '', delivery_addr: '', reward: 0 })
const biz = reactive({})

async function handleSubmit() {
  loading.value = true
  const res = await api('/orders/create', {
    method: 'POST',
    body: JSON.stringify({ ...form, biz_fields: { ...biz } }),
  })
  loading.value = false
  if (res.ok) {
    window.$toast('订单发布成功！', 'success')
    router.push('/user/home')
  } else {
    window.$toast(res.message)
  }
}
</script>

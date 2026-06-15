<template>
  <div class="profile-page">
    <div class="info-card" v-if="profile">
      <div class="info-card-header">
        <span class="avatar">{{ isRider ? '🛵' : '👤' }}</span>
        <h3>{{ profile.username }}</h3>
        <span style="opacity:0.8;font-size:0.8rem">{{ isRider ? '骑手' : '普通用户' }}</span>
      </div>
      <div class="info-card-body">
        <div class="info-row"><span class="l">手机号</span><span class="v">{{ profile.phone }}</span></div>
        <div class="info-row"><span class="l">账户余额</span><span class="v" style="color:var(--danger)">¥{{ profile.balance }}</span></div>
        <div class="info-row"><span class="l">默认地址</span><span class="v">{{ profile.default_address || '未设置' }}</span></div>
        <div class="info-row"><span class="l">注册时间</span><span class="v">{{ fmtDate(profile.created_at) }}</span></div>
      </div>
    </div>

    <!-- Rider info -->
    <div class="info-card" v-if="isRider && profile?.rider">
      <div class="info-card-header" style="background:linear-gradient(135deg,#F59E0B,#F97316)">
        <h3>骑手信息</h3>
      </div>
      <div class="info-card-body">
        <div class="info-row"><span class="l">服务区域</span><span class="v">{{ profile.rider.service_area || '未设置' }}</span></div>
        <div class="info-row"><span class="l">信用评分</span><span class="v">{{ profile.rider.credit_score }}</span></div>
        <div class="info-row"><span class="l">总接单数</span><span class="v">{{ profile.rider.total_orders }}单</span></div>
        <div class="info-row"><span class="l">好评率</span><span class="v">{{ Math.round((profile.rider.praise_rate || 1) * 100) }}%</span></div>
        <div class="info-row"><span class="l">成为骑手时间</span><span class="v">{{ fmtDate(profile.rider.created_at) }}</span></div>
      </div>
    </div>

    <!-- Become rider -->
    <div class="become-rider-box" v-if="!isRider">
      <h3>🛵 成为骑手，接单赚钱！</h3>
      <p>注册成为骑手后，您可以抢单配送</p>
      <form @submit.prevent="handleBecomeRider" style="max-width:300px;margin:0 auto;display:flex;flex-direction:column;gap:12px;">
        <div class="form-group">
          <input v-model="serviceArea" placeholder="服务区域 (如：北校区)" required />
        </div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? '提交中...' : '注册骑手' }}
        </button>
      </form>
    </div>

    <router-link v-if="isRider" to="/rider/home" class="btn btn-primary btn-block" style="margin-top:12px">前往骑手大厅</router-link>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const isRider = computed(() => !!userStore.userInfo?.rider)
const profile = computed(() => userStore.userInfo)
const serviceArea = ref('')
const loading = ref(false)

onMounted(async () => {
  await userStore.fetchProfile()
})

function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

async function handleBecomeRider() {
  loading.value = true
  const res = await userStore.becomeRider(serviceArea.value)
  loading.value = false
  if (res.ok) {
    window.$toast('骑手注册成功！', 'success')
  } else {
    window.$toast(res.message || '注册失败')
  }
}
</script>

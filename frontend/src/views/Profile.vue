<template>
  <div class="profile-page">
    <!-- User Info Card -->
    <div class="info-card" v-if="profile">
      <div class="info-card-header">
        <span class="avatar">{{ isRider ? '🛵' : '👤' }}</span>
        <h3>{{ profile.username }}</h3>
        <span style="opacity:0.8;font-size:0.8rem">{{ isRider ? '骑手' : '普通用户' }}</span>
      </div>
      <div class="info-card-body">
        <div class="info-row"><span class="l">手机号</span><span class="v">{{ profile.phone }}</span></div>
        <div class="info-row"><span class="l">账户余额</span><span class="v" style="color:var(--danger);font-weight:700">¥{{ profile.balance }}</span></div>
        <div class="info-row"><span class="l">默认地址</span><span class="v">{{ profile.default_address || '未设置' }}</span></div>
        <div class="info-row"><span class="l">注册时间</span><span class="v">{{ fmtDate(profile.created_at) }}</span></div>
      </div>
    </div>

    <!-- Edit Profile -->
    <div class="card" style="padding:20px;margin-bottom:16px">
      <div class="section-header"><h3>✏️ 修改个人信息</h3></div>
      <form @submit.prevent="handleUpdateProfile" style="display:flex;flex-direction:column;gap:12px">
        <div class="form-group">
          <label>手机号</label>
          <input v-model="editForm.phone" type="tel" placeholder="11位手机号" pattern="[0-9]{11}" />
        </div>
        <div class="form-group">
          <label>默认地址</label>
          <input v-model="editForm.default_address" placeholder="如：北校区宿舍3号楼501" />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="editLoading">
          {{ editLoading ? '保存中...' : '保存修改' }}
        </button>
      </form>
    </div>

    <!-- Topup -->
    <div class="card" style="padding:20px;margin-bottom:16px">
      <div class="section-header"><h3>💰 账户充值</h3></div>
      <form @submit.prevent="handleTopup" style="display:flex;flex-direction:column;gap:12px">
        <div class="form-group">
          <label>充值金额（元）</label>
          <input v-model.number="topupAmount" type="number" placeholder="请输入充值金额" min="0.01" step="0.01" required />
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button type="button" class="btn btn-ghost btn-sm" v-for="a in presetAmounts" :key="a" @click="topupAmount = a">¥{{ a }}</button>
        </div>
        <button type="submit" class="btn btn-success" :disabled="topupLoading">
          {{ topupLoading ? '充值中...' : '立即充值' }}
        </button>
      </form>
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
        <button type="submit" class="btn btn-primary btn-block" :disabled="riderLoading">
          {{ riderLoading ? '提交中...' : '注册骑手' }}
        </button>
      </form>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const isRider = computed(() => !!userStore.userInfo?.rider)
const profile = computed(() => userStore.userInfo)

// Edit profile
const editForm = reactive({ phone: '', default_address: '' })
const editLoading = ref(false)

// Topup
const topupAmount = ref(50)
const topupLoading = ref(false)
const presetAmounts = [10, 20, 50, 100, 200]

// Become rider
const serviceArea = ref('')
const riderLoading = ref(false)

onMounted(async () => {
  await userStore.fetchProfile()
  if (userStore.userInfo) {
    editForm.phone = userStore.userInfo.phone || ''
    editForm.default_address = userStore.userInfo.default_address || ''
  }
})

function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

async function handleUpdateProfile() {
  editLoading.value = true
  const res = await userStore.updateProfile({
    phone: editForm.phone || null,
    default_address: editForm.default_address || null,
  })
  editLoading.value = false
  if (res.ok) {
    window.$toast('信息更新成功！', 'success')
  } else {
    window.$toast(res.message || '更新失败')
  }
}

async function handleTopup() {
  if (topupAmount.value <= 0) {
    window.$toast('充值金额必须大于0')
    return
  }
  topupLoading.value = true
  const res = await userStore.topup(topupAmount.value)
  topupLoading.value = false
  if (res.ok) {
    window.$toast(`充值成功，余额 ¥${res.data.balance}`, 'success')
    topupAmount.value = 50
  } else {
    window.$toast(res.message || '充值失败')
  }
}

async function handleBecomeRider() {
  riderLoading.value = true
  const res = await userStore.becomeRider(serviceArea.value)
  riderLoading.value = false
  if (res.ok) {
    window.$toast('骑手注册成功！', 'success')
  } else {
    window.$toast(res.message || '注册失败')
  }
}
</script>

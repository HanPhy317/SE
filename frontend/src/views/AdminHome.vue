<template>
  <div class="admin-page">
    <h2>👑 管理后台</h2>

    <!-- Tab navigation -->
    <div class="admin-tabs">
      <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">👥 用户管理</button>
      <button :class="{ active: activeTab === 'transactions' }" @click="activeTab = 'transactions'">💳 交易记录</button>
    </div>

    <!-- Users tab -->
    <div v-if="activeTab === 'users'">
      <div class="section-header">
        <h3>所有用户</h3>
        <span class="count-badge">{{ users.length }}人</span>
      </div>
      <div v-if="loading" class="empty-state">加载中...</div>
      <div v-else-if="users.length === 0" class="empty-state"><p>暂无用户</p></div>
      <div v-else>
        <div class="user-card" v-for="u in users" :key="u.user_id">
          <div class="user-card-header">
            <span class="username">{{ u.username }}</span>
            <span class="badge" :class="u.is_banned ? 'badge-danger' : 'badge-success'">
              {{ u.is_banned ? '已封禁' : '正常' }}
            </span>
          </div>
          <div class="user-card-body">
            <div class="info-row"><span class="l">手机号</span><span class="v">{{ u.phone }}</span></div>
            <div class="info-row"><span class="l">余额</span><span class="v">¥{{ u.balance }}</span></div>
            <div class="info-row"><span class="l">注册时间</span><span class="v">{{ fmtDate(u.created_at) }}</span></div>
          </div>
          <div class="user-card-actions">
            <button v-if="!u.is_banned" class="btn btn-danger btn-sm" @click="banUser(u.user_id)">🔨 封禁</button>
            <button v-else class="btn btn-success btn-sm" @click="unbanUser(u.user_id)">✅ 解封</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transactions tab -->
    <div v-if="activeTab === 'transactions'">
      <div class="section-header">
        <h3>所有交易记录</h3>
        <span class="count-badge">{{ transactions.length }}笔</span>
      </div>
      <div v-if="loading" class="empty-state">加载中...</div>
      <div v-else-if="transactions.length === 0" class="empty-state"><p>暂无交易记录</p></div>
      <div v-else>
        <div class="txn-card" v-for="t in transactions" :key="t.txn_id">
          <div class="txn-card-header">
            <span class="txn-id">#{{ t.txn_id }}</span>
            <span class="badge" :class="txnBadgeClass(t.txn_type)">{{ txnLabel(t.txn_type) }}</span>
          </div>
          <div class="txn-card-body">
            <div class="info-row"><span class="l">用户</span><span class="v">{{ t.username }}</span></div>
            <div class="info-row"><span class="l">订单</span><span class="v">{{ t.order_no }}</span></div>
            <div class="info-row"><span class="l">金额</span>
              <span class="v" :class="t.txn_type === 'debit' ? 'text-danger' : 'text-success'">
                {{ t.txn_type === 'debit' ? '-' : '+' }}¥{{ t.amount }}
              </span>
            </div>
            <div class="info-row" v-if="t.description"><span class="l">说明</span><span class="v">{{ t.description }}</span></div>
            <div class="info-row"><span class="l">时间</span><span class="v">{{ fmtDate(t.created_at) }}</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { api } from '../api'

const activeTab = ref('users')
const loading = ref(false)
const users = ref([])
const transactions = ref([])

async function loadUsers() {
  loading.value = true
  const res = await api('/admin/users')
  if (res.ok) {
    users.value = res.data || []
  } else {
    window.$toast(res.message || '加载用户失败')
  }
  loading.value = false
}

async function loadTransactions() {
  loading.value = true
  const res = await api('/admin/transactions')
  if (res.ok) {
    transactions.value = res.data || []
  } else {
    window.$toast(res.message || '加载交易记录失败')
  }
  loading.value = false
}

async function banUser(userId) {
  if (!confirm('确认封禁该用户？封禁后该账号将无法登录。')) return
  const res = await api(`/admin/users/${userId}/ban`, { method: 'POST' })
  if (res.ok) {
    window.$toast('已封禁', 'success')
    await loadUsers()
  } else {
    window.$toast(res.message)
  }
}

async function unbanUser(userId) {
  if (!confirm('确认解封该用户？')) return
  const res = await api(`/admin/users/${userId}/unban`, { method: 'POST' })
  if (res.ok) {
    window.$toast('已解封', 'success')
    await loadUsers()
  } else {
    window.$toast(res.message)
  }
}

function fmtDate(d) {
  return d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'
}

function txnLabel(type) {
  return { debit: '支出', credit: '收入', refund: '退款' }[type] || type
}

function txnBadgeClass(type) {
  return { debit: 'badge-pending', credit: 'badge-success', refund: 'badge-cancelled' }[type] || ''
}

watch(activeTab, (tab) => {
  if (tab === 'users' && users.value.length === 0) loadUsers()
  if (tab === 'transactions' && transactions.value.length === 0) loadTransactions()
})

onMounted(() => { loadUsers() })
</script>

<style scoped>
.admin-page { max-width: 600px; margin: 0 auto; }
.admin-page h2 { font-size: 1.3rem; font-weight: 700; margin-bottom: 20px; }

.admin-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.admin-tabs button {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  background: #fff;
  font-size: 0.9rem;
  cursor: pointer;
}
.admin-tabs button.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.section-header h3 { font-size: 1rem; font-weight: 600; margin: 0; }

.count-badge {
  background: var(--gray-100);
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  color: var(--gray-500);
}

.user-card, .txn-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 14px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 10px;
}
.user-card-header, .txn-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.user-card-header .username { font-weight: 700; font-size: 1rem; }
.txn-id { font-family: monospace; font-size: 0.8rem; color: var(--gray-400); }

.user-card-body, .txn-card-body { font-size: 0.88rem; }
.info-row { display: flex; justify-content: space-between; padding: 3px 0; }
.info-row .l { color: var(--gray-400); }
.info-row .v { font-weight: 500; }

.user-card-actions { display: flex; gap: 8px; margin-top: 10px; }

.text-danger { color: var(--danger); }
.text-success { color: var(--success); }

.empty-state { text-align: center; padding: 40px 0; color: var(--gray-400); }

.btn-sm { padding: 6px 14px; font-size: 0.82rem; }
</style>

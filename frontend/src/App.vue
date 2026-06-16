<template>
  <div id="app-wrapper">
    <!-- Navbar -->
    <header class="navbar">
      <div class="nav-inner">
        <router-link to="/login" class="brand"><img src="/WHU.webp" alt="WHU" class="brand-logo" />校园跑腿</router-link>
        <nav class="nav-links" v-if="userStore.isLoggedIn">
          <router-link to="/user/home">🏠 主页</router-link>
          <router-link to="/notifications" class="nav-link-badge">
            🔔 通知
            <span v-if="unreadCount" class="unread-badge">{{ unreadCount }}</span>
          </router-link>
          <router-link to="/profile">👤 个人</router-link>
          <router-link v-if="userStore.isAdmin" to="/admin/home">👑 管理</router-link>
          <span class="nav-user">{{ userStore.userInfo?.username }}</span>
          <a href="#" @click.prevent="doLogout" class="btn-logout">退出</a>
        </nav>
        <button class="hamburger" v-if="userStore.isLoggedIn" @click="toggleMenu" :class="{ open: menuOpen }">
          <span></span><span></span><span></span>
        </button>
      </div>
    </header>

    <!-- Mobile menu -->
    <div class="mobile-nav" :class="{ open: menuOpen }" v-if="userStore.isLoggedIn" @click.self="menuOpen = false">
      <div class="mobile-panel">
        <router-link to="/user/home" @click="menuOpen = false">🏠 主页</router-link>
        <router-link to="/notifications" @click="menuOpen = false">
          🔔 通知
          <span v-if="unreadCount" class="unread-badge inline">{{ unreadCount }}</span>
        </router-link>
        <router-link to="/profile" @click="menuOpen = false">👤 个人</router-link>
        <router-link v-if="userStore.isAdmin" to="/admin/home" @click="menuOpen = false">👑 管理后台</router-link>
        <div class="nav-divider"></div>
        <a href="#" @click.prevent="doLogout" class="logout-link">🚪 退出登录</a>
      </div>
    </div>

    <!-- Main -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- Mobile bottom nav -->
    <nav class="bottom-nav" v-if="userStore.isLoggedIn">
      <router-link to="/user/home">🏠<span>主页</span></router-link>
      <router-link to="/notifications" class="bottom-link-badge">
        🔔<span>通知</span>
        <span v-if="unreadCount" class="unread-badge bottom">{{ unreadCount }}</span>
      </router-link>
      <router-link to="/profile">👤<span>个人</span></router-link>
      <router-link v-if="userStore.isAdmin" to="/admin/home">👑<span>管理</span></router-link>
    </nav>

    <!-- Toast -->
    <div class="toast" v-if="toast.msg" :class="toast.type">
      <span class="toast-icon">{{ toast.type === 'error' ? '⚠️' : '✅' }}</span>
      <span>{{ toast.msg }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import { unreadNotificationCount } from './services/notifications'

const router = useRouter()
const userStore = useUserStore()
const menuOpen = ref(false)
const unreadCount = ref(0)

function toggleMenu() { menuOpen.value = !menuOpen.value }

function refreshUnreadCount() {
  unreadCount.value = unreadNotificationCount()
}

function doLogout() {
  userStore.logout()
  menuOpen.value = false
  refreshUnreadCount()
  router.push('/login')
}

// Toast
const toast = reactive({ msg: '', type: 'success' })
window.$toast = (msg, type = 'error') => {
  toast.msg = msg
  toast.type = type
  setTimeout(() => (toast.msg = ''), 3000)
}

onMounted(() => {
  refreshUnreadCount()
  window.addEventListener('notification-store-updated', refreshUnreadCount)
})
onUnmounted(() => window.removeEventListener('notification-store-updated', refreshUnreadCount))
watch(() => userStore.userInfo?.user_id, refreshUnreadCount)
</script>

<template>
  <div id="app-wrapper">
    <!-- Navbar -->
    <header class="navbar">
      <div class="nav-inner">
        <router-link to="/login" class="brand">🏃 校园跑腿</router-link>
        <nav class="nav-links" v-if="userStore.isLoggedIn">
          <template v-if="userStore.isRider">
            <router-link to="/rider/home">📋 订单大厅</router-link>
            <router-link to="/profile">👤 个人信息</router-link>
          </template>
          <template v-else>
            <router-link to="/user/home">📦 我的订单</router-link>
            <router-link to="/user/place-order">➕ 发布订单</router-link>
            <router-link to="/profile">👤 个人信息</router-link>
          </template>
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
        <template v-if="userStore.isRider">
          <router-link to="/rider/home" @click="menuOpen = false">📋 订单大厅</router-link>
          <router-link to="/profile" @click="menuOpen = false">👤 个人信息</router-link>
        </template>
        <template v-else>
          <router-link to="/user/home" @click="menuOpen = false">📦 我的订单</router-link>
          <router-link to="/user/place-order" @click="menuOpen = false">➕ 发布订单</router-link>
          <router-link to="/profile" @click="menuOpen = false">👤 个人信息</router-link>
        </template>
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
      <template v-if="userStore.isRider">
        <router-link to="/rider/home">📋<span>订单大厅</span></router-link>
        <router-link to="/profile">👤<span>个人信息</span></router-link>
      </template>
      <template v-else>
        <router-link to="/user/home">📦<span>我的订单</span></router-link>
        <router-link to="/user/place-order">➕<span>发布订单</span></router-link>
        <router-link to="/profile">👤<span>个人信息</span></router-link>
      </template>
    </nav>

    <!-- Toast -->
    <div class="toast" v-if="toast.msg" :class="toast.type">
      <span class="toast-icon">{{ toast.type === 'error' ? '⚠️' : '✅' }}</span>
      <span>{{ toast.msg }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'

const router = useRouter()
const userStore = useUserStore()
const menuOpen = ref(false)

function toggleMenu() { menuOpen.value = !menuOpen.value }

function doLogout() {
  userStore.logout()
  menuOpen.value = false
  router.push('/login')
}

// Toast
const toast = reactive({ msg: '', type: 'success' })
window.$toast = (msg, type = 'error') => {
  toast.msg = msg
  toast.type = type
  setTimeout(() => (toast.msg = ''), 3000)
}
</script>

<template>
  <div class="nav-tabs">
    <router-link v-if="userStore.isAdmin" to="/admin/home" class="nav-tab" :class="{ active: route.path === '/admin/home' }">
      👑 管理后台
    </router-link>
    <router-link to="/rider/home" class="nav-tab" :class="{ active: route.path === '/rider/home' }">
      🛵 骑手模式
    </router-link>
    <router-link to="/user/home" class="nav-tab" :class="{ active: route.path === '/user/home' }">
      👤 用户模式
    </router-link>
    <router-link to="/notifications" class="nav-tab" :class="{ active: route.path === '/notifications' }">
      🔔 通知
    </router-link>
    <router-link to="/user/place-order" class="nav-tab" :class="{ active: route.path === '/user/place-order' }">
      ➕ 发布新订单
    </router-link>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
const route = useRoute()
const userStore = useUserStore()
</script>

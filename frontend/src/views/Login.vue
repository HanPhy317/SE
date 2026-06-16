<template>
  <div class="auth-page">
    <img src="/WHU.webp" alt="WHU" class="hero-logo" />
    <h2>校园跑腿平台</h2>
    <p class="subtitle">登录后开始使用</p>
    <form @submit.prevent="handleLogin" class="auth-form">
      <div class="form-group">
        <label>用户名 / 手机号</label>
        <input v-model="form.account" placeholder="请输入用户名或手机号" required />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码" required />
      </div>
      <button class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
    <p class="auth-switch">还没有账号？<router-link to="/register">立即注册</router-link></p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const form = reactive({ account: '', password: '' })

async function handleLogin() {
  loading.value = true
  const res = await userStore.login(form.account, form.password, 'user')
  loading.value = false
  if (res.ok) {
    if (res.data.role === 'admin') {
      router.push('/admin/home')
    } else {
      router.push('/user/home')
    }
  } else {
    window.$toast(res.message || '登录失败')
  }
}
</script>

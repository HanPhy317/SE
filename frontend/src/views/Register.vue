<template>
  <div class="auth-page">
    <span class="hero-icon">✨</span>
    <h2>创建账号</h2>
    <p class="subtitle">注册成为校园跑腿用户</p>
    <form @submit.prevent="handleRegister" class="auth-form">
      <div class="form-group">
        <label>用户名</label>
        <input v-model="form.username" placeholder="请输入用户名" required minlength="2" maxlength="64" />
      </div>
      <div class="form-group">
        <label>手机号</label>
        <input v-model="form.phone" type="tel" placeholder="请输入11位手机号" required pattern="[0-9]{11}" />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="至少6位密码" required minlength="6" />
      </div>
      <button class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>
    <p class="auth-switch">已有账号？<router-link to="/login">立即登录</router-link></p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const form = reactive({ username: '', phone: '', password: '' })

async function handleRegister() {
  loading.value = true
  const res = await userStore.register(form.username, form.phone, form.password)
  loading.value = false
  if (res.ok) {
    router.push('/user/home')
  } else {
    window.$toast(res.message || '注册失败')
  }
}
</script>

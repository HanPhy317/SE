import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isLoggedIn = computed(() => !!token.value)
  const isRider = computed(() => userInfo.value?.role === 'rider')

  async function login(account, password, role = 'user') {
    const res = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ account, password, role }),
    })
    if (res.ok) {
      token.value = res.data.token
      userInfo.value = res.data
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('user', JSON.stringify(res.data))
    }
    return res
  }

  async function register(username, phone, password) {
    const res = await api('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, phone, password }),
    })
    if (res.ok) {
      token.value = res.data.token
      userInfo.value = res.data
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('user', JSON.stringify(res.data))
    }
    return res
  }

  async function fetchProfile() {
    const res = await api('/auth/profile')
    if (res.ok) {
      userInfo.value = { ...userInfo.value, ...res.data }
      localStorage.setItem('user', JSON.stringify(userInfo.value))
    }
    return res
  }

  async function becomeRider(serviceArea) {
    const res = await api('/auth/become_rider', {
      method: 'POST',
      body: JSON.stringify({ service_area: serviceArea }),
    })
    if (res.ok) {
      userInfo.value = {
        ...userInfo.value,
        role: 'rider',
        rider: { rider_id: res.data.rider_id, service_area: res.data.service_area },
      }
      localStorage.setItem('user', JSON.stringify(userInfo.value))
    }
    return res
  }

  async function updateProfile(data) {
    const res = await api('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
    if (res.ok) {
      userInfo.value = { ...userInfo.value, ...res.data }
      localStorage.setItem('user', JSON.stringify(userInfo.value))
    }
    return res
  }

  async function topup(amount) {
    const res = await api('/auth/topup', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    })
    if (res.ok) {
      userInfo.value = { ...userInfo.value, balance: res.data.balance }
      localStorage.setItem('user', JSON.stringify(userInfo.value))
    }
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, userInfo, isLoggedIn, isRider, login, register, fetchProfile, becomeRider, updateProfile, topup, logout }
})

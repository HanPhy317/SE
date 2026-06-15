import { createRouter, createWebHashHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import UserHome from '../views/UserHome.vue'
import PlaceOrder from '../views/PlaceOrder.vue'
import RiderHome from '../views/RiderHome.vue'
import AcceptOrder from '../views/AcceptOrder.vue'
import Profile from '../views/Profile.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/user/home', component: UserHome, meta: { requiresAuth: true } },
  { path: '/user/place-order', component: PlaceOrder, meta: { requiresAuth: true } },
  { path: '/rider/home', component: RiderHome, meta: { requiresAuth: true } },
  { path: '/rider/accept/:id', component: AcceptOrder, meta: { requiresAuth: true }, props: true },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router

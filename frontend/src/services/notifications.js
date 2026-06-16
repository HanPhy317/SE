let socket = null
let activeToken = ''
let reconnectTimer = null
const MAX_NOTIFICATIONS = 80

function currentUserId() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')?.user_id ?? 'guest'
  } catch {
    return 'guest'
  }
}

function storageKey() {
  return `campus_notifications_${currentUserId()}`
}

function emitStoreUpdated() {
  window.dispatchEvent(new CustomEvent('notification-store-updated'))
}

export function getNotifications() {
  try {
    const raw = localStorage.getItem(storageKey())
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveNotifications(items) {
  localStorage.setItem(storageKey(), JSON.stringify(items.slice(0, MAX_NOTIFICATIONS)))
  emitStoreUpdated()
}

export function unreadNotificationCount() {
  return getNotifications().filter((item) => !item.read).length
}

export function markNotificationRead(id) {
  saveNotifications(getNotifications().map((item) => (
    item.id === id ? { ...item, read: true } : item
  )))
}

export function markAllNotificationsRead() {
  saveNotifications(getNotifications().map((item) => ({ ...item, read: true })))
}

export function clearNotifications() {
  saveNotifications([])
}

function storeNotification(notification) {
  const item = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    read: false,
    received_at: new Date().toISOString(),
    ...notification,
  }
  saveNotifications([item, ...getNotifications()])
}

function websocketUrl(token) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws/notifications?token=${encodeURIComponent(token)}`
}

function connect(token) {
  if (!token || token === activeToken && socket?.readyState <= WebSocket.OPEN) return

  socket?.close()
  activeToken = token
  socket = new WebSocket(websocketUrl(token))

  socket.onmessage = (event) => {
    const notification = JSON.parse(event.data)
    storeNotification(notification)
    window.$toast?.(notification.message, 'success')
    window.dispatchEvent(new CustomEvent('order-notification', { detail: notification }))
  }

  socket.onclose = () => {
    socket = null
    if (localStorage.getItem('token') === activeToken) {
      clearTimeout(reconnectTimer)
      reconnectTimer = setTimeout(() => connect(activeToken), 3000)
    }
  }
}

export function startNotifications() {
  setInterval(() => {
    const token = localStorage.getItem('token') || ''
    if (!token) {
      activeToken = ''
      socket?.close()
      socket = null
      return
    }
    connect(token)
  }, 1000)
}

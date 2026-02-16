import { defineNuxtRouteMiddleware, navigateTo } from '#app'
import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async (to) => {
  if (process.server) return

  const auth = useAuthStore()
  
  if (!auth.isAuth) {
    await auth.init()
  }

  if (to.path === '/login') {
    if (auth.isAuth) {
      return window.location.href = '/profile'
    }
    return
  }

  if (!auth.isAuth) {
    return window.location.href = '/login'
  }
})
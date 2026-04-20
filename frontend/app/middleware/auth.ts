import { defineNuxtRouteMiddleware, navigateTo } from '#app'
import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const auth = useAuthStore()
  
  if (!auth.isAuth) {
    await auth.init()
  }

  if (to.path === '/login') {
    if (auth.isAuth) {
      if (auth.user?.id) {
        return navigateTo(`/profile/${auth.user.id}`)
      }
      return navigateTo('/')
    }
    return
  }

  if (!auth.isAuth) {
    return navigateTo('/login')
  }
})
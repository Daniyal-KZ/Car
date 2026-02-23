export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  await auth.init()

  const allowed = to.meta.roles as string[] | undefined
  if (!allowed) return

  if (!auth.isAuth) return navigateTo('/login')

  const role = auth.user?.role
  if (!role || !allowed.includes(role)) {
    return navigateTo('/403')
  }
})
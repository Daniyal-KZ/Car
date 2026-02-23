export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  if (!authStore.user) return navigateTo('/login')

  const requiredRole = to.path.startsWith('/admin') ? 'admin' : 'user'
  if (authStore.user.role !== requiredRole && authStore.user.role !== 'dev') {
    return navigateTo('/403')
  }
})</content>
<parameter name="filePath">d:\Projects\Car\frontend\middleware\role.ts
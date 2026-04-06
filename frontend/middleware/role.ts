export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  if (!authStore.user) return navigateTo('/login')

  const isAdminRoute = to.path.startsWith('/admin')
  const isUserRoute = to.path.startsWith('/user')

  if (isAdminRoute && authStore.user.role !== 'admin' && authStore.user.role !== 'dev') {
    return navigateTo('/403')
  }

  if (isUserRoute && authStore.user.role !== 'user' && authStore.user.role !== 'dev') {
    return navigateTo('/403')
  }

  // backwards compatibility adjusted for active routes
  if (!isAdminRoute && !isUserRoute && (to.path.startsWith('/assistant') || to.path.startsWith('/profile') || to.path === '/')) {
    return
  }

  if (!isAdminRoute && !isUserRoute) {
    // protects routes not in new scheme, default to role check
    if (authStore.user.role === 'admin' || authStore.user.role === 'dev') return
    if (authStore.user.role === 'user') return
    return navigateTo('/403')
  }
})</content>
<parameter name="filePath">d:\Projects\Car\frontend\middleware\role.ts
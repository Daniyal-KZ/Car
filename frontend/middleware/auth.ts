export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  if (!authStore.token) {
    return navigateTo('/login')
  }
})</content>
<parameter name="filePath">d:\Projects\Car\frontend\middleware\auth.ts
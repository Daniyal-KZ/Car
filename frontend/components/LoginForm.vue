<template>
  <div class="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Вход</h2>
    <form @submit.prevent="login" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">Имя пользователя</label>
        <input
          v-model="username"
          type="text"
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Пароль</label>
        <input
          v-model="password"
          type="password"
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
      <button
        type="submit"
        :disabled="loading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
      >
        {{ loading ? 'Вход...' : 'Войти' }}
      </button>
    </form>
    <p v-if="error" class="mt-4 text-red-600 text-center">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const authStore = useAuthStore()

const login = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: new URLSearchParams({
        username: username.value,
        password: password.value
      })
    })
    authStore.setToken(response.access_token)
    // Декодируем токен для получения user info (упрощенно)
    const payload = JSON.parse(atob(response.access_token.split('.')[1]))
    authStore.setUser({ id: payload.user_id, role: payload.role })
    await navigateTo('/user/garage')
  } catch (err: any) {
    error.value = err.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>
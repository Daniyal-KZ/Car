<template>
  <form @submit.prevent="submitLogin" class="w-full max-w-sm space-y-6 p-8 rounded-2xl bg-white shadow-xl">
    <h1 class="text-center mb-6 text-xl">Sign in to your account</h1>

    <div v-if="errorText" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ errorText }}
    </div>

    <div class="space-y-2">
      <label class="block text-sm font-medium text-gray-700">Username</label>
      <input
        v-model="username"
        type="text"
        placeholder="Enter your username"
        class="w-full rounded-xl border border-gray-300 px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 placeholder:text-gray-400"
      />
    </div>

    <div class="space-y-2">
      <label class="block text-sm font-medium text-gray-700">Password</label>
      <input
        v-model="password"
        type="password"
        placeholder="Enter your password"
        class="w-full rounded-xl border border-gray-300 px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 placeholder:text-gray-400"
      />
    </div>

    <button
      type="submit"
      :disabled="loading"
      class="w-full rounded-xl bg-gradient-to-r from-gray-900 to-black text-white py-3.5 font-medium hover:opacity-90 active:scale-[0.99] transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-60"
    >
      {{ loading ? 'Signing in...' : 'Sign In' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

const username = ref('')
const password = ref('')
const errorText = ref<string | null>(null)
const loading = ref(false)

const auth = useAuthStore()

const submitLogin = async () => {
  errorText.value = null
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    await navigateTo('/')
  } catch (err: any) {
    errorText.value = err?.message || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>
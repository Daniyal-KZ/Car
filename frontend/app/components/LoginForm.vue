<template>
  <form
    @submit.prevent="submitLogin"
    class="w-full max-w-sm space-y-6 p-8 rounded-2xl
    bg-card dark:bg-card-dark
    text-text dark:text-text-dark
    shadow-xl dark:shadow-black/40"
  >
    <h1 class="text-center mb-6 text-xl font-semibold">
      Sign in to your account
    </h1>

    <div
      v-if="errorText"
      class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700
      dark:border-red-800 dark:bg-red-900/30 dark:text-red-300"
    >
      {{ errorText }}
    </div>

    <!-- Username -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-text-muted dark:text-text-dark">
        Username
      </label>
      <input
        v-model="username"
        type="text"
        placeholder="Enter your username"
        class="w-full rounded-xl border
        border-border dark:border-border-dark
        bg-bg dark:bg-bg-dark
        text-text dark:text-text-dark
        placeholder:text-text-muted
        px-4 py-3.5
        focus:outline-none focus:ring-2 focus:ring-blue-500
        transition-all duration-200"
      />
    </div>

    <!-- Password -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-text-muted dark:text-text-dark">
        Password
      </label>
      <input
        v-model="password"
        type="password"
        placeholder="Enter your password"
        class="w-full rounded-xl border
        border-border dark:border-border-dark
        bg-bg dark:bg-bg-dark
        text-text dark:text-text-dark
        placeholder:text-text-muted
        px-4 py-3.5
        focus:outline-none focus:ring-2 focus:ring-blue-500
        transition-all duration-200"
      />
    </div>

    <button
      type="submit"
      :disabled="loading"
      class="w-full rounded-xl
      bg-gradient-to-r from-gray-900 to-black
      dark:from-gray-100 dark:to-white
      text-white dark:text-black
      py-3.5 font-medium
      hover:opacity-90 active:scale-[0.99]
      transition-all duration-200
      shadow-lg hover:shadow-xl
      disabled:opacity-60"
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
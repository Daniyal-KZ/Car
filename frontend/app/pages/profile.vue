<template>
  <div class="h-screen flex flex-col items-center justify-center bg-gray-900 gap-4 p-8">
    <h1 class="text-6xl font-bold text-white">안녕하세요 — Hello in Korean</h1>
    <p class="text-xl text-yellow-400 font-medium">Tailwind + Nuxt + Noto Sans KR</p>

    <div v-if="auth.isAuth" class="text-white text-2xl flex flex-col items-center gap-4">
      <NuxtLink to="/garage" class="hover:underline">
        {{ auth.user.username }} — роль: {{ auth.user.role }}
      </NuxtLink>
      
      <button
        @click="handleLogout"
        class="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl transition"
      >
        Выйти
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const auth = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push('/login') // после выхода отправляем на логин
}
</script>
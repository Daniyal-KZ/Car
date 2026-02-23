<script setup lang="ts">
definePageMeta({
  middleware: ['auth', 'role'],
})
const router = useRouter()
const auth = useAuthStore()

const logout = () => {
  router.push('/login')
  auth.logout()

}
</script>

<template>
  <button @click="logout" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm transition">
    Выйти
  </button>
</template>

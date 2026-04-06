<script setup lang="ts">
import { onMounted } from 'vue'
const auth = useAuthStore()

onMounted(() => {
  auth.init()
  const theme = localStorage.getItem('theme') || 'light'
  document.documentElement.classList.toggle('dark', theme === 'dark')
})

</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
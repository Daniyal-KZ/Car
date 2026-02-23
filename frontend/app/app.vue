<script setup lang="ts">
const auth = useAuthStore()
onMounted(() => {
  auth.init()
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
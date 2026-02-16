<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const auth = useAuthStore()
const config = useRuntimeConfig()

// ТОЛЬКО ТАК РАБОТАЕТ - через хелпер
const { data: cars, refresh } = await useAsyncData('cars_' + Date.now(), async () => {
  return await $fetch(`${config.public.apiBase}/cars`, {
    headers: {
      Authorization: `Bearer ${auth.token}`
    }
  })
}, {
  server: false // грузим только на клиенте
})
</script>

<template>
  <div>
    <h1>Гараж {{ auth.user?.username }}</h1>
    <div v-if="cars?.length">
      <div v-for="car in cars" :key="car.id">
        {{ car.brand }} {{ car.model }} ({{ car.year }})
      </div>
    </div>
    <div v-else>
      Нет машин
    </div>
  </div>
</template>
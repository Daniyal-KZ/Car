<script setup lang="ts">
const config = useRuntimeConfig()
const { data } = await useFetch(`${config.public.apiBase}/users`)
</script>

<template>
  <div class="h-screen flex flex-col items-center justify-center bg-gray-900 gap-4 p-8">
    <h1 class="text-6xl font-bold text-white">안녕하세요 — Hello in Korean</h1>
    <p class="text-xl text-yellow-400 font-medium">Tailwind + Nuxt + Noto Sans KR</p>

    <div v-if="data && data.length > 0" class="text-white text-2xl">
      Hello, {{ data[0].username }} — роль: {{ data[0].role }}
    </div>
  </div>
</template>

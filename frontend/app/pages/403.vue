<script lang="ts">
  definePageMeta({
  layout: false
})
</script>

<template>
  <div class="min-h-screen bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-gray-900 text-text dark:text-text-dark dark:text-text dark:text-text-dark flex items-center justify-center p-8">
    <div class="max-w-md text-center">
      <h1 class="text-4xl font-bold">403</h1>
      <p class="mt-3 text-gray-300">У Вас нет доступа к этой странице.</p>
      <NuxtLink to="/" class="inline-block mt-6 px-6 py-3 bg-bg dark:bg-bg-dark dark:bg-bg text-black dark:text-text-dark dark:text-text rounded-xl">
        На главную
      </NuxtLink>
    </div>
  </div>
</template>
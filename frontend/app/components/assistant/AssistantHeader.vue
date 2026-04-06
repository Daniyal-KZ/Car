<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<template>
  <header class="flex items-center justify-between border-b border-border bg-bg dark:bg-bg-dark px-5 py-4 dark:border-border-dark">
    <div>
      <h1 class="text-lg font-semibold text-text dark:text-text-dark\">
        {{ title || "ИИ ассистент" }}
      </h1>
      <p class="text-sm text-text-muted dark:text-text-muted dark:text-text-muted">
        Помощник по диагностике, обслуживанию и ремонту
      </p>
    </div>
  </header>
</template>
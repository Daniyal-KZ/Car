<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  hint?: string
}>()
</script>

<template>
  <div class="rounded-2xl border border-border bg-bg dark:bg-bg-dark dark:bg-bg p-4 dark:border-border dark:border-border-dark dark:bg-bg-dark/">
    <p class="text-sm text-text-muted dark:text-text-muted dark:text-text-muted">
      {{ label }}
    </p>
    <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">
      {{ value }}
    </p>
    <p v-if="hint" class="mt-2 text-xs text-text dark:text-slate-300 dark:text-text-muted dark:text-text-muted">
      {{ hint }}
    </p>
  </div>
</template>
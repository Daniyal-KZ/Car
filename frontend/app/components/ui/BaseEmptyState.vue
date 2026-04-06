<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div
    class="rounded-3xl border border-dashed border-slate-300 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ px-6 py-12 text-center dark:border-border dark:border-slate-700"
  >
    <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">
      {{ title }}
    </h3>
    <p v-if="description" class="mx-auto mt-2 max-w-xl text-sm text-text-muted dark:text-text-muted dark:text-text-muted">
      {{ description }}
    </p>

    <div v-if="$slots.default" class="mt-5 flex justify-center">
      <slot />
    </div>
  </div>
</template>
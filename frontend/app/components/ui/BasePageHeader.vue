<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
    <div>
      <h1 class="text-3xl font-bold tracking-tight text-text dark:text-text-dark dark:text-text dark:text-text-dark">
        {{ title }}
      </h1>
      <p
        v-if="description"
        class="mt-2 max-w-3xl text-sm leading-6 text-text-muted dark:text-text-muted"
      >
        {{ description }}
      </p>
    </div>

    <div v-if="$slots.actions" class="flex items-center gap-3">
      <slot name="actions" />
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
}>()
</script>

<template>
  <section
    class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 shadow-[0_10px_30px_rgba(0,0,0,0.25)]"
  >
    <div v-if="title || subtitle" class="mb-5">
      <h2 v-if="title" class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">
        {{ title }}
      </h2>
      <p v-if="subtitle" class="mt-1 text-sm text-text-muted dark:text-text-muted">
        {{ subtitle }}
      </p>
    </div>

    <slot />
  </section>
</template>
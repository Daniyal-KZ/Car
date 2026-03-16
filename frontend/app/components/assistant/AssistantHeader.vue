<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>

<template>
  <header class="flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-4">
    <div>
      <h1 class="text-lg font-semibold text-zinc-900">
        {{ title || "Assistant" }}
      </h1>
      <p class="text-sm text-zinc-500">
        Тест
      </p>
    </div>
  </header>
</template>

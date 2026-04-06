<template>
  <div class="h-screen flex flex-col bg-bg dark:bg-bg-dark text-text dark:text-text-dark overflow-hidden">

    <AppHeader />

    <div class="flex flex-1 min-h-0">
      <AssistantSidebar />

      <main class="flex-1 min-w-0 overflow-y-auto px-4 py-6">
        <slot />
      </main>
    </div>

  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/layout/AppHeader.vue'
import AssistantSidebar from '~/components/assistant/AssistantSidebar.vue'
</script>
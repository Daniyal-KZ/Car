<template>
  <div class="min-h-screen flex flex-col bg-bg dark:bg-bg-dark dark:bg-bg text-text dark:text-text-dark dark:text-text">
    <AppHeader />

    <main class="flex-1 px-4 py-6">
      <slot />
    </main>

    <Footer />
  </div>
</template>



<script setup lang="ts">
import AppHeader from '~/components/layout/AppHeader.vue'
import Footer from '~/components/Footer.vue'
</script>
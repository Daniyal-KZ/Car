<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray">
    <LoginForm />
  </div>
</template>

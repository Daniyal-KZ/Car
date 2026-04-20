<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

onMounted(() => {
  navigateTo('/assistant')
})
</script>

<template>
  <div />
</template>
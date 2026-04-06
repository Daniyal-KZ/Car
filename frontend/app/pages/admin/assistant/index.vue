<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const { createChat } = useAssistant()

onMounted(() => {
  const chat = createChat()
  navigateTo(`/admin/assistant/${chat.id}`)
})
</script>

<template>
  <div />
</template>
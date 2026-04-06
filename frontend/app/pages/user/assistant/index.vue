<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const { createChat } = useAssistant()

onMounted(() => {
  const chat = createChat()
  navigateTo(`/user/assistant/${chat.id}`)
})
</script>

<template>
  <div />
</template>
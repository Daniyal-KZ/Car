<script setup lang="ts">
definePageMeta({ layout: 'assistant' })

const auth = useAuthStore()
const { createChat, fetchChats, sortedChats } = useAssistant()

onMounted(() => {
  if (!auth.user) {
    navigateTo('/login')
    return
  }

  void (async () => {
    await fetchChats()
    const existingChat = sortedChats.value[0]
    const chat = existingChat ?? await createChat()

    if (auth.user?.role === 'admin' || auth.user?.role === 'dev') {
      navigateTo(`/admin/assistant/${chat.id}`)
    } else {
      navigateTo(`/user/assistant/${chat.id}`)
    }
  })()
})
</script>

<template>
  <div />
</template>

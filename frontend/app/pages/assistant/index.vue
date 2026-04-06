<script setup lang="ts">
definePageMeta({ layout: 'assistant' })

const auth = useAuthStore()
const { createChat } = useAssistant()

onMounted(() => {
  if (!auth.user) {
    navigateTo('/login')
    return
  }

  const chat = createChat()

  if (auth.user.role === 'admin' || auth.user.role === 'dev') {
    navigateTo(`/admin/assistant/${chat.id}`)
  } else {
    navigateTo(`/user/assistant/${chat.id}`)
  }
})
</script>

<template>
  <div />
</template>

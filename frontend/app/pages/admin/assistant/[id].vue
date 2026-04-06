<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const router = useRouter()
const { getChatById, createChat } = useAssistant()

const chatId = computed(() => String(route.params.id || ""))
const chat = computed(() => getChatById(chatId.value))

onMounted(() => {
  if (!chat.value) {
    const newChat = createChat()
    router.replace(`/admin/assistant/${newChat.id}`)
  }
})
</script>

<template>
  <div class="flex h-[calc(100vh-140px)] overflow-hidden rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/">
    <AssistantSidebar />

    <div class="flex min-w-0 flex-1 flex-col">
      <AssistantHeader :title="chat?.title || 'ИИ ассистент'" />

      <template v-if="chat">
        <AssistantWelcome v-if="chat.messages.length === 0" />
        <AssistantMessages v-else :chat="chat" />
        <AssistantInput :chat-id="chat.id" />
      </template>
    </div>
  </div>
</template>
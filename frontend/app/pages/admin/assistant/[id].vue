<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { loadChat, createChat, chats, activeChat } = useAssistant()

const chatId = computed(() => String(route.params.id || ""))
const chat = computed(() => {
  // First check chats list
  const found = chats.value.find((item) => item.id === chatId.value)
  if (found) return found
  // Then check activeChat
  if (activeChat.value?.id === chatId.value) return activeChat.value
  return undefined
})

const ensureCurrentChat = async () => {
  if (!chatId.value) return
  try {
    await loadChat(chatId.value)
  } catch {
    await router.replace('/assistant')
  }
}

onMounted(() => {
  void ensureCurrentChat()
})

watch(chatId, () => {
  void ensureCurrentChat()
})
</script>

<template>
  <div class="flex h-[calc(100vh-140px)] overflow-hidden rounded-3xl border border-border bg-bg dark:border-border-dark dark:bg-bg-dark">
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
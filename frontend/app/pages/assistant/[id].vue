<script setup lang="ts">
definePageMeta({
  layout: "assistant"
})

const route = useRoute()
const router = useRouter()

const { getChatById, createChat } = useAssistant()

const chatId = computed(() => String(route.params.id || ""))

const chat = computed(() => getChatById(chatId.value))

onMounted(() => {

  if (!chat.value) {

    const newChat = createChat()

    router.replace(`/assistant/${newChat.id}`)

  }

})
</script>

<template>

<AssistantHeader :title="chat?.title || 'Assistant'" />

<template v-if="chat">

  <AssistantWelcome v-if="chat.messages.length === 0" />

  <AssistantMessages
    v-else
    :chat="chat"
  />

  <AssistantInput :chat-id="chat.id" />

</template>

</template>

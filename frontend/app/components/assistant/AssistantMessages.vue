<script setup lang="ts">
import type { Chat } from "@/composables/useAssistant";

const props = defineProps<{
  chat: Chat;
}>();

const containerRef = ref<HTMLElement | null>(null);

const scrollToBottom = async () => {
  await nextTick();
  if (!containerRef.value) return;
  containerRef.value.scrollTop = containerRef.value.scrollHeight;
};

watch(
  () => props.chat.messages.length,
  async () => {
    await scrollToBottom();
  },
  { immediate: true }
);
</script>

<template>
  <div ref="containerRef" class="flex-1 overflow-y-auto bg-zinc-50 px-6 py-6">
    <div class="mx-auto flex max-w-4xl flex-col gap-4">
      <AssistantMessageItem
        v-for="message in chat.messages"
        :key="message.id"
        :message="message"
      />
    </div>
  </div>
</template>

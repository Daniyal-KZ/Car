<script setup lang="ts">
import type { Message } from "@/composables/useAssistant";

defineProps<{
  message: Message;
}>();

const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
};
</script>

<template>
  <div
    class="flex w-full"
    :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
  >
    <div
      class="max-w-[80%] rounded-2xl px-4 py-3 shadow-sm"
      :class="
        message.role === 'user'
          ? 'bg-zinc-900 text-white'
          : 'border border-zinc-200 bg-white text-zinc-900'
      "
    >
      <p class="whitespace-pre-wrap break-words text-sm leading-6">
        {{ message.content }}
      </p>

      <div
        class="mt-2 text-[11px]"
        :class="message.role === 'user' ? 'text-zinc-300' : 'text-zinc-400'"
      >
        {{ formatTime(message.createdAt) }}
      </div>
    </div>
  </div>
</template>

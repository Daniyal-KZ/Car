<script setup lang="ts">
import type { Message } from "@/composables/useAssistant"

defineProps<{
  message: Message
}>()

const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  })
}
</script>

<template>
  <div
    class="flex w-full"
    :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
  >
    <div
      class="max-w-[85%] rounded-2xl px-4 py-3 shadow-sm"
      :class="message.role === 'user' ? 'bg-cyan-400 text-slate-950' : 'border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark text-text dark:text-text-dark dark:text-text dark:text-text-dark'"
    >
      <p class="whitespace-pre-wrap break-words text-sm leading-6">
        {{ message.content }}
      </p>

      <div
  class="mt-2 text-[11px]"
  :class="message.role === 'user'
    ? 'text-text dark:text-text-muted dark:text-text-muted'
    : 'text-slate-400 dark:text-slate-500'"
>
  {{ formatTime(message.createdAt) }}
</div>
    </div>
  </div>
</template>
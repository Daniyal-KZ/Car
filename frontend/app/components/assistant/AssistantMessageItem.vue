<script setup lang="ts">
import type { AssistantAction, Message } from "@/composables/useAssistant"

const props = defineProps<{
  message: Message
}>()

const { parseAction } = useAssistant()

const action = computed<AssistantAction | null>(() => parseAction(props.message.actionJson))

const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  })
}

const openAction = async () => {
  if (!action.value?.route) return
  await navigateTo(action.value.route)
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

      <button
        v-if="action?.route"
        class="mt-3 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-xs font-medium text-cyan-200 transition hover:bg-cyan-500/20"
        @click="openAction"
      >
        {{ action.label || 'Открыть' }}
      </button>

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
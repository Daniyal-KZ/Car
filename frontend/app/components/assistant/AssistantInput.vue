<script setup lang="ts">
const props = defineProps<{
  chatId: string
}>()

const { sendMessage } = useAssistant()

const message = ref("")
const isSending = ref(false)

const handleSend = async () => {
  const text = message.value.trim()
  if (!text || isSending.value) return

  isSending.value = true

  try {
    await sendMessage(props.chatId, text)
    message.value = ""
  } finally {
    isSending.value = false
  }
}
</script>

<template>
  <div class="border-t border-border bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ px-4 py-4 sm:px-6 dark:border-border dark:border-border-dark">
    <div class="mx-auto max-w-4xl">
      <div
        class="flex items-end gap-3 rounded-2xl border border-border bg-bg dark:bg-bg-dark dark:bg-bg px-3 py-3 shadow-sm dark:border-border dark:border-slate-700 dark:bg-card-dark"
      >
        <textarea
          v-model="message"
          rows="1"
          placeholder="Напиши сообщение..."
          class="min-h-[40px] max-h-32 flex-1 resize-none bg-bg dark:bg-bg-dark dark:bg-bg text-sm text-text dark:text-slate-300 outline-none placeholder:text-text-muted dark:text-text-muted dark:bg-card-dark dark:text-text dark:text-text-dark dark:text-text-dark dark:placeholder:text-text"
          @keydown.enter.exact.prevent="handleSend"
        />

        <button
          class="h-[46px] rounded-xl bg-cyan-500 px-4 text-sm font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="!message.trim() || isSending"
          @click="handleSend"
        >
          {{ isSending ? "..." : "Отправить" }}
        </button>
      </div>
    </div>
  </div>
</template>
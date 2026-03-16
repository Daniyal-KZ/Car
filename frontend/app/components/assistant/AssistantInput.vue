<script setup lang="ts">
const props = defineProps<{
  chatId: string;
}>();

const { sendMessage } = useAssistant();

const message = ref("");
const isSending = ref(false);

const handleSend = async () => {
  const text = message.value.trim();
  if (!text || isSending.value) return;

  isSending.value = true;

  try {
    await sendMessage(props.chatId, text);
    message.value = "";
  } finally {
    isSending.value = false;
  }
};
</script>

<template>
  <div class="border-t border-zinc-200 bg-white px-6 py-4">
    <div class="mx-auto max-w-4xl">
      <div class="flex items-end gap-3 rounded-xl border border-zinc-300 bg-white px-3 py-2 shadow-sm">

        <textarea
          v-model="message"
          rows="1"
          placeholder="Напиши сообщение..."
          class="flex-1 resize-none bg-transparent text-sm text-zinc-900 outline-none placeholder:text-zinc-400 min-h-[36px] max-h-32"
          @keydown.enter.exact.prevent="handleSend"
        />

        <button
          class="h-[46px] px-4 rounded-lg bg-zinc-900 text-white text-sm font-medium hover:bg-zinc-800 transition disabled:opacity-50"
          :disabled="!message.trim() || isSending"
          @click="handleSend"
        >
          {{ isSending ? "..." : "Send" }}
        </button>

      </div>
    </div>
  </div>
</template>
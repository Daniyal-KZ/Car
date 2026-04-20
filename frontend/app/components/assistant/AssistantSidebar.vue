<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const { sortedChats, createChat, fetchChats, renameChat, deleteChat } = useAssistant()

const assistantBase = computed(() => {
  if (auth.user?.role === "admin" || auth.user?.role === "dev") {
    return "/admin/assistant"
  }
  return "/user/assistant"
})

onMounted(() => {
  void fetchChats()
})

const handleCreateChat = async () => {
  const chat = await createChat()
  await router.push(`${assistantBase.value}/${chat.id}`)
}

const handleRenameChat = async (chatId: string, currentTitle: string) => {
  const nextTitle = window.prompt("Новое название чата", currentTitle)
  if (!nextTitle || !nextTitle.trim()) return
  await renameChat(chatId, nextTitle.trim())
  await fetchChats()
}

const handleDeleteChat = async (chatId: string) => {
  const confirmed = window.confirm("Удалить этот чат и всю историю сообщений?")
  if (!confirmed) return
  await deleteChat(chatId)
  await fetchChats()
  if (String(route.params.id || "") === chatId) {
    await router.push(assistantBase.value)
  }
}
</script>

<template>
  <aside class="flex h-full w-[300px] flex-col border-r border-border bg-bg dark:bg-bg-dark text-text dark:text-text-dark dark:border-border-dark">
    <div class="border-b border-border p-4 dark:border-border dark:border-border-dark">
      <button
        class="flex w-full items-center justify-center rounded-2xl bg-cyan-500 px-4 py-3 text-sm font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark transition hover:bg-cyan-400 dark:bg-cyan-500"
        @click="handleCreateChat"
      >
        + Новый чат
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-3">
      <div class="mb-3 px-2 text-xs uppercase tracking-wide text-text dark:text-slate-300">
        Чаты
      </div>

      <div v-if="sortedChats.length" class="space-y-2">
        <div
          v-for="chat in sortedChats"
          :key="chat.id"
          class="group rounded-2xl border px-3 py-3 text-sm transition"
          :class="route.params.id === chat.id ? 'border-cyan-500/30 bg-cyan-500/10 text-text dark:text-text-dark dark:text-text dark:text-text-dark dark:bg-cyan-600/20' : 'border-border bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ dark:text-slate-300 hover:border-slate-300 hover:bg-bg dark:border-border dark:border-border-dark dark:bg-card-dark/ dark:hover:border-border dark:border-slate-700 dark:hover:bg-bg dark:bg-card-dark dark:hover:text-text dark:text-text-dark'"
          role="button"
          tabindex="0"
          @click="router.push(`${assistantBase}/${chat.id}`)"
          @keydown.enter.prevent="router.push(`${assistantBase}/${chat.id}`)"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <div class="truncate font-medium">
                {{ chat.title }}
              </div>
              <div class="mt-1 truncate text-xs text-text dark:text-slate-300">
                {{ chat.messagesCount }} сообщений
              </div>
            </div>

            <div class="flex shrink-0 gap-1 opacity-0 transition group-hover:opacity-100">
              <button
                class="rounded-lg border border-border px-2 py-1 text-[11px] text-text-muted hover:border-cyan-400 hover:text-cyan-300 dark:border-border-dark dark:text-text-muted"
                @click.prevent="handleRenameChat(chat.id, chat.title)"
              >
                Переименовать
              </button>
              <button
                class="rounded-lg border border-border px-2 py-1 text-[11px] text-text-muted hover:border-red-400 hover:text-red-300 dark:border-border-dark dark:text-text-muted"
                @click.prevent="handleDeleteChat(chat.id)"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else
        class="rounded-2xl border border-dashed border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4 text-sm text-text dark:text-slate-300"
      >
        Пока нет чатов
      </div>
    </div>
  </aside>
</template>
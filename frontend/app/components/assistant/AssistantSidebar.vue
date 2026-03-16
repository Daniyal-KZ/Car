<script setup lang="ts">
const route = useRoute();
const router = useRouter();

const { sortedChats, createChat } = useAssistant();

const handleCreateChat = () => {
  const chat = createChat();
  router.push(`/assistant/${chat.id}`);
};
</script>

<template>
  <aside class="flex h-screen w-[280px] flex-col border-r border-zinc-800 bg-zinc-950 text-white">
    <div class="border-b border-zinc-800 p-4">
      <button
        class="flex w-full items-center justify-center rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-3 text-sm font-medium transition hover:bg-zinc-800"
        @click="handleCreateChat"
      >
        + New chat
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-3">
      <div class="mb-3 px-2 text-xs uppercase tracking-wide text-zinc-500">
        Chats
      </div>

      <div v-if="sortedChats.length" class="space-y-2">
        <NuxtLink
          v-for="chat in sortedChats"
          :key="chat.id"
          :to="`/assistant/${chat.id}`"
          class="block rounded-xl px-3 py-3 text-sm transition"
          :class="
            route.params.id === chat.id
              ? 'bg-zinc-800 text-white'
              : 'text-zinc-300 hover:bg-zinc-900 hover:text-white'
          "
        >
          <div class="truncate font-medium">
            {{ chat.title }}
          </div>
          <div class="mt-1 truncate text-xs text-zinc-500">
            {{ chat.messages.length }} messages
          </div>
        </NuxtLink>
      </div>

      <div
        v-else
        class="rounded-xl border border-dashed border-zinc-800 p-4 text-sm text-zinc-500"
      >
        Пока нет чатов
      </div>
    </div>
  </aside>
</template>

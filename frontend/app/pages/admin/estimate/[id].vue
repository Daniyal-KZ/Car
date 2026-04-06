<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const parts = [
  { name: "Передний бампер", qty: 1, price: "85 000 ₸" },
  { name: "Крепления", qty: 1, price: "8 000 ₸" },
  { name: "Покраска элемента", qty: 1, price: "35 000 ₸" },
]
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Смета E-{{ route.params.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Смета по ремонту</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/admin/estimate')"
      >
        Назад
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-3">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Toyota Camry 70</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Клиент</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Daniyal</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Статус</p>
        <p class="mt-2 font-semibold text-cyan-300">Черновик</p>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.35fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Состав сметы</h2>

        <div class="mt-5 space-y-3">
          <div
            v-for="part in parts"
            :key="part.name"
            class="grid gap-3 rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4 md:grid-cols-[1.6fr_0.4fr_0.6fr]"
          >
            <div class="font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ part.name }}</div>
            <div class="text-sm text-text dark:text-text-dark dark:text-slate-300">x{{ part.qty }}</div>
            <div class="text-sm text-text dark:text-text-dark dark:text-slate-300">{{ part.price }}</div>
          </div>
        </div>

        <div class="mt-6">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Комментарий мастера</label>
          <textarea
            rows="6"
            placeholder="Комментарий по ремонту..."
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />
        </div>
      </div>

      <div class="space-y-6">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Итоги</h2>

          <div class="mt-5 space-y-4">
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Работы</p>
              <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">55 000 ₸</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Запчасти</p>
              <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">93 000 ₸</p>
            </div>

            <div class="rounded-2xl border border-cyan-500/30 bg-cyan-500/10 p-4">
              <p class="text-sm text-cyan-200">Итого</p>
              <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">148 000 ₸</p>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Действия</h2>

          <div class="mt-5 space-y-3">
            <button class="w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
              Сохранить смету
            </button>
            <button class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300">
              Отправить клиенту
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
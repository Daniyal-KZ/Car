<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const items = [
  {
    id: 201,
    code: "F-201",
    car: "Toyota Camry 70",
    date: "18.03.2026",
    description: "Царапина и вмятина на бампере",
    status: "В обработке",
  },
  {
    id: 202,
    code: "F-202",
    car: "Hyundai Elantra",
    date: "12.03.2026",
    description: "Повреждение двери",
    status: "Готово",
  },
]

const openItem = (id: number) => navigateTo(`/user/damages/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Повреждения</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Все ваши заявки на осмотр повреждений и результаты оценки.
        </p>
      </div>

      <button
        class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        @click="navigateTo('/user/damages/new')"
      >
        + Новая заявка
      </button>
    </div>

    <div class="space-y-4">
      <button
        v-for="item in items"
        :key="item.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400"
        @click="openItem(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.code }} — {{ item.car }}</h2>
              <span class="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                {{ item.status }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Дата: {{ item.date }}</p>
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ item.description }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
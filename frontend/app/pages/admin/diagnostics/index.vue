<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const requests = [
  {
    id: 101,
    code: "D-101",
    client: "Daniyal",
    car: "Toyota Camry 70",
    year: 2021,
    symptom: "Стук в подвеске на неровностях",
    date: "19.03.2026",
    status: "Новая",
  },
  {
    id: 102,
    code: "D-102",
    client: "Ayan",
    car: "Hyundai Elantra",
    year: 2020,
    symptom: "Горит Check Engine",
    date: "18.03.2026",
    status: "В работе",
  },
  {
    id: 103,
    code: "D-103",
    client: "Nursultan",
    car: "Kia K5",
    year: 2022,
    symptom: "Вибрация после 80 км/ч",
    date: "17.03.2026",
    status: "Ожидает",
  },
]

const openRequest = (id: number) => navigateTo(`/admin/diagnostics/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Диагностика</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Список заявок на диагностику. Нажмите на карточку, чтобы открыть конкретную машину.
      </p>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-3">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Всего заявок</p>
        <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">3</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Новые</p>
        <p class="mt-2 text-2xl font-bold text-cyan-300">1</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">В работе</p>
        <p class="mt-2 text-2xl font-bold text-amber-300">1</p>
      </div>
    </div>

    <div class="space-y-4">
      <button
        v-for="item in requests"
        :key="item.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400 hover:bg-bg dark:bg-card-dark"
        @click="openRequest(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">
                {{ item.code }} — {{ item.car }}
              </h2>
              <span class="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                {{ item.status }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
              Клиент: {{ item.client }} • {{ item.year }} • Дата: {{ item.date }}
            </p>

            <p class="mt-3 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">
              {{ item.symptom }}
            </p>
          </div>

          <div class="text-sm font-medium text-cyan-300">
            Открыть →
          </div>
        </div>
      </button>
    </div>
  </div>
</template>
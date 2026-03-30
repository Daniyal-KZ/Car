<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const items = [
  {
    id: 101,
    code: "D-101",
    car: "Toyota Camry 70",
    date: "19.03.2026",
    symptom: "Стук в подвеске",
    status: "В работе",
  },
  {
    id: 102,
    code: "D-102",
    car: "Hyundai Elantra",
    date: "15.03.2026",
    symptom: "Горит Check Engine",
    status: "Готово",
  },
]

const openItem = (id: number) => navigateTo(`/user/diagnostics/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white">Диагностика</h1>
        <p class="mt-2 text-sm text-slate-400">
          Ваши заявки на диагностику и результаты по каждой машине.
        </p>
      </div>

      <button
        class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        @click="navigateTo('/user/diagnostics/new')"
      >
        + Новая заявка
      </button>
    </div>

    <div class="space-y-4">
      <button
        v-for="item in items"
        :key="item.id"
        class="w-full rounded-2xl border border-slate-800 bg-slate-900/70 p-5 text-left transition hover:border-cyan-400"
        @click="openItem(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-lg font-semibold text-white">{{ item.code }} — {{ item.car }}</h2>
              <span class="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                {{ item.status }}
              </span>
            </div>

            <p class="mt-2 text-sm text-slate-400">Дата: {{ item.date }}</p>
            <p class="mt-3 text-sm text-slate-300">{{ item.symptom }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
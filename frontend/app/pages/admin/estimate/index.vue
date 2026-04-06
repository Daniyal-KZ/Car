<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const estimates = [
  {
    id: 401,
    code: "E-401",
    client: "Daniyal",
    car: "Toyota Camry 70",
    reason: "Ремонт переднего бампера",
    status: "Черновик",
  },
  {
    id: 402,
    code: "E-402",
    client: "Ayan",
    car: "Hyundai Elantra",
    reason: "Замена двери и покраска",
    status: "Отправлено",
  },
]

const openItem = (id: number) => navigateTo(`/admin/estimate/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Расчёт сметы</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Список заявок на смету. Каждая смета открывается на отдельной странице.
      </p>
    </div>

    <div class="space-y-4">
      <button
        v-for="item in estimates"
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

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Клиент: {{ item.client }}</p>
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ item.reason }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
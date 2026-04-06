<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const defects = [
  {
    id: 301,
    code: "F-301",
    client: "Daniyal",
    car: "Toyota Camry 70",
    description: "Царапина и вмятина на переднем бампере",
    status: "Новая",
  },
  {
    id: 302,
    code: "F-302",
    client: "Ayan",
    car: "Hyundai Elantra",
    description: "Повреждение правой двери",
    status: "В работе",
  },
]

const openItem = (id: number) => navigateTo(`/admin/defects/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Детекция дефектов</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Список заявок с повреждениями. Каждая машина открывается отдельно.
      </p>
    </div>

    <div class="space-y-4">
      <button
        v-for="item in defects"
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
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ item.description }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
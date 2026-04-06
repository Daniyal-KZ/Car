<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()

const getEndpoint = computed(() => `${config.public.apiBase}/maintenance-rules/admin/all`)

const { data, pending, error } = useFetch(
  () => getEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [getEndpoint, auth.token],
  }
)

const rules = computed(() => data.value ?? [])

const totalCount = computed(() => rules.value.length)
const activeCount = computed(() => rules.value.filter(rule => rule.status === "active").length)
const draftCount = computed(() => rules.value.filter(rule => rule.status !== "active").length)
const brandsCount = computed(() => new Set(rules.value.map(rule => rule.brand)).size)

const formatMileage = (rule: any) => {
  const parts = []
  if (rule.mileage_from != null) {
    parts.push(`${rule.mileage_from.toLocaleString()} км`)
  }
  if (rule.mileage_to != null) {
    parts.push(`до ${rule.mileage_to.toLocaleString()} км`)
  }
  return parts.length ? parts.join(" — ") : "Любой пробег"
}

const formatYear = (rule: any) => {
  if (rule.year_from && rule.year_to) return `${rule.year_from}–${rule.year_to}`
  if (rule.year_from) return `${rule.year_from}+`
  if (rule.year_to) return `до ${rule.year_to}`
  return "Любой год"
}

const openRule = (id: number) => navigateTo(`/admin/maintenance-rules/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Регламенты ТО</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Список регламентов обслуживания по маркам, моделям и пробегу.
        </p>
      </div>

      <button
        class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        @click="navigateTo('/admin/maintenance-rules/create')"
      >
        + Добавить регламент
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Всего регламентов</p>
        <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ totalCount }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Активные</p>
        <p class="mt-2 text-2xl font-bold text-cyan-300">{{ activeCount }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Черновики</p>
        <p class="mt-2 text-2xl font-bold text-amber-300">{{ draftCount }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Марок</p>
        <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ brandsCount }}</p>
      </div>
    </div>

    <div class="mb-6 grid gap-4 lg:grid-cols-4">
      <input
        type="text"
        placeholder="Марка"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none transition focus:border-cyan-400"
      />

      <input
        type="text"
        placeholder="Модель"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none transition focus:border-cyan-400"
      />

      <input
        type="text"
        placeholder="Пробег"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none transition focus:border-cyan-400"
      />

      <button
        class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
      >
        Найти
      </button>
    </div>

    <div class="space-y-4">
      <button
        v-for="rule in rules"
        :key="rule.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400 hover:bg-bg dark:bg-card-dark"
        @click="openRule(rule.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">
                {{ rule.brand }} {{ rule.model }}
              </h2>

              <span class="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                {{ formatMileage(rule) }}
              </span>

              <span
  class="rounded-full px-3 py-1 text-xs"
  :class="rule.status === 'active' ? 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-300' : 'border border-amber-500/30 bg-amber-500/10 text-amber-300'"
>
  {{ rule.status === 'active' ? 'Активен' : 'Черновик' }}
</span>
            </div>

            <p class="mt-3 text-sm text-text-muted dark:text-text-muted">
              Работ: {{ rule.tasks?.length ?? 0 }} • Длительность: {{ rule.duration_minutes ? rule.duration_minutes + ' мин' : '—' }} • Цена: {{ rule.price ? rule.price + ' ₸' : '—' }}
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
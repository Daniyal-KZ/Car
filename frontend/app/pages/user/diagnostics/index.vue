<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

type DiagnosticOrder = {
  id: number
  service_kind: string
  service_name: string
  status: string
  requested_comment?: string | null
  created_at: string
  scheduled_at?: string | null
  car?: {
    brand: string
    model: string
    year: number | null
    mileage?: number | null
  } | null
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const endpoint = computed(() => `${config.public.apiBase}/service-orders/my`)
const { data, pending, error } = useFetch<DiagnosticOrder[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const items = computed(() => (data.value ?? []).filter(item => item.service_kind === 'diagnostics'))

const statusLabel = (status: string) => {
  if (status === 'new') return 'Новая'
  if (status === 'accepted') return 'В работе'
  if (status === 'in_progress') return 'В работе'
  if (status === 'completed') return 'Готово'
  return status
}

const statusTone = (status: string) => {
  if (status === 'new') return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
  if (status === 'accepted') return 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
  if (status === 'in_progress') return 'border-blue-500/30 bg-blue-500/10 text-blue-300'
  if (status === 'completed') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  return 'border-slate-500/30 bg-slate-500/10 text-slate-300'
}

const newCount = computed(() => items.value.filter(item => item.status === 'new').length)
const inWorkCount = computed(() => items.value.filter(item => item.status === 'accepted' || item.status === 'in_progress').length)
const doneCount = computed(() => items.value.filter(item => item.status === 'completed').length)

const symptomShort = (raw?: string | null) => {
  if (!raw) return 'Симптомы не указаны'
  return raw.length > 140 ? `${raw.slice(0, 140)}...` : raw
}

const openItem = (id: number) => navigateTo(`/user/diagnostics/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Диагностика</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
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

    <div class="mb-6 grid gap-4 md:grid-cols-3">
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Новые</p>
        <p class="mt-2 text-2xl font-bold text-amber-300">{{ newCount }}</p>
      </div>

      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">В работе</p>
        <p class="mt-2 text-2xl font-bold text-cyan-300">{{ inWorkCount }}</p>
      </div>

      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Готово</p>
        <p class="mt-2 text-2xl font-bold text-emerald-300">{{ doneCount }}</p>
      </div>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить диагностику.
    </div>

    <div v-else-if="!items.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Заявок на диагностику пока нет.
    </div>

    <div v-else class="space-y-4">
      <button
        v-for="item in items"
        :key="item.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400"
        @click="openItem(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">D-{{ item.id }} — {{ item.car?.brand }} {{ item.car?.model }}</h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">
                {{ statusLabel(item.status) }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Дата: {{ item.scheduled_at ? new Date(item.scheduled_at).toLocaleString() : new Date(item.created_at).toLocaleDateString() }}</p>
            <p class="mt-1 text-xs text-text-muted dark:text-text-muted">{{ item.car?.year || '-' }} год • {{ Number(item.car?.mileage || 0).toLocaleString() }} км</p>
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ symptomShort(item.requested_comment) }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
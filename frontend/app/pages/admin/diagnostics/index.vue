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
    vin?: string | null
    year: number | null
    mileage?: number | null
  } | null
  requester?: {
    username: string
  } | null
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const endpoint = computed(() => `${config.public.apiBase}/service-orders/mechanic/queue`)
const { data, pending, error } = useFetch<DiagnosticOrder[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const requests = computed(() => (data.value ?? []).filter(item => item.service_kind === 'diagnostics'))

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

const totalCount = computed(() => requests.value.length)
const newCount = computed(() => requests.value.filter(item => item.status === 'new').length)
const inWorkCount = computed(() => requests.value.filter(item => item.status === 'accepted' || item.status === 'in_progress').length)

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
        <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ totalCount }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Новые</p>
        <p class="mt-2 text-2xl font-bold text-cyan-300">{{ newCount }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">В работе</p>
        <p class="mt-2 text-2xl font-bold text-amber-300">{{ inWorkCount }}</p>
      </div>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить заявки диагностики.
    </div>

    <div v-else-if="!requests.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Активных заявок диагностики нет.
    </div>

    <div v-else class="space-y-4">
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
                D-{{ item.id }} — {{ item.car?.brand }} {{ item.car?.model }}
              </h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">
                {{ statusLabel(item.status) }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
              Владелец: {{ item.requester?.username || '-' }} • VIN: {{ item.car?.vin || 'Не указан' }}
            </p>
            <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ item.car?.year || '-' }} • {{ Number(item.car?.mileage || 0).toLocaleString() }} км • Дата: {{ item.scheduled_at ? new Date(item.scheduled_at).toLocaleString() : new Date(item.created_at).toLocaleDateString() }}</p>

            <p class="mt-3 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">
              {{ item.requested_comment || 'Симптомы не указаны' }}
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
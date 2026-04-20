<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

type ServiceRequest = {
  id: number
  order_number?: string | null
  car_id: number
  service_kind: string
  service_name: string
  status: string
  requested_comment?: string | null
  scheduled_at?: string | null
  created_at: string
  completion_comment?: string | null
  car?: {
    brand: string
    model: string
    vin?: string | null
    year: number | null
    mileage?: number | null
  } | null
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const endpoint = computed(() => `${config.public.apiBase}/service-orders/my`)

const { data, pending, error } = useFetch<ServiceRequest[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const items = computed(() => data.value ?? [])
const filter = ref<'all' | 'new' | 'accepted' | 'in_progress' | 'completed'>('all')

const kindLabel = (kind: string) => {
  if (kind === 'maintenance_rule') return 'Регламентное ТО'
  if (kind === 'diagnostics') return 'Диагностика'
  if (kind === 'technical_inspection') return 'Техосмотр'
  if (kind === 'damage_assessment') return 'Осмотр повреждений'
  return kind
}

const statusLabel = (status: string) => {
  if (status === 'new') return 'Новая'
  if (status === 'accepted') return 'Принята'
  if (status === 'in_progress') return 'В работе'
  if (status === 'completed') return 'Завершена'
  return status
}

const statusTone = (status: string) => {
  if (status === 'new') return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
  if (status === 'accepted') return 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
  if (status === 'in_progress') return 'border-blue-500/30 bg-blue-500/10 text-blue-300'
  if (status === 'completed') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  return 'border-slate-500/30 bg-slate-500/10 text-slate-300'
}

const filteredItems = computed(() => {
  if (filter.value === 'all') return items.value
  return items.value.filter(item => item.status === filter.value)
})

const counts = computed(() => ({
  all: items.value.length,
  new: items.value.filter(item => item.status === 'new').length,
  accepted: items.value.filter(item => item.status === 'accepted').length,
  in_progress: items.value.filter(item => item.status === 'in_progress').length,
  completed: items.value.filter(item => item.status === 'completed').length,
}))

const openItem = (id: number) => navigateTo(`/user/booking/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-text dark:text-text-dark">Все заявки</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Здесь собраны все ваши записи: регламент, диагностика, техосмотр и осмотр повреждений.
        </p>
      </div>

      <button
        class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        @click="navigateTo('/user/booking/new')"
      >
        + Новая заявка
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-5">
      <button class="rounded-2xl border px-4 py-3 text-left" :class="filter === 'all' ? 'border-cyan-400 bg-cyan-500/10' : 'border-border bg-bg dark:border-border-dark dark:bg-bg-dark'" @click="filter = 'all'">
        <p class="text-sm text-text-muted dark:text-text-muted">Все</p>
        <p class="mt-1 text-2xl font-bold text-text dark:text-text-dark">{{ counts.all }}</p>
      </button>
      <button class="rounded-2xl border px-4 py-3 text-left" :class="filter === 'new' ? 'border-amber-400 bg-amber-500/10' : 'border-border bg-bg dark:border-border-dark dark:bg-bg-dark'" @click="filter = 'new'">
        <p class="text-sm text-text-muted dark:text-text-muted">Новые</p>
        <p class="mt-1 text-2xl font-bold text-amber-300">{{ counts.new }}</p>
      </button>
      <button class="rounded-2xl border px-4 py-3 text-left" :class="filter === 'accepted' ? 'border-cyan-400 bg-cyan-500/10' : 'border-border bg-bg dark:border-border-dark dark:bg-bg-dark'" @click="filter = 'accepted'">
        <p class="text-sm text-text-muted dark:text-text-muted">Приняты</p>
        <p class="mt-1 text-2xl font-bold text-cyan-300">{{ counts.accepted }}</p>
      </button>
      <button class="rounded-2xl border px-4 py-3 text-left" :class="filter === 'in_progress' ? 'border-blue-400 bg-blue-500/10' : 'border-border bg-bg dark:border-border-dark dark:bg-bg-dark'" @click="filter = 'in_progress'">
        <p class="text-sm text-text-muted dark:text-text-muted">В работе</p>
        <p class="mt-1 text-2xl font-bold text-blue-300">{{ counts.in_progress }}</p>
      </button>
      <button class="rounded-2xl border px-4 py-3 text-left" :class="filter === 'completed' ? 'border-emerald-400 bg-emerald-500/10' : 'border-border bg-bg dark:border-border-dark dark:bg-bg-dark'" @click="filter = 'completed'">
        <p class="text-sm text-text-muted dark:text-text-muted">Готово</p>
        <p class="mt-1 text-2xl font-bold text-emerald-300">{{ counts.completed }}</p>
      </button>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить заявки.
    </div>

    <div v-else-if="!filteredItems.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Заявок по фильтру нет.
    </div>

    <div v-else class="space-y-4">
      <button
        v-for="item in filteredItems"
        :key="item.id"
        class="w-full rounded-2xl border border-border bg-bg p-5 text-left transition hover:border-cyan-400 dark:border-border-dark dark:bg-bg-dark"
        @click="openItem(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark">{{ item.order_number || `ORD-${item.id}` }} — {{ item.car?.brand }} {{ item.car?.model }}</h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">
                {{ statusLabel(item.status) }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">{{ kindLabel(item.service_kind) }} · {{ item.service_name }}</p>
            <p class="mt-2 text-sm text-text dark:text-text-dark dark:text-slate-300">
              {{ item.scheduled_at ? new Date(item.scheduled_at).toLocaleString() : 'Без времени' }}
            </p>
            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">VIN: {{ item.car?.vin || 'Не указан' }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>

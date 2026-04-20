<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
  roles: ["mechanic", "admin", "dev"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()

const endpoint = computed(() => `${config.public.apiBase}/service-orders/mechanic/queue`)

const { data, pending, error, refresh } = useFetch<any[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const items = computed(() => data.value ?? [])

const counts = computed(() => ({
  all: items.value.length,
  new: items.value.filter(item => item.status === 'new').length,
  maintenance: items.value.filter(item => item.service_kind === 'maintenance_rule').length,
  diagnostics: items.value.filter(item => item.service_kind === 'diagnostics').length,
  inspection: items.value.filter(item => item.service_kind === 'technical_inspection').length,
  damage: items.value.filter(item => item.service_kind === 'damage_assessment').length,
}))

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

const acceptOrder = async (id: number) => {
  await $fetch(`${config.public.apiBase}/service-orders/${id}/accept`, {
    method: 'POST',
    headers: {
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    },
    body: {},
  })
  await refresh()
}

const openOrder = (id: number) => navigateTo(`/mechanic/orders/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-text dark:text-text-dark">Заявки механика</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Все заявки на регламент, диагностику, техосмотр и осмотр повреждений.</p>
      </div>
      <button class="rounded-2xl border border-border bg-bg px-5 py-3 text-sm font-medium text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark" @click="navigateTo('/mechanic/orders')">
        Открыть рабочую очередь
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-5">
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Всего</p>
        <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark">{{ counts.all }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Новые</p>
        <p class="mt-2 text-2xl font-bold text-amber-300">{{ counts.new }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Регламент</p>
        <p class="mt-2 text-2xl font-bold text-emerald-300">{{ counts.maintenance }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Диагностика</p>
        <p class="mt-2 text-2xl font-bold text-cyan-300">{{ counts.diagnostics }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Дефекты</p>
        <p class="mt-2 text-2xl font-bold text-blue-300">{{ counts.damage + counts.inspection }}</p>
      </div>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">Загрузка...</div>
    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">Не удалось загрузить очередь.</div>
    <div v-else-if="!items.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">Активных записей нет.</div>

    <div v-else class="space-y-4">
      <div v-for="item in items" :key="item.id" class="rounded-2xl border border-border bg-bg p-5 dark:border-border-dark dark:bg-bg-dark">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark">ORD-{{ item.id }} — {{ item.car?.brand }} {{ item.car?.model }}</h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">{{ statusLabel(item.status) }}</span>
            </div>
            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">{{ kindLabel(item.service_kind) }} · {{ item.service_name }}</p>
            <p class="mt-1 text-sm text-text-muted dark:text-text-muted">Владелец: {{ item.requester?.username || '-' }}</p>
            <p class="mt-1 text-sm text-text-muted dark:text-text-muted">VIN: {{ item.car?.vin || 'Не указан' }}</p>
            <p class="mt-1 text-sm text-text dark:text-text-dark">{{ item.scheduled_at ? new Date(item.scheduled_at).toLocaleString() : 'Без времени' }}</p>
          </div>
          <div class="flex gap-2">
            <button v-if="item.status === 'new'" class="rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300 hover:bg-emerald-500/20" @click="acceptOrder(item.id)">Принять</button>
            <button class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-300" @click="openOrder(item.id)">Открыть</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

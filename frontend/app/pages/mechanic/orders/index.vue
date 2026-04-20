<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
  roles: ["mechanic", "admin", "dev"],
})

type ServiceOrder = {
  id: number
  car_id: number
  service_kind: string
  service_name: string
  status: string
  requested_comment?: string | null
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
  mechanic?: {
    username: string
  } | null
}

const config = useRuntimeConfig()
const auth = useAuthStore()
const { t, locale } = useI18n()

const endpoint = computed(() => `${config.public.apiBase}/service-orders/mechanic/queue`)

const { data, pending, error, refresh } = useFetch<ServiceOrder[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
      'X-Lang': locale.value,
    })),
    watch: [endpoint, () => auth.token, locale],
  }
)

const items = computed(() => data.value ?? [])

const newCount = computed(() => items.value.filter(item => item.status === 'new').length)
const acceptedCount = computed(() => items.value.filter(item => item.status === 'accepted').length)
const inProgressCount = computed(() => items.value.filter(item => item.status === 'in_progress').length)
const maintenanceCount = computed(() => items.value.filter(item => item.service_kind === 'maintenance_rule').length)

const kindLabel = (kind: string) => {
  if (kind === 'maintenance_rule') return t('service_kind_maintenance_rule')
  if (kind === 'diagnostics') return t('service_kind_diagnostics')
  if (kind === 'technical_inspection') return t('service_kind_technical_inspection')
  if (kind === 'damage_assessment') return t('service_kind_damage_assessment')
  return kind
}

const statusLabel = (status: string) => {
  if (status === 'new') return t('service_status_new')
  if (status === 'accepted') return t('service_status_accepted')
  if (status === 'in_progress') return t('service_status_in_progress')
  if (status === 'completed') return t('service_status_completed')
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
      'X-Lang': locale.value,
    },
    body: {},
  })
  await refresh()
}

const openOrder = (id: number) => navigateTo(`/mechanic/orders/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark">{{ t('mechanic_queue_title') }}</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_queue_subtitle') }}</p>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_stat_new') }}</p>
        <p class="mt-2 text-2xl font-bold text-amber-300">{{ newCount }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_stat_accepted') }}</p>
        <p class="mt-2 text-2xl font-bold text-cyan-300">{{ acceptedCount }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_stat_in_progress') }}</p>
        <p class="mt-2 text-2xl font-bold text-blue-300">{{ inProgressCount }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_stat_maintenance') }}</p>
        <p class="mt-2 text-2xl font-bold text-emerald-300">{{ maintenanceCount }}</p>
      </div>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      {{ t('common_loading') }}
    </div>

    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      {{ t('mechanic_queue_load_error') }}
    </div>

    <div v-else-if="!items.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      {{ t('mechanic_queue_empty') }}
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="rounded-2xl border border-border bg-bg p-5 dark:border-border-dark dark:bg-bg-dark"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark">ORD-{{ item.id }} — {{ item.car?.brand }} {{ item.car?.model }}</h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">
                {{ statusLabel(item.status) }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_service_label') }}: {{ item.service_name }}</p>
            <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_type_label') }}: {{ kindLabel(item.service_kind) }}</p>
            <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_owner_label') }}: {{ item.requester?.username || '-' }}</p>
            <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ t('mechanic_car_line', { id: item.car_id, year: item.car?.year || '-', mileage: Number(item.car?.mileage || 0).toLocaleString(), km: t('garage_km_short') }) }}</p>
            <p class="mt-1 text-sm text-text-muted dark:text-text-muted">VIN: {{ item.car?.vin || t('garage_not_specified') }}</p>
            <p class="mt-1 text-sm text-text dark:text-text-dark">{{ item.scheduled_at ? new Date(item.scheduled_at).toLocaleString() : t('mechanic_no_time') }}</p>
          </div>

          <div class="flex gap-2">
            <button
              v-if="item.status === 'new'"
              class="rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300 hover:bg-emerald-500/20"
              @click="acceptOrder(item.id)"
            >
              {{ t('mechanic_accept') }}
            </button>
            <button
              class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-300"
              @click="openOrder(item.id)"
            >
              {{ t('mechanic_open') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

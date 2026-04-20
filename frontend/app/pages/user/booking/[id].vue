<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

type BookingOrder = {
  id: number
  car_id: number
  service_kind: string
  service_name: string
  status: string
  requested_comment?: string | null
  completion_comment?: string | null
  scheduled_at?: string | null
  created_at: string
  completed_at?: string | null
  accepted_at?: string | null
  car?: {
    brand: string
    model: string
    year: number | null
  } | null
}

const bookingId = computed(() => Number(route.params.id))
const getEndpoint = computed(() => `${config.public.apiBase}/service-orders/${bookingId.value}`)

const { data, pending, error } = useFetch<BookingOrder>(
  () => getEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [getEndpoint, () => auth.token],
  }
)

const statusLabel = (status?: string) => {
  if (!status) return '-'
  if (status === 'new') return 'Создана'
  if (status === 'accepted') return 'Принята механиком'
  if (status === 'in_progress') return 'В работе'
  if (status === 'completed') return 'Завершена'
  return status
}

const statusTone = (status?: string) => {
  if (status === 'new') return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
  if (status === 'accepted') return 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
  if (status === 'in_progress') return 'border-blue-500/30 bg-blue-500/10 text-blue-300'
  if (status === 'completed') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  return 'border-slate-500/30 bg-slate-500/10 text-slate-300'
}

const item = computed(() => data.value ?? null)
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !item" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить детали записи.
    </div>

    <div v-else>
      <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Запись ORD-{{ item.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Детали записи</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/booking')"
      >
        Назад
      </button>
      </div>

      <div class="grid gap-6 md:grid-cols-2">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Информация</h2>

          <div class="mt-5 space-y-4">
            <div><p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.car?.brand }} {{ item.car?.model }}</p></div>
            <div><p class="text-sm text-text-muted dark:text-text-muted">Услуга</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.service_name }}</p></div>
            <div><p class="text-sm text-text-muted dark:text-text-muted">Дата и время</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.scheduled_at ? new Date(item.scheduled_at).toLocaleString() : '-' }}</p></div>
            <div>
              <p class="text-sm text-text-muted dark:text-text-muted">Статус</p>
              <p class="mt-1 inline-flex rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">
                {{ statusLabel(item.status) }}
              </p>
            </div>
            <div v-if="item.accepted_at"><p class="text-sm text-text-muted dark:text-text-muted">Принята</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ new Date(item.accepted_at).toLocaleString() }}</p></div>
            <div v-if="item.completed_at"><p class="text-sm text-text-muted dark:text-text-muted">Завершена</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ new Date(item.completed_at).toLocaleString() }}</p></div>
          </div>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Комментарии</h2>
          <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">{{ item.requested_comment || 'Комментарий клиента отсутствует' }}</p>
          <p v-if="item.completion_comment" class="mt-4 text-sm leading-6 text-emerald-300">Результат механика: {{ item.completion_comment }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
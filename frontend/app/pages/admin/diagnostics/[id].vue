<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

type DiagnosticOrder = {
  id: number
  car_id: number
  service_kind: string
  service_name: string
  status: string
  requested_comment?: string | null
  scheduled_at?: string | null
  completion_comment?: string | null
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

const endpoint = computed(() => `${config.public.apiBase}/service-orders/${route.params.id}`)
const { data, pending, error } = useFetch<DiagnosticOrder>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const request = computed(() => data.value)

const statusLabel = computed(() => {
  const status = request.value?.status
  if (status === 'new') return 'Новая'
  if (status === 'accepted') return 'В работе'
  if (status === 'in_progress') return 'В работе'
  if (status === 'completed') return 'Готово'
  return status || '-'
})

const vin = computed(() => request.value?.car?.vin || 'Не указан')
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Заявка D-{{ route.params.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Диагностика автомобиля</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Работа с конкретной заявкой клиента и оформление результата диагностики.
        </p>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/admin/diagnostics')"
      >
        Назад
      </button>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !request || request.service_kind !== 'diagnostics'" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить заявку диагностики.
    </div>

    <template v-else>
    <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ request.car?.brand }} {{ request.car?.model }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">VIN</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ vin }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Пробег</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ Number(request.car?.mileage || 0).toLocaleString() }} км</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Клиент</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ request.requester?.username || '-' }}</p>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.1fr_1.2fr]">
      <div class="space-y-6">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Описание клиента</h2>
          <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">
            {{ request.requested_comment || 'Симптомы не указаны' }}
          </p>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Текущий результат</h2>
          <p class="mt-4 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ request.completion_comment || 'Механик еще не сохранил результат.' }}</p>
        </div>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Рабочая карта</h2>
        <p class="mt-4 text-sm text-text-muted dark:text-text-muted">Статус: {{ statusLabel }}</p>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Тип: {{ request.service_name }}</p>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Время записи: {{ request.scheduled_at ? new Date(request.scheduled_at).toLocaleString() : '-' }}</p>

        <button
          class="mt-6 w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
          @click="navigateTo(`/mechanic/orders/${request.id}`)"
        >
          Открыть и завершить диагностику
        </button>
      </div>
    </div>
    </template>
  </div>
</template>
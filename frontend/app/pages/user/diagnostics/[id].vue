<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

type DiagnosticOrder = {
  id: number
  service_kind: string
  service_name: string
  status: string
  requested_comment?: string | null
  completion_comment?: string | null
  car?: {
    brand: string
    model: string
    vin?: string | null
    year: number | null
    mileage?: number | null
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

const item = computed(() => data.value)

const statusLabel = computed(() => {
  const status = item.value?.status
  if (status === 'new') return 'Новая'
  if (status === 'accepted') return 'В работе'
  if (status === 'in_progress') return 'В работе'
  if (status === 'completed') return 'Готово'
  return status || '-'
})

const vinFromComment = computed(() => item.value?.car?.vin || 'Не указан')
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Заявка D-{{ route.params.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Результат диагностики</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/diagnostics')"
      >
        Назад
      </button>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !item || item.service_kind !== 'diagnostics'" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить заявку на диагностику.
    </div>

    <template v-else>
    <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.car?.brand }} {{ item.car?.model }}</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">VIN</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ vinFromComment }}</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Пробег</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ Number(item.car?.mileage || 0).toLocaleString() }} км</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Статус</p>
        <p class="mt-2 font-semibold text-cyan-300">{{ statusLabel }}</p>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Симптомы</h2>
        <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">{{ item.requested_comment || 'Не указаны' }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Результат</h2>
        <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">{{ item.completion_comment || 'Диагностика еще не завершена механиком.' }}</p>

        <div class="mt-5 rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
          <p class="text-sm text-text-muted dark:text-text-muted">Тип услуги</p>
          <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.service_name }}</p>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>
<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
  roles: ["admin", "dev"],
})

type Invoice = {
  id: number
  invoice_number: string
  status: string
  total: number
  created_at: string
  order?: {
    id: number
    service_name: string
    status: string
  } | null
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const endpoint = computed(() => `${config.public.apiBase}/invoices/admin/all`)

const { data, pending, error } = useFetch<Invoice[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const estimates = computed(() => data.value ?? [])

const statusLabel = (status: string) => {
  if (status === 'draft') return 'Черновик'
  if (status === 'sent') return 'Отправлено клиенту'
  if (status === 'paid') return 'Оплачено'
  return 'Ожидает оплаты'
}

const statusTone = (status: string) => {
  if (status === 'paid') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  if (status === 'sent') return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
  if (status === 'draft') return 'border-slate-500/30 bg-slate-500/10 text-slate-300'
  return 'border-rose-500/30 bg-rose-500/10 text-rose-300'
}

const openItem = (id: number) => navigateTo(`/admin/estimate/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Расчёт сметы</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Список заявок на смету. Каждая смета открывается на отдельной странице.
      </p>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить сметы.
    </div>

    <div v-else-if="!estimates.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Смет пока нет.
    </div>

    <div v-else class="space-y-4">
      <button
        v-for="item in estimates"
        :key="item.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400"
        @click="openItem(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.invoice_number }}</h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">
                {{ statusLabel(item.status) }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Заявка: ORD-{{ item.order?.id || '-' }}</p>
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ item.order?.service_name || 'Сервисная заявка' }}</p>
            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Сумма: {{ item.total.toLocaleString() }} ₸</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
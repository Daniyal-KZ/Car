<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

type Invoice = {
  id: number
  invoice_number: string
  status: string
  total: number
  created_at: string
}

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const invoiceId = computed(() => Number(route.params.id))
const endpoint = computed(() => `${config.public.apiBase}/invoices/${invoiceId.value}`)

const { data, pending, error } = useFetch<Invoice>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const invoice = computed(() => data.value ?? null)

const statusLabel = (status: string) => {
  if (status === 'paid') return 'Оплачено'
  if (status === 'sent') return 'Отправлено'
  return 'Ожидает оплаты'
}

const statusTone = (status: string) => {
  if (status === 'paid') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  if (status === 'sent') return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
  return 'border-slate-500/30 bg-slate-500/10 text-slate-300'
}

const openKaspiQr = () => navigateTo(`/user/payment/${invoiceId.value}/kaspi-qr`)
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !invoice" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить данные для оплаты.
    </div>

    <div v-else>
      <div class="mb-8 flex items-start justify-between gap-4">
        <div>
          <p class="text-sm text-text dark:text-slate-300">Оплата счёта {{ invoice.invoice_number }}</p>
          <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark">Выбор способа оплаты</h1>
        </div>

        <button
          class="rounded-xl border border-border px-4 py-2 text-sm text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-slate-700 dark:text-text-dark"
          @click="navigateTo(`/user/invoices/${invoice.id}`)"
        >
          Назад к счёту
        </button>
      </div>

      <div class="mb-6 rounded-2xl border border-cyan-500/30 bg-cyan-500/10 p-5">
        <p class="text-sm text-cyan-100">Сумма к оплате</p>
        <p class="mt-2 text-3xl font-bold text-text dark:text-text-dark">{{ invoice.total.toLocaleString() }} ₸</p>
        <p class="mt-4 text-sm text-text-muted dark:text-text-muted">Статус: <span class="inline-flex rounded-full border px-3 py-1 text-xs" :class="statusTone(invoice.status)">{{ statusLabel(invoice.status) }}</span></p>
      </div>

      <div v-if="invoice.status === 'paid'" class="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-5 text-emerald-200">
        Этот счёт уже оплачен.
        <button
          class="mt-4 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-300"
          @click="navigateTo(`/user/invoices/${invoice.id}`)"
        >
          Открыть счёт
        </button>
      </div>

      <div v-else class="grid gap-4 md:grid-cols-3">
        <button
          class="rounded-2xl border border-border bg-bg p-5 text-left transition hover:border-cyan-400 dark:border-border-dark dark:bg-bg-dark"
          @click="openKaspiQr"
        >
          <p class="text-base font-semibold text-text dark:text-text-dark">QR Kaspi</p>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Оплата по QR-коду Kaspi (заглушка страницы)</p>
        </button>

        <button
          class="rounded-2xl border border-border bg-bg p-5 text-left transition hover:border-cyan-400 dark:border-border-dark dark:bg-bg-dark"
          disabled
        >
          <p class="text-base font-semibold text-text dark:text-text-dark">Банк</p>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Банковская карта/перевод. Скоро.</p>
        </button>

        <button
          class="rounded-2xl border border-border bg-bg p-5 text-left transition hover:border-cyan-400 dark:border-border-dark dark:bg-bg-dark"
          disabled
        >
          <p class="text-base font-semibold text-text dark:text-text-dark">Наличка</p>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Оплата на кассе при визите. Скоро.</p>
        </button>
      </div>
    </div>
  </div>
</template>

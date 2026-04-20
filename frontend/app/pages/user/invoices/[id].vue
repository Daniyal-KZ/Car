<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

type InvoiceItem = {
  id: number
  title: string
  quantity: number
  unit_price: number
  total_price: number
}

type Invoice = {
  id: number
  invoice_number: string
  status: string
  total: number
  created_at: string
  items: InvoiceItem[]
}

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
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !invoice" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить счет.
    </div>

    <div v-else>
      <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Счёт {{ invoice.invoice_number }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Детали счёта</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/invoices')"
      >
        Назад
      </button>
      </div>

      <div class="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Состав счёта</h2>

        <div class="mt-5 space-y-3">
          <div
            v-for="item in invoice.items"
            :key="item.id"
            class="flex items-center justify-between rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ px-4 py-3"
          >
            <span class="text-sm text-text dark:text-text-dark">{{ item.title }} × {{ item.quantity }}</span>
            <span class="text-sm font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.total_price.toLocaleString() }} ₸</span>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Сводка</h2>

        <div class="mt-5 space-y-4">
          <div><p class="text-sm text-text-muted dark:text-text-muted">Номер</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoice.invoice_number }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Дата</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ new Date(invoice.created_at).toLocaleString() }}</p></div>
          <div>
            <p class="text-sm text-text-muted dark:text-text-muted">Статус</p>
            <p class="mt-1 inline-flex rounded-full border px-3 py-1 text-xs" :class="statusTone(invoice.status)">
              {{ statusLabel(invoice.status) }}
            </p>
          </div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Итого</p><p class="mt-1 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoice.total.toLocaleString() }} ₸</p></div>
        </div>

        <button
          v-if="invoice.status !== 'paid'"
          class="mt-6 w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
          @click="navigateTo(`/user/payment/${invoice.id}`)"
        >
          Оплатить
        </button>

        <div v-else class="mt-6 rounded-2xl border border-emerald-500/40 bg-emerald-500/10 px-5 py-3 text-center text-sm font-semibold text-emerald-300">
          Счет уже оплачен
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
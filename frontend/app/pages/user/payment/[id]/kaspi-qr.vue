<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const invoiceId = computed(() => Number(route.params.id))

const endpoint = computed(() => `${config.public.apiBase}/invoices/${invoiceId.value}`)
const { data, pending, error, refresh } = useFetch<{ invoice_number: string; total: number; status: string }>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const paying = ref(false)
const payError = ref('')
const redirectTimer = ref<ReturnType<typeof setTimeout> | null>(null)

const statusLabel = (status: string) => {
  if (status === 'paid') return 'Оплачено'
  return 'Ожидает оплаты'
}

const statusTone = (status: string) => {
  if (status === 'paid') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
}

const scheduleRedirectToInvoice = () => {
  if (redirectTimer.value) {
    clearTimeout(redirectTimer.value)
  }
  redirectTimer.value = setTimeout(() => {
    navigateTo(`/user/invoices/${invoiceId.value}`)
  }, 1300)
}

watch(
  () => data.value?.status,
  (status) => {
    if (status === 'paid') {
      scheduleRedirectToInvoice()
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (redirectTimer.value) {
    clearTimeout(redirectTimer.value)
  }
})

const markAsPaid = async () => {
  payError.value = ''
  paying.value = true
  try {
    await $fetch(`${config.public.apiBase}/invoices/${invoiceId.value}/mark-paid`, {
      method: 'POST',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
    })
    await refresh()
    scheduleRedirectToInvoice()
  } catch (e) {
    console.error(e)
    payError.value = 'Не удалось подтвердить оплату.'
  } finally {
    paying.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-4xl px-4 py-6">
    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !data" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось открыть страницу QR.
    </div>

    <div v-else>
      <div class="mb-8 flex items-start justify-between gap-4">
        <div>
          <p class="text-sm text-text dark:text-slate-300">Счёт {{ data.invoice_number }}</p>
          <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark">Kaspi QR</h1>
        </div>

        <button
          class="rounded-xl border border-border px-4 py-2 text-sm text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-slate-700 dark:text-text-dark"
          @click="navigateTo(`/user/payment/${invoiceId}`)"
        >
          Назад к способам
        </button>
      </div>

      <div class="grid gap-6 md:grid-cols-[1fr_1fr]">
        <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Сумма</p>
          <p class="mt-2 text-3xl font-bold text-text dark:text-text-dark">{{ data.total.toLocaleString() }} ₸</p>

          <p class="mt-4 text-sm text-text-muted dark:text-text-muted">Статус: <span class="inline-flex rounded-full border px-3 py-1 text-xs" :class="statusTone(data.status)">{{ statusLabel(data.status) }}</span></p>

          <p class="mt-6 text-sm text-text-muted dark:text-text-muted">
            Отсканируйте QR в приложении Kaspi и подтвердите оплату.
          </p>

          <p class="mt-2 text-xs text-amber-300">
            Заглушка: реальный QR и авто-подтверждение подключим позже.
          </p>

          <div v-if="payError" class="mt-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
            {{ payError }}
          </div>

          <button
            v-if="data.status !== 'paid'"
            class="mt-5 w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
            :disabled="paying"
            @click="markAsPaid"
          >
            {{ paying ? 'Оплата...' : 'Я оплатил (Kaspi)' }}
          </button>

          <button
            v-else
            class="mt-5 w-full rounded-2xl border border-emerald-500/40 bg-emerald-500/10 px-5 py-3 text-sm font-semibold text-emerald-300"
            @click="navigateTo(`/user/invoices/${invoiceId}`)"
          >
            Счёт оплачен, открыть счёт (переход автоматически)
          </button>
        </div>

        <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
          <div class="mx-auto flex h-64 w-64 items-center justify-center rounded-2xl border border-dashed border-cyan-400 bg-cyan-500/10">
            <div class="text-center">
              <p class="text-sm font-semibold text-cyan-200">QR PLACEHOLDER</p>
              <p class="mt-2 text-xs text-cyan-100/80">Kaspi QR будет здесь</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

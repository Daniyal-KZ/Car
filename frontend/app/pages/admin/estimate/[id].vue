<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
  roles: ["admin", "dev"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

type InvoiceItem = {
  id?: number
  title: string
  quantity: number
  unit_price: number
  total_price?: number
}

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
  items: InvoiceItem[]
}

const invoiceId = computed(() => Number(route.params.id))
const endpoint = computed(() => `${config.public.apiBase}/invoices/admin/${invoiceId.value}`)

const { data, pending, error, refresh } = useFetch<Invoice>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const estimateItems = ref<InvoiceItem[]>([])
const saving = ref(false)
const sending = ref(false)
const message = ref('')
const isLocked = computed(() => {
  const status = data.value?.status
  return status === 'sent' || status === 'paid'
})
const canSend = computed(() => {
  const status = data.value?.status
  return status === 'draft' || status === 'unpaid'
})

watch(
  () => data.value,
  (invoice) => {
    if (!invoice) return
    estimateItems.value = invoice.items?.map(item => ({
      id: item.id,
      title: item.title,
      quantity: item.quantity,
      unit_price: item.unit_price,
      total_price: item.total_price,
    })) ?? []
  },
  { immediate: true }
)

const addItem = () => {
  if (isLocked.value) return
  estimateItems.value.push({ title: '', quantity: 1, unit_price: 0 })
}

const removeItem = (index: number) => {
  if (isLocked.value) return
  estimateItems.value.splice(index, 1)
}

const total = computed(() =>
  estimateItems.value.reduce((sum, item) => sum + Number(item.quantity || 0) * Number(item.unit_price || 0), 0)
)

const saveEstimate = async () => {
  if (isLocked.value) return
  saving.value = true
  message.value = ''
  try {
    await $fetch(`${config.public.apiBase}/invoices/admin/${invoiceId.value}`, {
      method: 'PUT',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
      body: {
        items: estimateItems.value
          .filter(item => item.title.trim().length > 0)
          .map(item => ({
            title: item.title,
            quantity: Number(item.quantity || 1),
            unit_price: Number(item.unit_price || 0),
          })),
      },
    })
    await refresh()
    message.value = 'Смета сохранена.'
  } catch (e) {
    console.error(e)
    message.value = 'Ошибка сохранения сметы.'
  } finally {
    saving.value = false
  }
}

const sendEstimate = async () => {
  if (!canSend.value || isLocked.value) return
  sending.value = true
  message.value = ''
  try {
    await $fetch(`${config.public.apiBase}/invoices/admin/${invoiceId.value}/send`, {
      method: 'POST',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
    })
    await refresh()
    message.value = 'Смета отправлена клиенту.'
  } catch (e) {
    console.error(e)
    message.value = 'Ошибка отправки сметы.'
  } finally {
    sending.value = false
  }
}

const statusLabel = computed(() => {
  if (!data.value) return '-'
  if (data.value.status === 'draft') return 'Черновик'
  if (data.value.status === 'sent') return 'Отправлено клиенту'
  if (data.value.status === 'paid') return 'Оплачено'
  return 'Ожидает оплаты'
})
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !data" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить смету.
    </div>

    <div v-else>
      <div class="mb-8 flex items-start justify-between gap-4">
        <div>
          <p class="text-sm text-text dark:text-slate-300">Смета {{ data.invoice_number }}</p>
          <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark">Редактирование сметы</h1>
        </div>

        <button
          class="rounded-xl border border-border px-4 py-2 text-sm text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-slate-700 dark:text-text-dark"
          @click="navigateTo('/admin/estimate')"
        >
          Назад
        </button>
      </div>

      <div v-if="message" class="mb-4 rounded-xl border border-border bg-bg p-3 text-sm text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
        {{ message }}
      </div>

      <div class="mb-6 grid gap-4 md:grid-cols-3">
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Заявка</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">ORD-{{ data.order?.id || '-' }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Услуга</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ data.order?.service_name || '-' }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Статус</p>
          <p class="mt-2 font-semibold text-cyan-300">{{ statusLabel }}</p>
        </div>
      </div>

      <div class="grid gap-6 xl:grid-cols-[1.35fr_1fr]">
        <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark">Состав сметы</h2>

          <div class="mt-5 space-y-3">
            <div
              v-for="(part, index) in estimateItems"
              :key="index"
              class="grid gap-3 rounded-2xl border border-border p-4 md:grid-cols-[1.4fr_0.4fr_0.6fr_auto] dark:border-border-dark"
            >
              <input v-model="part.title" type="text" :disabled="isLocked" class="rounded-xl border border-border bg-bg px-3 py-2 text-sm dark:border-border-dark dark:bg-bg-dark disabled:opacity-60" placeholder="Название" />
              <input v-model.number="part.quantity" type="number" min="1" :disabled="isLocked" class="rounded-xl border border-border bg-bg px-3 py-2 text-sm dark:border-border-dark dark:bg-bg-dark disabled:opacity-60" placeholder="Кол-во" />
              <input v-model.number="part.unit_price" type="number" min="0" :disabled="isLocked" class="rounded-xl border border-border bg-bg px-3 py-2 text-sm dark:border-border-dark dark:bg-bg-dark disabled:opacity-60" placeholder="Цена" />
              <button class="rounded-xl border border-red-500 px-3 py-2 text-sm text-red-500 disabled:opacity-50" :disabled="isLocked" @click="removeItem(index)">X</button>
            </div>
          </div>

          <button class="mt-4 rounded-xl border border-border px-4 py-2 text-sm hover:border-cyan-400 dark:border-border-dark disabled:opacity-50" :disabled="isLocked" @click="addItem">
            + Добавить позицию
          </button>
        </div>

        <div class="space-y-6">
          <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
            <h2 class="text-lg font-semibold text-text dark:text-text-dark">Итоги</h2>

            <div class="mt-5 space-y-4">
              <div class="rounded-2xl border border-cyan-500/30 bg-cyan-500/10 p-4">
                <p class="text-sm text-cyan-200">Итого</p>
                <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark">{{ total.toLocaleString() }} ₸</p>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
            <h2 class="text-lg font-semibold text-text dark:text-text-dark">Действия</h2>

            <div class="mt-5 space-y-3">
              <button
                class="w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
                :disabled="saving || isLocked"
                @click="saveEstimate"
              >
                {{ saving ? 'Сохранение...' : 'Сохранить смету' }}
              </button>
              <button
                class="w-full rounded-2xl border border-border bg-bg px-5 py-3 text-sm font-medium text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark disabled:opacity-50"
                :disabled="sending || isLocked || !canSend"
                @click="sendEstimate"
              >
                {{ sending ? 'Отправка...' : 'Отправить клиенту' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

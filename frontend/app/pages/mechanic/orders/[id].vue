<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
  roles: ["mechanic", "admin", "dev"],
})

type MaintenanceRuleTask = {
  id: number
  title: string
  description?: string | null
  mileage_interval: number
  duration_minutes?: number | null
  unit_price: number
}

type MaintenanceRule = {
  id: number
  title: string
  tasks: MaintenanceRuleTask[]
}

type EstimateItem = {
  title: string
  quantity: number
  unit_price: number
  task_id?: number
}

type ServiceOrder = {
  id: number
  car_id: number
  service_name: string
  service_kind: string
  status: string
  requested_comment?: string | null
  completion_comment?: string | null
  scheduled_at?: string | null
  maintenance_rule?: MaintenanceRule | null
  car?: {
    brand: string
    model: string
    vin?: string | null
    year: number | null
    mileage: number
  } | null
  requester?: {
    username: string
  } | null
  mechanic?: {
    username: string
  } | null
}

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const orderId = computed(() => Number(route.params.id))
const endpoint = computed(() => `${config.public.apiBase}/service-orders/${orderId.value}`)

const { data, pending, error, refresh } = useFetch<ServiceOrder>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const order = computed(() => data.value ?? null)
const isCompleted = computed(() => order.value?.status === 'completed')
const saving = ref(false)
const saveError = ref<string | null>(null)

const completionComment = ref('')
const estimateItems = reactive<EstimateItem[]>([
  { title: 'Работы', quantity: 1, unit_price: 20000 },
])
const selectedTasks = reactive<Set<number>>(new Set())

watch(order, (value) => {
  if (!value) return
  completionComment.value = value.completion_comment || ''
})

const addItem = () => {
  if (isCompleted.value) return
  estimateItems.push({ title: '', quantity: 1, unit_price: 0 })
}

const removeItem = (index: number) => {
  if (isCompleted.value) return
  estimateItems.splice(index, 1)
}

const toggleTask = (task: MaintenanceRuleTask) => {
  if (isCompleted.value) return
  if (selectedTasks.has(task.id)) {
    selectedTasks.delete(task.id)
    // Удалить из сметы
    const idx = estimateItems.findIndex(item => item.task_id === task.id)
    if (idx !== -1) {
      estimateItems.splice(idx, 1)
    }
  } else {
    selectedTasks.add(task.id)
    // Добавить в смету с ценой из регламента
    estimateItems.push({
      title: task.title,
      quantity: 1,
      unit_price: task.unit_price || 0,
      task_id: task.id,
    })
  }
}

const acceptOrder = async () => {
  await $fetch(`${config.public.apiBase}/service-orders/${orderId.value}/accept`, {
    method: 'POST',
    headers: {
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    },
    body: {},
  })
  await refresh()
}

const completeOrder = async () => {
  saving.value = true
  saveError.value = null
  try {
    await $fetch(`${config.public.apiBase}/service-orders/${orderId.value}/complete`, {
      method: 'POST',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
      body: {
        completion_comment: completionComment.value,
        estimate_items: estimateItems.filter(item => item.title.trim().length > 0),
      },
    })

    await refresh()
  } catch (e) {
    console.error(e)
    saveError.value = 'Не удалось завершить заявку.'
  } finally {
    saving.value = false
  }
}

const total = computed(() =>
  estimateItems.reduce((sum, item) => sum + Number(item.quantity || 0) * Number(item.unit_price || 0), 0)
)

const kindLabel = computed(() => {
  const kind = order.value?.service_kind
  if (kind === 'maintenance_rule') return 'Регламентное ТО'
  if (kind === 'diagnostics') return 'Диагностика'
  if (kind === 'technical_inspection') return 'Техосмотр'
  if (kind === 'damage_assessment') return 'Осмотр повреждений'
  return kind || '-'
})
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !order" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить заявку.
    </div>

    <div v-else>
      <div class="mb-8 flex items-start justify-between gap-4">
        <div>
          <p class="text-sm text-text dark:text-slate-300">Заявка ORD-{{ order.id }}</p>
          <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark">{{ order.service_name }}</h1>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">{{ order.car?.brand }} {{ order.car?.model }} • Клиент: {{ order.requester?.username || '-' }}</p>
        </div>

        <button
          class="rounded-xl border border-border px-4 py-2 text-sm text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-slate-700 dark:text-text-dark"
          @click="navigateTo('/mechanic/orders')"
        >
          Назад
        </button>
      </div>

      <div v-if="saveError" class="mb-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
        {{ saveError }}
      </div>

      <div class="mb-6 grid gap-4 md:grid-cols-3">
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Статус</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ order.status }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Время записи</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ order.scheduled_at ? new Date(order.scheduled_at).toLocaleString() : '-' }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Пробег</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ order.car?.mileage?.toLocaleString() || '-' }} км</p>
        </div>
      </div>

      <div class="mb-6 grid gap-4 md:grid-cols-4">
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Владелец</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ order.requester?.username || '-' }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">VIN</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ order.car?.vin || 'Не указан' }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Тип услуги</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ kindLabel }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">ID машины</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ order.car_id }}</p>
        </div>
      </div>

      <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark">Комментарий клиента</h2>
          <p class="mt-3 text-sm text-text dark:text-text-dark">{{ order.requested_comment || 'Без комментария' }}</p>

          <!-- РЕГЛАМЕНТ ЕСЛИ ЭТО MAINTENANCE_RULE -->
          <div v-if="order.service_kind === 'maintenance_rule' && order.maintenance_rule" class="mt-6 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
            <h3 class="font-semibold text-amber-200">{{ order.maintenance_rule.title }}</h3>
            <p class="mt-3 text-sm text-text dark:text-text-dark">Выбери какие работы выполнены:</p>
            <div class="mt-3 space-y-2">
              <label v-for="task in order.maintenance_rule.tasks" :key="task.id" class="flex items-start gap-3 rounded-lg p-2 hover:bg-slate-800/40">
                <input
                  type="checkbox"
                  :checked="selectedTasks.has(task.id)"
                  :disabled="isCompleted"
                  @change="toggleTask(task)"
                  class="mt-1 h-5 w-5 rounded border-border accent-cyan-400 disabled:opacity-60 dark:border-border-dark"
                />
                <div class="flex-1">
                  <p class="font-medium text-text dark:text-text-dark">{{ task.title }}</p>
                  <p v-if="task.description" class="mt-1 text-xs text-text-muted dark:text-text-muted">{{ task.description }}</p>
                  <p class="mt-1 text-xs text-text-muted dark:text-text-muted">Интервал: {{ task.mileage_interval }} км</p>
                  <p class="mt-1 text-sm font-semibold text-cyan-300">{{ task.unit_price?.toLocaleString() || '0' }} ₸</p>
                </div>
              </label>
            </div>
          </div>

          <h3 class="mt-6 text-base font-semibold text-text dark:text-text-dark">Комментарий выполнения</h3>
          <textarea
            v-model="completionComment"
            :disabled="isCompleted"
            rows="6"
            class="mt-3 w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none focus:border-cyan-400 disabled:opacity-60 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
            placeholder="Что сделано по машине"
          />

          <div class="mt-4 flex gap-2">
            <button
              v-if="order.status === 'new'"
              class="rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300 hover:bg-emerald-500/20"
              @click="acceptOrder"
            >
              Принять заявку
            </button>
            <button
              class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-300 disabled:opacity-50"
              :disabled="saving || isCompleted"
              @click="completeOrder"
            >
              {{ saving ? 'Завершение...' : order.status === 'completed' ? 'Уже завершена' : 'Сделать и закрыть' }}
            </button>
          </div>
        </div>

        <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark">Смета / счет</h2>
          <div class="mt-4 space-y-3">
            <div v-for="(item, index) in estimateItems" :key="index" class="grid grid-cols-[1fr_120px_140px_auto] gap-2">
              <input v-model="item.title" type="text" :disabled="isCompleted" class="rounded-xl border border-border bg-bg px-3 py-2 text-sm disabled:opacity-60 dark:border-border-dark dark:bg-bg-dark" placeholder="Название" />
              <input v-model.number="item.quantity" type="number" min="1" :disabled="isCompleted" class="rounded-xl border border-border bg-bg px-3 py-2 text-sm disabled:opacity-60 dark:border-border-dark dark:bg-bg-dark" placeholder="Кол-во" />
              <input v-model.number="item.unit_price" type="number" min="0" :disabled="isCompleted" class="rounded-xl border border-border bg-bg px-3 py-2 text-sm disabled:opacity-60 dark:border-border-dark dark:bg-bg-dark" placeholder="Цена" />
              <button class="rounded-xl border border-red-500 px-3 py-2 text-sm text-red-500 disabled:opacity-50" :disabled="isCompleted" @click="removeItem(index)">X</button>
            </div>
          </div>
          <button class="mt-3 rounded-xl border border-border px-3 py-2 text-sm hover:border-cyan-400 disabled:opacity-50 dark:border-border-dark" :disabled="isCompleted" @click="addItem">+ Позиция</button>

          <div class="mt-6 rounded-xl border border-border p-4 text-sm dark:border-border-dark">
            Итого: <span class="font-semibold">{{ total.toLocaleString() }} ₸</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

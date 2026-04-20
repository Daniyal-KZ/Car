<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

type CarDto = {
  id: number
  brand: string
  model: string
  year: number | null
  mileage: number | null
}

type MaintenanceTaskDto = {
  id: number
  mileage_interval: number
  title: string
  description?: string | null
  duration_minutes?: number | null
}

type MaintenanceRuleDto = {
  id: number
  title: string
  status: string
  tasks?: MaintenanceTaskDto[]
  execution_status?: string | null
}

type ServiceExecutionDto = {
  id: number
  task_id?: number | null
  performed_at: string
  related_object_type: string
  related_object_id: number
  comment?: string | null
  performed_by?: number | null
  performed_by_username?: string | null
  performed_by_name?: string | null
}

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const carId = computed(() => Number(route.params.id))
const carEndpoint = computed(() => `${config.public.apiBase}/cars/${carId.value}`)
const rulesEndpoint = computed(() => `${config.public.apiBase}/maintenance-rules/car/${carId.value}`)
const executionsEndpoint = computed(() => `${config.public.apiBase}/maintenance-rules/car/${carId.value}/executions`)

const { data: carData, pending: carPending, error: carError } = useFetch<CarDto>(
  () => carEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carEndpoint, () => auth.token],
  }
)

const { data: rulesData, pending: rulesPending, error: rulesError } = useFetch<MaintenanceRuleDto[]>(
  () => rulesEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [rulesEndpoint, () => auth.token],
  }
)

const { data: executionsData } = useFetch<ServiceExecutionDto[]>(
  () => executionsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [executionsEndpoint, () => auth.token],
  }
)

const car = computed(() => carData.value ?? null)
const rules = computed(() => rulesData.value ?? [])
const executions = computed(() => executionsData.value ?? [])
const latestExecution = computed(() => executions.value[0] ?? null)
const executedTaskIds = computed(() => {
  const ids = new Set<number>()
  executions.value.forEach((execution) => {
    if (typeof execution.task_id === 'number') ids.add(execution.task_id)
  })
  return ids
})

const now = computed(() => new Date())
const hasRecentExecution = computed(() => {
  if (!latestExecution.value) return false
  const performedAt = new Date(latestExecution.value.performed_at)
  const diffDays = (now.value.getTime() - performedAt.getTime()) / (1000 * 60 * 60 * 24)
  return diffDays <= 180
})

const dueTaskCount = computed(() => {
  if (car.value?.mileage == null) return 0
  return allTasks.value.filter(task => task.mileage_interval <= car.value!.mileage!).length
})

const plannedTaskCount = computed(() => allTasks.value.length - dueTaskCount.value)

const executionStatusText = computed(() => {
  const statuses = rules.value.map(rule => rule.execution_status)
  if (statuses.includes('overdue') && statuses.includes('planned')) return 'Просрочен (есть план)'
  if (statuses.includes('overdue')) return 'Просрочен'
  if (statuses.includes('not_performed')) return 'Не выполнен'
  if (statuses.includes('planned')) return 'Запланирован'
  if (statuses.some(status => status === 'performed')) return 'Выполнен'
  return 'Нет данных'
})

// Собираем все работы из всех подходящих регламентов
const allTasks = computed(() => {
  const tasks: any[] = []
  rules.value.forEach(rule => {
    rule.tasks?.forEach(task => {
      tasks.push({
        ...task,
        ruleTitle: rule.title
      })
    })
  })
  // Сортируем по пробегу
  return tasks.sort((a, b) => a.mileage_interval - b.mileage_interval)
})

// Группируем работы по пробегу
const groupedTasks = computed(() => {
  const groups: { [key: number]: any[] } = {}
  allTasks.value.forEach(task => {
    if (!groups[task.mileage_interval]) {
      groups[task.mileage_interval] = []
    }
    groups[task.mileage_interval]!.push(task)
  })
  return groups
})

const getMileageGroupStatus = (mileage: number, tasks: any[]) => {
  if (car.value?.mileage == null) return { label: 'План', className: 'bg-slate-500' }

  if (mileage > car.value.mileage) {
    return { label: 'План', className: 'bg-cyan-500' }
  }

  const pendingTasks = tasks.filter(task => !executedTaskIds.value.has(task.id))

  if (!pendingTasks.length) {
    return { label: 'Выполнено', className: 'bg-emerald-500' }
  }

  if (mileage < car.value.mileage) {
    return { label: 'Просрочено', className: 'bg-rose-500' }
  }

  return { label: 'Нужно выполнить', className: 'bg-amber-500' }
}

const nextServiceMileage = computed(() => {
  if (car.value?.mileage == null) return null
  // Находим следующий интервал обслуживания
  const intervals = Object.keys(groupedTasks.value).map(Number).sort((a, b) => a - b)
  const nextInterval = intervals.find(interval => interval > car.value!.mileage!)
  return nextInterval
})

const openMaintenanceList = () => navigateTo('/user/maintenance')

const openBooking = () => {
  const preferredService = allTasks.value[0]?.title || rules.value[0]?.title || 'Регламентное ТО'
  navigateTo({
    path: '/user/booking/new',
    query: {
      carId: String(carId.value),
      service: preferredService,
      serviceKind: 'maintenance_rule',
    },
  })
}

const errText = computed(() => {
  if (carError.value) return "Не удалось загрузить данные автомобиля"
  if (rulesError.value) return "Не удалось загрузить регламент ТО"
  return null
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <div class="mb-6 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">ТО по машине #{{ car?.id ?? carId }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark">Регламентное ТО</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Рекомендации по обслуживанию для конкретного автомобиля.
        </p>
      </div>

      <button
        class="rounded-xl border border-border px-4 py-2 text-sm text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-slate-700 dark:text-text-dark dark:text-slate-300"
        @click="openMaintenanceList"
      >
        Назад
      </button>
    </div>

    <div v-if="carPending || rulesPending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="errText" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      {{ errText }}
    </div>

    <div v-else>
      <div class="mb-6 grid gap-4 md:grid-cols-4">
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ car?.brand ?? '-' }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Год</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ car?.year ?? '-' }}</p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Пробег</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">
            {{ car?.mileage ? car.mileage.toLocaleString() + ' км' : '-' }}
          </p>
        </div>
        <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
          <p class="text-sm text-text-muted dark:text-text-muted">Регламенты</p>
          <p class="mt-2 font-semibold text-text dark:text-text-dark">{{ rules.length }}</p>
        </div>
      </div>

      <div class="grid gap-6 xl:grid-cols-2">
        <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark">Рекомендуемые работы</h2>

          <div v-if="!allTasks.length" class="mt-5 rounded-2xl border border-border bg-bg px-4 py-6 text-sm text-text-muted dark:border-border-dark dark:bg-bg-dark dark:text-text-muted">
            Нет найденных регламентов для этой машины.
          </div>

          <div v-else class="mt-5 space-y-4">
            <div
              v-for="(tasks, mileage) in groupedTasks"
              :key="mileage"
              class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark"
            >
              <div class="mb-3 flex items-center gap-2">
                <h3 class="font-semibold text-text dark:text-text-dark">
                  {{ Number(mileage).toLocaleString() }} км
                </h3>
                <span
                  class="rounded-full px-2 py-1 text-xs text-white"
                  :class="getMileageGroupStatus(Number(mileage), tasks).className"
                >
                  {{ getMileageGroupStatus(Number(mileage), tasks).label }}
                </span>
              </div>

              <div class="space-y-2">
                <div
                  v-for="task in tasks"
                  :key="task.id"
                  class="rounded-xl border border-border bg-bg/50 px-3 py-2 text-sm dark:border-border-dark dark:bg-bg-dark/50"
                >
                  <div class="font-medium text-text dark:text-text-dark">{{ task.title }}</div>
                  <div class="text-text-muted text-xs dark:text-text-muted">{{ task.description || 'Описание отсутствует' }}</div>
                  <div class="text-text-muted text-xs dark:text-text-muted mt-1">
                    {{ task.duration_minutes ? `${task.duration_minutes} мин` : '' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
            <h2 class="text-lg font-semibold text-text dark:text-text-dark">Сводка</h2>

            <div class="mt-5 space-y-4">
              <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
                <p class="text-sm text-text-muted dark:text-text-muted">Следующее ТО</p>
                <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark">
                  {{ nextServiceMileage ? `${nextServiceMileage.toLocaleString()} км` : 'Рекомендации выполнены' }}
                </p>
              </div>

              <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
                <p class="text-sm text-text-muted dark:text-text-muted">Текущее ТО</p>
                <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark">
                  {{ car?.mileage ? `${car.mileage.toLocaleString()} км` : '-' }}
                </p>
              </div>

              <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
                <p class="text-sm text-text-text-muted dark:text-text-muted">Всего работ</p>
                <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark">{{ allTasks.length }}</p>
              </div>

              <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
                <p class="text-sm text-text-muted dark:text-text-muted">Нужно выполнить сейчас</p>
                <p class="mt-2 text-lg font-semibold text-amber-400">{{ dueTaskCount }}</p>
              </div>

              <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
                <p class="text-sm text-text-muted dark:text-text-muted">Плановые пункты</p>
                <p class="mt-2 text-lg font-semibold text-cyan-300">{{ plannedTaskCount }}</p>
              </div>

              <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
                <p class="text-sm text-text-muted dark:text-text-muted">Статус регламентов</p>
                <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark">{{ executionStatusText }}</p>
              </div>

              <div v-if="latestExecution" class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
                <p class="text-sm text-text-muted dark:text-text-muted">Последнее выполнение</p>
                <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark">
                  {{ new Date(latestExecution.performed_at).toLocaleString() }}
                </p>
                <p class="mt-1 text-sm text-text-muted dark:text-text-muted">
                  {{ latestExecution.performed_by_name || latestExecution.performed_by_username || latestExecution.performed_by }}
                </p>
              </div>
            </div>

            <div class="mt-6">
              <p class="mb-3 text-xs text-text-muted dark:text-text-muted">
                Логика статусов: "Нужно выполнить" = пробег достигнут и фиксации нет/устарела, "Выполнено" = есть свежая фиксация, "План" = пробег еще не достигнут.
              </p>
              <h3 class="text-base font-semibold text-text dark:text-text-dark">История выполнений</h3>
              <div v-if="!executions.length" class="mt-3 text-sm text-text-muted dark:text-text-muted">
                Пока нет записей о выполнении.
              </div>
              <div v-else class="mt-3 space-y-2">
                <div
                  v-for="execution in executions"
                  :key="execution.id"
                  class="rounded-xl border border-border bg-bg p-3 text-sm dark:border-border-dark dark:bg-bg-dark"
                >
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="font-medium text-text dark:text-text-dark">{{ new Date(execution.performed_at).toLocaleString() }}</span>
                    <span class="text-text-muted dark:text-text-muted">{{ execution.related_object_type }} #{{ execution.related_object_id }}</span>
                  </div>
                  <p class="mt-1 text-text-muted dark:text-text-muted">{{ execution.comment || 'Без комментария' }}</p>
                </div>
              </div>
            </div>
          </div>

          <button
            class="w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
            @click="openBooking"
          >
            Записаться на обслуживание
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
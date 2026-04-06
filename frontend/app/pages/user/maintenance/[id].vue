<script setup lang="ts">
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const carId = computed(() => Number(route.params.id))
const carEndpoint = computed(() => `${config.public.apiBase}/cars/${carId.value}`)
const rulesEndpoint = computed(() => `${config.public.apiBase}/maintenance-rules/car/${carId.value}`)

const { data: carData, pending: carPending, error: carError } = useFetch<Car>(
  () => carEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carEndpoint, auth.token],
  }
)

const { data: rulesData, pending: rulesPending, error: rulesError } = useFetch(
  () => rulesEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [rulesEndpoint, auth.token],
  }
)

const car = computed(() => carData.value)
const rules = computed(() => rulesData.value ?? [])

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
    groups[task.mileage_interval].push(task)
  })
  return groups
})

const nextServiceMileage = computed(() => {
  if (!car.value?.mileage) return null
  // Находим следующий интервал обслуживания
  const intervals = Object.keys(groupedTasks.value).map(Number).sort((a, b) => a - b)
  const nextInterval = intervals.find(interval => interval > car.value.mileage)
  return nextInterval
})

const openMaintenanceList = () => navigateTo('/user/maintenance')

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
                  v-if="car?.mileage && Number(mileage) <= car.mileage"
                  class="rounded-full bg-green-500 px-2 py-1 text-xs text-white"
                >
                  Выполнено
                </span>
                <span
                  v-else-if="car?.mileage && Number(mileage) > car.mileage"
                  class="rounded-full bg-cyan-500 px-2 py-1 text-xs text-white"
                >
                  Рекомендуется
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
            </div>
          </div>

          <button
            class="w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
            @click="navigateTo('/user/booking/new')"
          >
            Записаться на обслуживание
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
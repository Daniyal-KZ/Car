<script setup lang="ts">
definePageMeta({ middleware: ["auth", "role"] })

type MaintenanceRulePayload = {
  title: string
  brand: string
  model: string
  year_from?: number
  year_to?: number
  mileage_from?: number
  mileage_to?: number
  status: string
  notes?: string
  tasks: Array<{
    mileage_interval: number
    title: string
    description?: string
    duration_minutes?: number
  }>
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const loading = ref(false)
const router = useRouter()

const defaultTemplateTasks: MaintenanceRulePayload['tasks'] = [
  { mileage_interval: 10000, title: 'Замена моторного масла', description: 'Замена масла и проверка уровня', duration_minutes: 30 },
  { mileage_interval: 10000, title: 'Замена масляного фильтра', description: 'Установка нового фильтра', duration_minutes: 20 },
  { mileage_interval: 20000, title: 'Проверка тормозной системы', description: 'Осмотр колодок, дисков и суппортов', duration_minutes: 40 },
  { mileage_interval: 20000, title: 'Замена салонного фильтра', description: 'Профилактическая замена фильтра салона', duration_minutes: 20 },
  { mileage_interval: 30000, title: 'Проверка подвески', description: 'Диагностика элементов передней и задней подвески', duration_minutes: 45 },
  { mileage_interval: 40000, title: 'Замена воздушного фильтра', description: 'Замена воздушного фильтра двигателя', duration_minutes: 20 },
  { mileage_interval: 60000, title: 'Замена свечей зажигания', description: 'Комплексная замена свечей', duration_minutes: 35 },
  { mileage_interval: 80000, title: 'Замена тормозной жидкости', description: 'Обновление тормозной жидкости по регламенту', duration_minutes: 45 },
]

// Reactive form data
const formData = reactive<MaintenanceRulePayload>({
  title: '',
  brand: '',
  model: '',
  status: 'draft',
  tasks: []
})

// Task management
const addTask = () => {
  formData.tasks.push({
    mileage_interval: 0,
    title: '',
    description: '',
    duration_minutes: undefined
  })
}

const removeTask = (index: number) => {
  formData.tasks.splice(index, 1)
}

const fillTemplate = () => {
  formData.tasks = defaultTemplateTasks.map(task => ({ ...task }))
}

const submit = async (payload: MaintenanceRulePayload) => {
  loading.value = true
  try {
    const normalizedPayload = {
      ...payload,
      tasks: [...payload.tasks]
        .filter(task => task.title.trim().length > 0)
        .sort((a, b) => a.mileage_interval - b.mileage_interval),
    }

    await $fetch(`${config.public.apiBase}/maintenance-rules`, {
      method: "POST",
      body: normalizedPayload,
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : "",
      },
    })

    await router.push('/admin/maintenance-rules')
  } catch (error) {
    console.error('Error creating maintenance rule:', error)
    alert('Ошибка при создании регламента')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <NuxtLink
        to="/admin/maintenance-rules"
        class="text-sm text-text-muted hover:text-cyan-400 dark:text-text-muted"
      >
        ← Назад к регламентам
      </NuxtLink>
      <h1 class="mt-2 text-3xl font-bold text-text dark:text-text-dark">Создание регламента ТО</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Создайте новый регламент технического обслуживания для конкретной марки и модели автомобиля.
      </p>
    </div>

    <div class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
      <form @submit.prevent="submit(formData)" class="space-y-6">
        <!-- Основная информация -->
        <div class="grid gap-6 md:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Название регламента *
            </label>
            <input
              v-model="formData.title"
              type="text"
              required
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              placeholder="Например: ТО-1 для Toyota Camry"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Статус
            </label>
            <select
              v-model="formData.status"
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
            >
              <option value="draft">Черновик</option>
              <option value="active">Активный</option>
            </select>
          </div>
        </div>

        <!-- Марка и модель -->
        <div class="grid gap-6 md:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Марка автомобиля *
            </label>
            <input
              v-model="formData.brand"
              type="text"
              required
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              placeholder="Toyota"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Модель автомобиля *
            </label>
            <input
              v-model="formData.model"
              type="text"
              required
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              placeholder="Camry"
            />
          </div>
        </div>

        <!-- Диапазоны -->
        <div class="grid gap-6 md:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Год выпуска (от)
            </label>
            <input
              v-model.number="formData.year_from"
              type="number"
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              placeholder="2020"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Год выпуска (до)
            </label>
            <input
              v-model.number="formData.year_to"
              type="number"
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              placeholder="2030"
            />
          </div>
        </div>

        <div class="grid gap-6 md:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Пробег (от, км)
            </label>
            <input
              v-model.number="formData.mileage_from"
              type="number"
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              placeholder="30000"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
              Пробег (до, км)
            </label>
            <input
              v-model.number="formData.mileage_to"
              type="number"
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              placeholder="50000"
            />
          </div>
        </div>

        <!-- Заметки -->
        <div>
          <label class="block text-sm font-medium text-text dark:text-text-dark mb-2">
            Заметки
          </label>
          <textarea
            v-model="formData.notes"
            rows="3"
            class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
            placeholder="Дополнительная информация о регламенте"
          />
        </div>

        <!-- Задачи -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-text dark:text-text-dark">Работы по регламенту</h3>
            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="fillTemplate"
                class="rounded-xl border border-emerald-500/60 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300 transition hover:bg-emerald-500/20"
              >
                Заполнить шаблон (8 пунктов)
              </button>
              <button
                type="button"
                @click="addTask"
                class="rounded-xl border border-border px-4 py-2 text-sm text-text transition hover:border-cyan-400 hover:text-cyan-300 dark:border-border-dark dark:text-text-dark"
              >
                + Добавить работу
              </button>
            </div>
          </div>

          <div v-if="!formData.tasks.length" class="rounded-2xl border border-border bg-bg p-6 text-center dark:border-border-dark dark:bg-bg-dark">
            <p class="text-text-muted dark:text-text-muted">Нет добавленных работ</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="(task, index) in formData.tasks"
              :key="index"
              class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark"
            >
              <div class="flex items-start justify-between gap-4 mb-4">
                <div class="flex-1 grid gap-4 md:grid-cols-2">
                  <div>
                    <input
                      v-model.number="task.mileage_interval"
                      type="number"
                      placeholder="Пробег (км)"
                      class="w-full rounded-xl border border-border bg-bg px-3 py-2 text-sm text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
                    />
                  </div>
                  <input
                    v-model="task.title"
                    type="text"
                    placeholder="Название работы"
                    class="w-full rounded-xl border border-border bg-bg px-3 py-2 text-sm text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
                  />
                  <div class="flex gap-2">
                    <input
                      v-model.number="task.duration_minutes"
                      type="number"
                      placeholder="Время (мин)"
                      class="flex-1 rounded-xl border border-border bg-bg px-3 py-2 text-sm text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
                    />
                  </div>
                </div>
                <button
                  type="button"
                  @click="removeTask(index)"
                  class="rounded-xl border border-red-500 px-3 py-2 text-sm text-red-500 transition hover:bg-red-500 hover:text-white"
                >
                  Удалить
                </button>
              </div>

              <textarea
                v-model="task.description"
                placeholder="Описание работы"
                rows="2"
                class="w-full rounded-xl border border-border bg-bg px-3 py-2 text-sm text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
              />
            </div>
          </div>
        </div>

        <!-- Кнопки -->
        <div class="flex gap-4 pt-6">
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
          >
            {{ loading ? 'Создание...' : 'Создать регламент' }}
          </button>

          <NuxtLink
            to="/admin/maintenance-rules"
            class="flex-1 rounded-2xl border border-border bg-bg px-5 py-3 text-center text-sm font-semibold text-text transition hover:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
          >
            Отмена
          </NuxtLink>
        </div>
      </form>
    </div>
  </div>
</template>
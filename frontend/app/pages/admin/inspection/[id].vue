<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

type InspectionEntry = {
  id: number
  car_id: number
  type: string
  mileage: number
  description: string
  order_number?: string | null
  created_at: string
  car?: {
    brand: string
    model: string
    year: number | null
    mileage: number | null
  } | null
}

const checklist = [
  'Проверка тормозной системы',
  'Осмотр подвески',
  'Проверка жидкостей',
  'Осмотр шин и дисков',
  'Проверка освещения',
  'Проверка рулевого управления',
  'Проверка аккумулятора',
  'Осмотр приводных ремней',
  'Проверка состояния свечей',
  'Проверка утечек по двигателю',
  'Проверка системы охлаждения',
  'Проверка дворников и омывателя',
]

const inspectionId = computed(() => Number(route.params.id))
const endpoint = computed(() => `${config.public.apiBase}/service-book/admin/entry/${inspectionId.value}`)

const { data, pending, error, refresh } = useFetch<InspectionEntry>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const form = reactive({
  mileage: 0,
  conclusion: 'Требуется обслуживание',
  comment: '',
  passed: [] as string[],
})

const saving = ref(false)
const saveError = ref<string | null>(null)

watch(
  () => data.value,
  (entry) => {
    if (!entry) return
    form.mileage = entry.mileage

    try {
      const parsed = JSON.parse(entry.description || '{}')
      form.conclusion = parsed.conclusion || 'Требуется обслуживание'
      form.comment = parsed.comment || ''
      form.passed = Array.isArray(parsed.checklist_passed)
        ? parsed.checklist_passed.filter((x: unknown) => typeof x === 'string')
        : []
    } catch {
      form.conclusion = 'Требуется обслуживание'
      form.comment = ''
      form.passed = []
    }
  },
  { immediate: true }
)

const failedChecklist = computed(() => checklist.filter(item => !form.passed.includes(item)))

const saveInspection = async () => {
  if (!data.value?.car_id) return

  saving.value = true
  saveError.value = null
  try {
    await $fetch(`${config.public.apiBase}/service-book/admin/entry/${inspectionId.value}`, {
      method: 'PUT',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
      body: {
        car_id: data.value.car_id,
        mileage: Number(form.mileage || 0),
        checklist_passed: form.passed,
        checklist_failed: failedChecklist.value,
        conclusion: form.conclusion,
        comment: form.comment,
        order_number: data.value.order_number || undefined,
      },
    })

    await refresh()
  } catch (err) {
    console.error(err)
    saveError.value = 'Не удалось сохранить техосмотр.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !data" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить техосмотр.
    </div>

    <div v-else>
      <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Осмотр {{ data.order_number || `I-${data.id}` }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Тех. осмотр автомобиля</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/admin/inspection')"
      >
        Назад
      </button>
      </div>

      <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ data.car?.brand }} {{ data.car?.model }}</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Год</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ data.car?.year || '-' }}</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Пробег</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ Number(data.mileage || 0).toLocaleString() }} км</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Пунктов в чек-листе</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ checklist.length }}</p>
      </div>
      </div>

      <div class="grid gap-6 xl:grid-cols-[1.2fr_0.9fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Чек-лист осмотра</h2>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Отметьте исправные пункты. Неотмеченные уйдут в "нужно исправить".</p>

        <div class="mt-5 space-y-3">
          <label
            v-for="item in checklist"
            :key="item"
            class="flex items-center gap-3 rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4 text-text dark:text-text-dark"
          >
            <input v-model="form.passed" :value="item" type="checkbox" class="h-4 w-4" />
            <span>{{ item }}</span>
          </label>
        </div>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Заключение</h2>

        <div v-if="saveError" class="mt-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
          {{ saveError }}
        </div>

        <div class="mt-5 space-y-4">
          <input
            v-model.number="form.mileage"
            type="number"
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
            placeholder="Пробег на момент осмотра"
          />

          <select v-model="form.conclusion" class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none">
            <option>Исправно</option>
            <option>Требуется обслуживание</option>
            <option>Нужен ремонт</option>
          </select>

          <textarea
            v-model="form.comment"
            rows="8"
            placeholder="Комментарий по результатам осмотра..."
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />

          <div class="rounded-xl border border-border p-3 text-sm text-text-muted dark:border-border-dark dark:text-text-muted">
            Исправно: {{ form.passed.length }} • Требует внимания: {{ failedChecklist.length }}
          </div>

          <button
            class="w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
            :disabled="saving"
            @click="saveInspection"
          >
            {{ saving ? 'Сохранение...' : 'Сохранить осмотр' }}
          </button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
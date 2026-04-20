<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
})

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
  } | null
}

type CarDto = {
  id: number
  brand: string
  model: string
  year: number | null
  mileage: number | null
}

const config = useRuntimeConfig()
const auth = useAuthStore()
const { t, locale } = useI18n()
const endpoint = computed(() => `${config.public.apiBase}/service-book/admin/inspection`)

const { data, pending, error } = useFetch<InspectionEntry[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [endpoint, () => auth.token],
  }
)

const inspections = computed(() => data.value ?? [])

const carsEndpoint = computed(() => `${config.public.apiBase}/cars/admin/all`)
const { data: carsData } = useFetch<CarDto[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carsEndpoint, () => auth.token],
  }
)

const cars = computed(() => carsData.value ?? [])
const selectedCarId = ref<number | null>(null)
const creating = ref(false)

const parseConclusion = (description: string) => {
  try {
    const parsed = JSON.parse(description)
    return parsed.conclusion || 'Без заключения'
  } catch {
    return 'Без заключения'
  }
}

const statusChip = (description: string) => {
  const conclusion = parseConclusion(description).toLowerCase()
  if (conclusion.includes('исправ')) return { label: 'Исправно', className: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' }
  if (conclusion.includes('ремонт')) return { label: 'Нужен ремонт', className: 'border-rose-500/30 bg-rose-500/10 text-rose-300' }
  return { label: 'Требуется обслуживание', className: 'border-amber-500/30 bg-amber-500/10 text-amber-300' }
}

const openItem = (id: number) => navigateTo(`/admin/inspection/${id}`)

const createInspection = async () => {
  if (!selectedCarId.value) return

  creating.value = true
  try {
    const created = await $fetch<{ id: number }>(`${config.public.apiBase}/service-book/admin/inspection`, {
      method: 'POST',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
      body: {
        car_id: selectedCarId.value,
        conclusion: 'Требуется обслуживание',
        checklist_passed: [],
        checklist_failed: [],
        comment: '',
      },
    })

    await navigateTo(`/admin/inspection/${created.id}`)
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Тех. осмотр</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Список автомобилей на техосмотр. Открывайте запись и заполняйте чек-лист отдельно по каждой машине.
      </p>

      <div class="mt-4 flex flex-col gap-2 rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark md:flex-row md:items-center">
        <select
          v-model.number="selectedCarId"
          class="w-full rounded-xl border border-border bg-bg px-4 py-2 text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
        >
          <option :value="null" disabled>Выберите авто для нового техосмотра</option>
          <option v-for="car in cars" :key="car.id" :value="car.id">
            {{ car.brand }} {{ car.model }} ({{ car.year || '-' }})
          </option>
        </select>
        <button
          class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
          :disabled="!selectedCarId || creating"
          @click="createInspection"
        >
          {{ creating ? 'Создание...' : '+ Новый техосмотр' }}
        </button>
      </div>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить техосмотры.
    </div>

    <div v-else-if="!inspections.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Техосмотров пока нет.
    </div>

    <div v-else class="space-y-4">
      <button
        v-for="item in inspections"
        :key="item.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400"
        @click="openItem(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">
                {{ item.order_number || `I-${item.id}` }} — {{ item.car?.brand }} {{ item.car?.model }}
              </h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusChip(item.description).className">
                {{ statusChip(item.description).label }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
              Пробег: {{ item.mileage.toLocaleString() }} км
            </p>
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ parseConclusion(item.description) }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
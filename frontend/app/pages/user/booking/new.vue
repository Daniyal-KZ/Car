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

type ServiceCatalogItem = {
  code: string
  name: string
  description: string
}

type ServiceOrderDto = {
  id: number
}

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const loading = ref(false)
const submitError = ref<string | null>(null)

const formData = reactive({
  car_id: null as number | null,
  service_kind: '',
  service_name: '',
  appointment_date: '',
  appointment_time: '',
  comment: '',
})

const carsEndpoint = computed(() => `${config.public.apiBase}/cars`)

const { data: carsData, pending: carsPending, error: carsError } = useFetch<CarDto[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carsEndpoint, () => auth.token],
  }
)

const cars = computed(() => carsData.value ?? [])
const serviceCatalogEndpoint = computed(() => `${config.public.apiBase}/service-orders/catalog`)
const { data: serviceCatalogData } = useFetch<ServiceCatalogItem[]>(
  () => serviceCatalogEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [serviceCatalogEndpoint, () => auth.token],
  }
)

const services = computed(() => serviceCatalogData.value ?? [
  { code: 'maintenance_rule', name: 'Регламентное ТО', description: 'Плановое обслуживание по регламенту' },
  { code: 'diagnostics', name: 'Диагностика', description: 'Комплексная диагностика автомобиля' },
  { code: 'technical_inspection', name: 'Технический осмотр', description: 'Проверка автомобиля по требованиям техосмотра' },
  { code: 'damage_assessment', name: 'Осмотр повреждений', description: 'Осмотр и оценка повреждений' },
])

const selectedService = computed(() => services.value.find(service => service.code === formData.service_kind) ?? null)

const selectService = (service: ServiceCatalogItem) => {
  formData.service_kind = service.code
  formData.service_name = service.name
}

const prefillServiceFromQuery = () => {
  const rawService = String(route.query.service || '').trim()
  const rawServiceKind = String(route.query.serviceKind || '').trim()
  const matched = services.value.find(service => service.code === rawServiceKind || service.code === rawService || service.name === rawService)
  if (matched) {
    selectService(matched)
    return
  }

  if (!formData.service_kind && services.value.length) {
    selectService(services.value[0]!)
  }
}

watch(
  cars,
  (list) => {
    if (!list.length || formData.car_id) return

    const prefilledCarId = Number(route.query.carId || 0)
    const hasPrefilled = prefilledCarId && list.some(car => car.id === prefilledCarId)
    formData.car_id = hasPrefilled ? prefilledCarId : list[0]!.id
    prefillServiceFromQuery()
  },
  { immediate: true }
)

const submit = async () => {
  submitError.value = null
  if (!formData.car_id || !formData.service_kind || !formData.service_name || !formData.appointment_date || !formData.appointment_time) {
    submitError.value = 'Заполните автомобиль, услугу, дату и время.'
    return
  }

  loading.value = true
  try {
    const created = await $fetch<ServiceOrderDto>(`${config.public.apiBase}/service-orders`, {
      method: 'POST',
      body: {
        car_id: formData.car_id,
        service_kind: formData.service_kind,
        service_name: formData.service_name,
        requested_comment: [
          `Дата: ${formData.appointment_date}`,
          `Время: ${formData.appointment_time}`,
          formData.comment.trim() ? `Комментарий: ${formData.comment.trim()}` : '',
        ]
          .filter(Boolean)
          .join(' | '),
        scheduled_at: `${formData.appointment_date}T${formData.appointment_time}:00`,
      },
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
    })

    await navigateTo(`/user/booking/${created.id}`)
  } catch (error) {
    console.error('Error creating booking:', error)
    submitError.value = 'Не удалось создать запись. Попробуйте еще раз.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Новая запись в сервис</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Выберите машину, услугу и удобное время посещения.
      </p>
    </div>

    <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
      <div v-if="submitError" class="mb-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
        {{ submitError }}
      </div>

      <div v-if="carsPending" class="mb-4 rounded-xl border border-border p-3 text-sm text-text-muted dark:border-border-dark dark:text-text-muted">
        Загрузка автомобилей...
      </div>

      <div v-else-if="carsError || !cars.length" class="mb-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
        Нет доступных автомобилей для записи.
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Автомобиль</label>
          <select
            v-model.number="formData.car_id"
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          >
            <option :value="null" disabled>Выберите автомобиль</option>
            <option v-for="car in cars" :key="car.id" :value="car.id">
              {{ car.brand }} {{ car.model }} ({{ car.year ?? '-' }})
            </option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Услуга</label>
          <div class="grid gap-3 md:grid-cols-2">
            <button
              v-for="service in services"
              :key="service.code"
              type="button"
              class="rounded-2xl border p-4 text-left transition"
              :class="formData.service_kind === service.code ? 'border-cyan-400 bg-cyan-500/10' : 'border-border bg-bg hover:border-cyan-400 dark:border-slate-700 dark:bg-bg-dark'"
              @click="selectService(service)"
            >
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-base font-semibold text-text dark:text-text-dark">{{ service.name }}</p>
                  <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ service.description }}</p>
                </div>
                <span class="rounded-full border px-3 py-1 text-xs" :class="formData.service_kind === service.code ? 'border-cyan-400 bg-cyan-500/10 text-cyan-300' : 'border-slate-500/30 bg-slate-500/10 text-slate-300'">
                  {{ service.code }}
                </span>
              </div>
            </button>
          </div>
          <p class="mt-2 text-xs text-text-muted dark:text-text-muted">
            Выберите нужную услугу карточкой выше.
          </p>
        </div>

        <div>
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Дата</label>
          <input
            v-model="formData.appointment_date"
            type="date"
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />
        </div>

        <div>
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Время</label>
          <input
            v-model="formData.appointment_time"
            type="time"
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />
        </div>

        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Комментарий</label>
          <textarea
            v-model="formData.comment"
            rows="5"
            placeholder="Комментарий к визиту..."
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />
        </div>
      </div>

      <div class="mt-6 flex gap-3">
        <button
          class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
          :disabled="loading || !cars.length"
          @click="submit"
        >
          {{ loading ? 'Создание...' : 'Создать запись' }}
        </button>
        <button
          class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
          @click="navigateTo('/user/booking')"
        >
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>
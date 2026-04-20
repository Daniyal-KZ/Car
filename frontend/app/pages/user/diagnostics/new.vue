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

type ServiceOrderDto = {
  id: number
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const symptoms = [
  "Стук в подвеске",
  "Вибрация на скорости",
  "Горит Check Engine",
  "Шум при торможении",
]

const form = reactive({
  car_id: null as number | null,
  description: '',
})

const loading = ref(false)
const errText = ref('')

const carsEndpoint = computed(() => `${config.public.apiBase}/cars`)
const { data: carsData } = useFetch<CarDto[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [carsEndpoint, () => auth.token],
  }
)

const cars = computed(() => carsData.value ?? [])

watch(cars, (list) => {
  if (!form.car_id && list.length) {
    form.car_id = list[0]!.id
  }
}, { immediate: true })

const addSymptom = (value: string) => {
  if (!form.description.trim()) {
    form.description = value
    return
  }

  if (!form.description.includes(value)) {
    form.description = `${form.description.trim()}\n- ${value}`
  }
}

const submit = async () => {
  errText.value = ''
  if (!form.car_id || !form.description.trim()) {
    errText.value = 'Выберите автомобиль и опишите симптомы.'
    return
  }

  loading.value = true
  try {
    const created = await $fetch<ServiceOrderDto>(`${config.public.apiBase}/service-orders`, {
      method: 'POST',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
      body: {
        car_id: form.car_id,
        service_name: 'Диагностика',
        service_kind: 'diagnostics',
        requested_comment: form.description,
      },
    })

    await navigateTo(`/user/diagnostics/${created.id}`)
  } catch (e) {
    console.error(e)
    errText.value = 'Не удалось отправить заявку.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Новая заявка на диагностику</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Опишите проблему и отправьте автомобиль на диагностику.
      </p>
    </div>

    <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
      <div v-if="errText" class="mb-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
        {{ errText }}
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Автомобиль</label>
          <select v-model.number="form.car_id" class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none">
            <option :value="null" disabled>Выберите автомобиль</option>
            <option v-for="car in cars" :key="car.id" :value="car.id">{{ car.brand }} {{ car.model }} ({{ car.year || '-' }})</option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Описание проблемы</label>
          <textarea
            v-model="form.description"
            rows="7"
            placeholder="Опишите симптомы..."
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />
        </div>
      </div>

      <div class="mt-6">
        <p class="mb-3 text-sm text-text-muted dark:text-text-muted">Быстрые симптомы</p>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="item in symptoms"
            :key="item"
            class="rounded-full border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
            @click="addSymptom(item)"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <div class="mt-6 flex gap-3">
        <button class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50" :disabled="loading" @click="submit">
          {{ loading ? 'Отправка...' : 'Отправить заявку' }}
        </button>
        <button
          class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
          @click="navigateTo('/user/diagnostics')"
        >
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>
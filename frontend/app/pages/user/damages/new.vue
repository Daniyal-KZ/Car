<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

type CarDto = {
  id: number
  brand: string
  model: string
  year: number | null
}

type DamageReportDto = {
  id: number
}

const config = useRuntimeConfig()
const auth = useAuthStore()
const route = useRoute()

const damageTypes = ["Царапина", "Вмятина", "Скол", "Трещина", "Разрыв", "Другое"]

const form = reactive({
  car_id: null as number | null,
  damage_type: "Царапина",
  title: '',
  description: '',
})

const selectedFiles = ref<File[]>([])
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

onMounted(() => {
  const qType = String(route.query.damageType || '').trim()
  const qTitle = String(route.query.title || '').trim()
  const qDescription = String(route.query.description || '').trim()

  if (qType && damageTypes.includes(qType)) {
    form.damage_type = qType
  }
  if (qTitle) {
    form.title = qTitle
  }
  if (qDescription) {
    form.description = qDescription
  }
})

const onFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  selectedFiles.value = Array.from(input.files || [])
}

const submit = async () => {
  errText.value = ''
  if (!form.car_id || !form.title.trim()) {
    errText.value = 'Выберите авто и заполните заголовок.'
    return
  }

  if (!selectedFiles.value.length) {
    errText.value = 'Добавьте хотя бы одно фото повреждения.'
    return
  }

  loading.value = true
  try {
    const report = await $fetch<DamageReportDto>(`${config.public.apiBase}/damage-reports`, {
      method: 'POST',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
      body: {
        car_id: form.car_id,
        title: form.title,
        damage_type: form.damage_type,
        description: form.description,
      },
    })

    if (selectedFiles.value.length) {
      const multipart = new FormData()
      selectedFiles.value.forEach(file => multipart.append('files', file))
      await $fetch(`${config.public.apiBase}/damage-reports/${report.id}/photos`, {
        method: 'POST',
        headers: {
          Authorization: auth.token ? `Bearer ${auth.token}` : '',
        },
        body: multipart,
      })
    }

    await navigateTo(`/user/damages/${report.id}`)
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
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Новая заявка на осмотр повреждений</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Загрузите фото и отправьте машину на оценку повреждений.
      </p>
    </div>

    <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
      <div v-if="errText" class="mb-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
        {{ errText }}
      </div>
      <div class="grid gap-4">
        <div>
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Автомобиль</label>
          <select v-model.number="form.car_id" class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none">
            <option :value="null" disabled>Выберите автомобиль</option>
            <option v-for="car in cars" :key="car.id" :value="car.id">{{ car.brand }} {{ car.model }} ({{ car.year || '-' }})</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Кратко о повреждении</label>
          <input v-model="form.title" type="text" placeholder="Например: Повреждение переднего бампера" class="w-full rounded-2xl border border-border px-4 py-3 text-text outline-none dark:border-slate-700 dark:bg-bg-dark dark:text-text-dark" />
        </div>

        <div class="rounded-3xl border border-dashed border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ px-6 py-16 text-center">
          <p class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Зона загрузки фото</p>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Прикрепите фото повреждений</p>
          <input class="mt-4" type="file" multiple accept="image/*" @change="onFileSelect" />
          <p v-if="selectedFiles.length" class="mt-2 text-xs text-text-muted dark:text-text-muted">Выбрано файлов: {{ selectedFiles.length }}</p>
        </div>
      </div>

      <div class="mt-6">
        <p class="mb-3 text-sm text-text-muted dark:text-text-muted">Тип повреждения</p>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="item in damageTypes"
            :key="item"
            class="rounded-full border px-4 py-2 text-sm transition"
            :class="form.damage_type === item ? 'border-cyan-500 bg-cyan-500/10 text-cyan-300' : 'border-border text-text dark:border-slate-700 dark:text-slate-300'"
            @click="form.damage_type = item"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <div class="mt-6">
        <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Описание</label>
        <textarea v-model="form.description" rows="5" placeholder="Опишите детали повреждения" class="w-full rounded-2xl border border-border px-4 py-3 text-text outline-none dark:border-slate-700 dark:bg-bg-dark dark:text-text-dark" />
      </div>

      <div class="mt-6 flex gap-3">
        <button class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50" :disabled="loading" @click="submit">
          {{ loading ? 'Отправка...' : 'Отправить заявку' }}
        </button>
        <button
          class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
          @click="navigateTo('/user/damages')"
        >
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>
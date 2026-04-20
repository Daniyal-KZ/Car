<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

type DamagePhoto = {
  id: number
  file_path: string
  file_name: string
}

type DamageReport = {
  id: number
  title: string
  damage_type: string
  description?: string | null
  status: string
  severity?: string | null
  mechanic_analysis?: string | null
  recommendation?: string | null
  estimated_cost?: number | null
  car?: {
    brand: string
    model: string
  } | null
  requester?: {
    username: string
  } | null
  photos: DamagePhoto[]
}

const endpoint = computed(() => `${config.public.apiBase}/damage-reports/${route.params.id}`)
const { data, pending, error, refresh } = useFetch<DamageReport>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const item = computed(() => data.value)

const form = reactive({
  severity: '',
  mechanic_analysis: '',
  recommendation: '',
  estimated_cost: null as number | null,
})

watch(item, (val) => {
  if (!val) return
  form.severity = val.severity || ''
  form.mechanic_analysis = val.mechanic_analysis || ''
  form.recommendation = val.recommendation || ''
  form.estimated_cost = val.estimated_cost ?? null
}, { immediate: true })

const saving = ref(false)
const saveError = ref('')

const photoUrl = (path: string) => `${config.public.apiBase}${path}`

const submit = async () => {
  saveError.value = ''
  if (!form.mechanic_analysis.trim() || !form.recommendation.trim()) {
    saveError.value = 'Заполните анализ и рекомендации.'
    return
  }

  saving.value = true
  try {
    await $fetch(`${config.public.apiBase}/damage-reports/${route.params.id}/analysis`, {
      method: 'PUT',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : '',
      },
      body: {
        severity: form.severity || null,
        mechanic_analysis: form.mechanic_analysis,
        recommendation: form.recommendation,
        estimated_cost: form.estimated_cost,
        estimate_items: form.estimated_cost
          ? [
              {
                title: 'Восстановление повреждений',
                quantity: 1,
                unit_price: form.estimated_cost,
              },
            ]
          : [],
      },
    })

    await refresh()
  } catch (e) {
    console.error(e)
    saveError.value = 'Не удалось сохранить результат.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Заявка DR-{{ route.params.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Повреждения автомобиля</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/admin/defects')"
      >
        Назад
      </button>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error || !item" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить заявку.
    </div>

    <div v-else class="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Фото автомобиля</h2>

        <div v-if="item.photos?.length" class="mt-5 grid gap-3 sm:grid-cols-2">
          <img
            v-for="photo in item.photos"
            :key="photo.id"
            :src="photoUrl(photo.file_path)"
            :alt="photo.file_name"
            class="h-56 w-full rounded-2xl object-cover"
          />
        </div>
        <div v-else class="mt-5 flex min-h-[220px] items-center justify-center rounded-3xl border border-dashed border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/">
          <p class="text-sm text-text-muted dark:text-text-muted">Фото отсутствуют</p>
        </div>
      </div>

      <div class="space-y-6">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Данные заявки</h2>

          <div class="mt-5 space-y-3">
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Клиент</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.requester?.username || '-' }}</p>
            </div>
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.car?.brand }} {{ item.car?.model }}</p>
            </div>
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Тип</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.damage_type }}</p>
            </div>
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Описание</p>
              <p class="mt-2 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ item.description || '-' }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Анализ механика</h2>

          <div v-if="saveError" class="mt-4 rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">
            {{ saveError }}
          </div>

          <div class="mt-5 space-y-3">
            <input
              v-model="form.severity"
              type="text"
              placeholder="Степень повреждения (например: средняя)"
              class="w-full rounded-2xl border border-border dark:border-slate-700 bg-bg px-4 py-3 text-text outline-none dark:bg-bg-dark dark:text-text-dark"
            />

            <textarea
              v-model="form.mechanic_analysis"
              rows="5"
              placeholder="Что увидел механик"
              class="w-full rounded-2xl border border-border dark:border-slate-700 bg-bg px-4 py-3 text-text outline-none dark:bg-bg-dark dark:text-text-dark"
            />

            <textarea
              v-model="form.recommendation"
              rows="4"
              placeholder="Что нужно делать"
              class="w-full rounded-2xl border border-border dark:border-slate-700 bg-bg px-4 py-3 text-text outline-none dark:bg-bg-dark dark:text-text-dark"
            />

            <input
              v-model.number="form.estimated_cost"
              type="number"
              min="0"
              placeholder="Оценочная цена, KZT"
              class="w-full rounded-2xl border border-border dark:border-slate-700 bg-bg px-4 py-3 text-text outline-none dark:bg-bg-dark dark:text-text-dark"
            />
          </div>

          <button class="mt-4 w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50" :disabled="saving" @click="submit">
            {{ saving ? 'Сохранение...' : 'Сохранить результат' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
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
  photos: DamagePhoto[]
}

const endpoint = computed(() => `${config.public.apiBase}/damage-reports/${route.params.id}`)
const { data, pending, error } = useFetch<DamageReport>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const item = computed(() => data.value)

const statusLabel = computed(() => {
  const status = item.value?.status
  if (status === 'new') return 'Новая'
  if (status === 'in_review') return 'В обработке'
  if (status === 'analyzed') return 'Осмотрено'
  return status || '-'
})

const photoUrl = (path: string) => `${config.public.apiBase}${path}`
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Заявка DR-{{ route.params.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Результат осмотра повреждений</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/damages')"
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

    <div v-else class="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Фото и зона повреждения</h2>

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
          <p class="text-sm text-text-muted dark:text-text-muted">Фото не загружены</p>
        </div>
      </div>

      <div class="space-y-6">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Сводка</h2>

          <div class="mt-5 space-y-4">
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.car?.brand }} {{ item.car?.model }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Статус</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ statusLabel }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Степень</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.severity || '-' }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Оценочная сумма</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.estimated_cost ? `${item.estimated_cost.toLocaleString()} KZT` : 'Пока не определена' }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Комментарий</h2>
          <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">{{ item.mechanic_analysis || 'Механик еще не завершил анализ.' }}</p>
          <p v-if="item.recommendation" class="mt-4 rounded-xl border border-border p-3 text-sm text-text dark:border-border-dark dark:text-text-dark">
            Что делать: {{ item.recommendation }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
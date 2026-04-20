<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

type DamageReport = {
  id: number
  title: string
  description?: string | null
  status: string
  created_at: string
  car?: {
    brand: string
    model: string
  } | null
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const endpoint = computed(() => `${config.public.apiBase}/damage-reports/my`)

const { data, pending, error } = useFetch<DamageReport[]>(
  () => endpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : '',
    })),
    watch: [endpoint, () => auth.token],
  }
)

const items = computed(() => data.value ?? [])

const statusLabel = (status: string) => {
  if (status === 'new') return 'Новая'
  if (status === 'in_review') return 'В обработке'
  if (status === 'analyzed') return 'Осмотрено'
  return status
}

const statusTone = (status: string) => {
  if (status === 'new') return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
  if (status === 'in_review') return 'border-blue-500/30 bg-blue-500/10 text-blue-300'
  if (status === 'analyzed') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  return 'border-slate-500/30 bg-slate-500/10 text-slate-300'
}

const newCount = computed(() => items.value.filter(item => item.status === 'new').length)
const inReviewCount = computed(() => items.value.filter(item => item.status === 'in_review').length)
const analyzedCount = computed(() => items.value.filter(item => item.status === 'analyzed').length)

const openItem = (id: number) => navigateTo(`/user/damages/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Повреждения</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Все ваши заявки на осмотр повреждений и результаты оценки.
        </p>
      </div>

      <button
        class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        @click="navigateTo('/user/damages/new')"
      >
        + Новая заявка
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-3">
      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Новые</p>
        <p class="mt-2 text-2xl font-bold text-amber-300">{{ newCount }}</p>
      </div>

      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">В обработке</p>
        <p class="mt-2 text-2xl font-bold text-blue-300">{{ inReviewCount }}</p>
      </div>

      <div class="rounded-2xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-sm text-text-muted dark:text-text-muted">Осмотрено</p>
        <p class="mt-2 text-2xl font-bold text-emerald-300">{{ analyzedCount }}</p>
      </div>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="error" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      Не удалось загрузить заявки.
    </div>

    <div v-else-if="!items.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Заявок пока нет.
    </div>

    <div v-else class="space-y-4">
      <button
        v-for="item in items"
        :key="item.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400"
        @click="openItem(item.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">DR-{{ item.id }} — {{ item.car?.brand }} {{ item.car?.model }}</h2>
              <span class="rounded-full border px-3 py-1 text-xs" :class="statusTone(item.status)">
                {{ statusLabel(item.status) }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Дата: {{ new Date(item.created_at).toLocaleDateString() }}</p>
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ item.title }}</p>
            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">{{ item.description || 'Без описания' }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
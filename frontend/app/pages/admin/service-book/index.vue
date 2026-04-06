<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()

const getEndpoint = computed(() => `${config.public.apiBase}/service-book/admin/all`)

const { data, pending, error } = useFetch(
  () => getEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [getEndpoint],
  }
)

const entries = computed(() => data.value ?? [])

const errText = computed(
  () => (error.value ? "Не удалось загрузить сервисные книжки" : null)
)

const formatDate = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleString("ru-RU", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    })
  } catch {
    return dateStr
  }
}

const onViewCar = (carId: number) => navigateTo(`/admin/service-book/${carId}`)
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-text dark:text-text-dark">Все сервисные книжки</h1>
      <p class="mt-1 text-sm text-text-muted dark:text-text-muted">
        История обслуживания всех машин
      </p>
    </div>

    <div
      v-if="pending"
      class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
    >
      Загрузка...
    </div>

    <div
      v-else-if="errText"
      class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200"
    >
      {{ errText }}
    </div>

    <div v-else-if="!entries.length" class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
      <p class="text-text-muted dark:text-text-muted">Нет записей в сервисных книжках</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="entry in entries"
        :key="entry.id"
        class="rounded-2xl border border-border bg-bg p-5 hover:border-slate-400 transition dark:border-border-dark dark:bg-bg-dark dark:hover:border-slate-600"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <div class="text-lg font-semibold text-text dark:text-text-dark">
              {{ entry.car.brand }} {{ entry.car.model }}
              <span class="text-sm text-text-muted dark:text-text-muted">({{ entry.car.year }})</span>
            </div>
            <div class="mt-2 text-sm font-semibold text-yellow-400 uppercase">
              {{ entry.type }}
            </div>
            <div class="mt-1 text-text-muted dark:text-text-muted">
              {{ entry.description }}
            </div>
            <div class="mt-3 flex gap-6 text-sm">
              <div class="flex items-center gap-2">
                <span class="text-text-muted">Пробег:</span>
                <span class="text-text dark:text-text-dark">{{ entry.mileage.toLocaleString() }} км</span>
              </div>
              <div v-if="entry.order_number" class="flex items-center gap-2">
                <span class="text-text-muted">Заказ:</span>
                <span class="text-text dark:text-text-dark">{{ entry.order_number }}</span>
              </div>
            </div>
          </div>
          <div class="text-right shrink-0">
            <div class="text-sm text-text-muted dark:text-text-muted mb-3">
              {{ formatDate(entry.created_at) }}
            </div>
            <button
              class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition"
              @click="onViewCar(entry.car_id)"
            >
              Книжка
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
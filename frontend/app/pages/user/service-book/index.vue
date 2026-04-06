<script setup lang="ts">
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({
  middleware: ["auth"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()

const carsEndpoint = computed(() => `${config.public.apiBase}/cars`)

const { data: cars, pending, error, refresh } = useFetch<Car[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carsEndpoint],
  }
)

const errText = computed(() => (error.value ? "Не удалось загрузить машины" : null))

const onViewServiceBook = (id: number) => navigateTo(`/user/service-book/${id}`)
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-text dark:text-text-dark">Сервисные книжки</h1>
      <p class="mt-1 text-sm text-text-muted dark:text-text-muted">Просмотр истории обслуживания ваших машин</p>
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

    <div v-else-if="!cars?.length" class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
      <p class="text-text-muted dark:text-text-muted">Нет машин в гараже</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="car in cars"
        :key="car.id"
        class="rounded-2xl border border-border bg-bg p-5 flex items-center justify-between hover:border-slate-400 transition dark:border-border-dark dark:bg-bg-dark dark:hover:border-slate-600"
      >
        <div>
          <div class="text-lg font-semibold text-text dark:text-text-dark">
            {{ car.brand }} {{ car.model }}
          </div>
          <div class="mt-1 text-sm text-text-muted dark:text-text-muted">
            {{ car.year }} год • Пробег: {{ car.mileage.toLocaleString() }} км
          </div>
        </div>
        <button
          class="rounded-xl bg-yellow-400 px-5 py-2 font-medium text-black hover:opacity-90 transition dark:text-text-dark"
          @click="onViewServiceBook(car.id)"
        >
          Открыть книжку
        </button>
      </div>
    </div>
  </div>
</template>
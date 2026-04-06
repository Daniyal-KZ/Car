<script setup lang="ts">
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({
  middleware: ["auth"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()

const carsEndpoint = computed(() => `${config.public.apiBase}/cars`)

const { data, pending, error } = await useFetch<Car[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carsEndpoint, auth.token],
  }
)

const cars = computed(() => data.value ?? [])

const openItem = (id: number) => navigateTo(`/user/maintenance/${id}`)

const errText = computed(() => (error.value ? "Не удалось загрузить машины" : null))
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Регламентное ТО</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Список автомобилей и рекомендуемое обслуживание по каждой машине.
      </p>
    </div>

    <div v-if="pending" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      Загрузка...
    </div>

    <div v-else-if="errText" class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200">
      {{ errText }}
    </div>

    <div v-else-if="!cars.length" class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark">
      <p class="text-text-muted dark:text-text-muted">У вас пока нет добавленных машин. Сначала добавьте автомобиль в гараж.</p>
    </div>

    <div v-else class="space-y-4">
      <button
        v-for="car in cars"
        :key="car.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400"
        @click="openItem(car.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ car.brand }} {{ car.model }}</h2>
              <span class="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                По машине
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
              {{ car.year }} год • Пробег: {{ car.mileage.toLocaleString() }} км
            </p>

            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">
              Откройте для рекомендаций ТО
            </p>
          </div>

          <div class="text-sm font-medium text-cyan-300">
            Открыть →
          </div>
        </div>
      </button>
    </div>
  </div>
</template>
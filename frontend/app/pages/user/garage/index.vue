<script setup lang="ts">
import CarTable from "~/components/garage/CarTable.vue"
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({
  middleware: ["auth", "role"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()

const carsEndpoint = computed(() => `${config.public.apiBase}/cars`)

const pageTitle = 'Мой гараж'

const { data, pending, error, refresh } = await useFetch<Car[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carsEndpoint],
  }
)

const cars = computed(() => data.value ?? [])

const onOpen = (id: number) => navigateTo(`/user/garage/${id}`)
const onCreate = () => navigateTo(`/user/garage/create`)

const onDelete = async (id: number) => {
  if (!confirm("Удалить машину?")) return

  await $fetch(`${config.public.apiBase}/cars/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    },
  })

  await refresh()
}

const errText = computed(() => (error.value ? "Не удалось загрузить машины" : null))
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-text dark:text-text-dark">{{ pageTitle }}</h1>
        <p class="mt-1 text-sm text-text-muted dark:text-text-muted">Всего машин: {{ cars.length }}</p>
      </div>

      <button
        class="rounded-2xl bg-yellow-400 px-5 py-3 font-medium text-black dark:text-text-dark dark:text-text transition hover:opacity-90"
        @click="onCreate"
      >
        + Добавить машину
      </button>
    </div>

    <CarTable
      :cars="cars"
      :showOwner="false"
      :loading="pending"
      :error="errText"
      @open="onOpen"
    />
  </div>
</template>

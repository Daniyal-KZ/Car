<script setup lang="ts">
import CarTable from "~/components/garage/CarTable.vue"
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({
  middleware: ["auth", "role"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()
const { t } = useI18n()

const carsEndpoint = computed(() => `${config.public.apiBase}/cars/admin/all`)

const { data, pending, error, refresh } = useFetch<Car[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carsEndpoint],
  }
)

const cars = computed(() => data.value ?? [])

const onOpen = (id: number) => navigateTo(`/admin/garage/${id}`)

const onDelete = async (id: number) => {
  if (!confirm(t('admin_garage_delete_confirm'))) return

  await $fetch(`${config.public.apiBase}/cars/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    },
  })

  await refresh()
}

const errText = computed(() => (error.value ? t('admin_garage_load_error') : null))
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-text dark:text-text-dark">{{ t('garage') }}</h1>
        <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ t('admin_garage_total') }}: {{ cars.length }}</p>
      </div>
    </div>

    <CarTable
      :cars="cars"
      :showOwner="true"
      :loading="pending"
      :error="errText"
      @open="onOpen"
    />
  </div>
</template>

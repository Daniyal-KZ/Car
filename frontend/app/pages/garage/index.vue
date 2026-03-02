<script setup lang="ts">
import CarTable from "~/components/garage/CarTable.vue"
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({
  middleware: ["auth"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()

const role = computed(() => auth.user?.role ?? "user")
const isAdmin = computed(() => role.value === "admin")

// ✅ один маршрут /garage, но разные данные
const carsEndpoint = computed(() => {
  return isAdmin.value
    ? `${config.public.apiBase}/cars/admin/all`
    : `${config.public.apiBase}/cars`
})

const pageTitle = computed(() => (isAdmin.value ? "Гараж сервиса" : "Мой гараж"))

const { data, pending, error, refresh } = await useFetch<Car[]>(
  () => carsEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [carsEndpoint], // ✅ если роль поменялась/перелогинился, перезагрузит
  }
)

const cars = computed(() => data.value ?? [])

const onOpen = (id: number) => navigateTo(`/garage/${id}`)
const onEdit = (id: number) => navigateTo(`/garage/${id}?edit=1`)
const onCreate = () => navigateTo(`/garage/create`)

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
 <CarTable
  :title="pageTitle"
  :cars="cars"
  :showOwner="isAdmin"
  :loading="pending"
  :error="errText"
  @open="onOpen"
/>
  </div>
</template>
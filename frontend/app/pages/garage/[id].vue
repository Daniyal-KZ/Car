<script setup lang="ts">
import CarForm from "~/components/garage/CarForm.vue"
import CarDetails from "~/components/garage/CarDetails.vue"
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({ middleware: ["auth"] })

type CarPayload = {
  brand: string
  model: string
  year: number
  mileage: number
  last_service?: number | null
}

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const id = computed(() => Number(route.params.id))
const isEdit = computed(() => route.query.edit === "1")

const role = computed(() => auth.user?.role ?? "user")
const isAdmin = computed(() => role.value === "admin")

const getEndpoint = computed(() => {
  return isAdmin.value
    ? `${config.public.apiBase}/cars/admin/${id.value}`
    : `${config.public.apiBase}/cars/${id.value}`
})

const { data, pending, error, refresh } = await useFetch<Car>(
  () => getEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [getEndpoint],
  }
)

const mode = computed(() => (isEdit.value ? "edit" : "view"))

const saving = ref(false)
const selectedFiles = ref<File[]>([])

const onFilesChange = (files: File[]) => {
  selectedFiles.value = files
}

const uploadCarImages = async (carId: number) => {
  if (!selectedFiles.value.length) return

  const formData = new FormData()

  for (const file of selectedFiles.value) {
    formData.append("files", file)
  }

  await $fetch(`${config.public.apiBase}/cars/${carId}/images`, {
    method: "POST",
    body: formData,
    headers: {
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    },
  })

  selectedFiles.value = []
}

const submit = async (payload: CarPayload) => {
  if (isAdmin.value) return

  saving.value = true
  try {
    await $fetch(`${config.public.apiBase}/cars/${id.value}`, {
      method: "PUT",
      body: payload,
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : "",
      },
    })

    await uploadCarImages(id.value)
    await refresh()
    await navigateTo(`/garage/${id.value}`)
  } finally {
    saving.value = false
  }
}

const cancel = () => navigateTo(`/garage/${id.value}`)

const goEdit = () => {
  if (isAdmin.value) return
  navigateTo(`/garage/${id.value}?edit=1`)
}

const errText = computed(() => (error.value ? "Не удалось загрузить машину" : null))
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <div class="mb-6">
      <NuxtLink to="/garage" class="text-sm text-gray-400 hover:text-cyan-400">
        ← Назад в гараж
      </NuxtLink>
    </div>

    <div
      v-if="pending"
      class="rounded-2xl border border-gray-800 bg-gray-950 p-6 text-gray-300"
    >
      Загрузка...
    </div>

    <div
      v-else-if="errText"
      class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200"
    >
      {{ errText }}
    </div>

    <CarDetails
      v-else-if="mode === 'view' && data"
      :car="data"
      :show-owner="isAdmin"
      :can-edit="!isAdmin"
      @edit="goEdit"
    />

    <CarForm
      v-else-if="data"
      :mode="mode"
      :initial="data as any"
      :loading="saving"
      @submit="submit"
      @files-change="onFilesChange"
      @cancel="cancel"
      @edit="goEdit"
    />
  </div>
</template>
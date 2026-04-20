<script setup lang="ts">
import CarForm from "~/components/garage/CarForm.vue"
import CarDetails from "~/components/garage/CarDetails.vue"
import type { Car } from "~/components/garage/CarRow.vue"

type CarPayload = {
  brand: string
  model: string
  vin: string | null
  year: number
  mileage: number
}

definePageMeta({ middleware: ["auth", "role"] })

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const id = computed(() => Number(route.params.id))
const isEdit = computed(() => route.query.edit === "1")

const getEndpoint = computed(() => `${config.public.apiBase}/cars/${id.value}`)

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
    await navigateTo(`/user/garage/${id.value}`)
  } finally {
    saving.value = false
  }
}

const cancel = () => navigateTo(`/user/garage/${id.value}`)

const goEdit = () => {
  navigateTo(`/user/garage/${id.value}?edit=1`)
}

const errText = computed(() => (error.value ? "Не удалось загрузить машину" : null))
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <div class="mb-6">
      <NuxtLink to="/user/garage" class="text-sm text-text-muted hover:text-cyan-400 dark:text-text-muted">
        ← Назад в гараж
      </NuxtLink>
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

    <CarDetails
      v-else-if="mode === 'view' && data"
      :car="data"
      :show-owner="false"
      :can-edit="true"
      :service-book-url="`/user/service-book/${data.id}`"
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

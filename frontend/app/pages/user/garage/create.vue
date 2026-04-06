<script setup lang="ts">
import CarForm from "~/components/garage/CarForm.vue"

definePageMeta({ middleware: ["auth", "role"] })

type CarPayload = {
  brand: string
  model: string
  year: number
  mileage: number
}

const config = useRuntimeConfig()
const auth = useAuthStore()

const loading = ref(false)
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
  loading.value = true
  try {
    const created = await $fetch<{ id: number }>(`${config.public.apiBase}/cars`, {
      method: "POST",
      body: payload,
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : "",
      },
    })

    await uploadCarImages(created.id)
    await navigateTo(`/user/garage/${created.id}`)
  } finally {
    loading.value = false
  }
}

const cancel = () => navigateTo("/user/garage")
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-10">
    <CarForm
      mode="create"
      :loading="loading"
      @submit="submit"
      @files-change="onFilesChange"
      @cancel="cancel"
    />
  </div>
</template>

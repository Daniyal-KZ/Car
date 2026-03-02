<script setup lang="ts">
import CarForm from "~/components/garage/CarForm.vue"

definePageMeta({ middleware: ["auth"] })

const config = useRuntimeConfig()
const auth = useAuthStore()

const loading = ref(false)

const submit = async (payload: any) => {
  loading.value = true
  try {
    const created = await $fetch(`${config.public.apiBase}/cars`, {
      method: "POST",
      body: payload,
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : "",
      },
    })
    // @ts-ignore
    await navigateTo(`/garage/${created.id}`)
  } finally {
    loading.value = false
  }
}

const cancel = () => navigateTo("/garage")
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-10">
    <CarForm mode="create" :loading="loading" @submit="submit" @cancel="cancel" />
  </div>
</template>
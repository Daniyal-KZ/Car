<script setup lang="ts">
import CarDetails from "~/components/garage/CarDetails.vue"
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({ middleware: ["auth", "role"] })

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()
const { t } = useI18n()

const id = computed(() => Number(route.params.id))

const getEndpoint = computed(() => `${config.public.apiBase}/cars/admin/${id.value}`)

const { data, pending, error, refresh } = await useFetch<Car>(
  () => getEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [getEndpoint],
  }
)

const errText = computed(() => (error.value ? t('admin_garage_item_load_error') : null))

const cancel = () => navigateTo("/admin/garage")
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <div class="mb-6">
      <NuxtLink to="/admin/garage" class="text-sm text-text-muted hover:text-cyan-400 dark:text-text-muted">
        {{ t('admin_garage_back') }}
      </NuxtLink>
    </div>

    <div
      v-if="pending"
      class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
    >
      {{ t('common_loading') }}
    </div>

    <div
      v-else-if="errText"
      class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200"
    >
      {{ errText }}
    </div>

    <CarDetails
      v-else-if="data"
      :car="data"
      :show-owner="true"
      :can-edit="false"
      :service-book-url="`/admin/service-book/${data.id}`"
    />
  </div>
</template>

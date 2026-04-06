<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const carId = computed(() => Number(route.params.id))

const getEndpoint = computed(() => `${config.public.apiBase}/service-book/${carId.value}`)

const { data, pending, error } = useFetch(
  () => getEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [getEndpoint],
  }
)

const entries = computed(() => data.value ?? [])

const errText = computed(() => (error.value ? "Не удалось загрузить сервисную книжку" : null))

const formatDate = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleString("ru-RU", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <div class="mb-6">
      <NuxtLink
        to="/user/service-book"
        class="text-sm text-text-muted hover:text-cyan-400 dark:text-text-muted"
      >
        ← Назад к сервисным книжкам
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

    <div v-else>
      <h1 class="text-2xl font-bold text-text dark:text-text-dark mb-6">
        Сервисная книжка машины
      </h1>

      <div v-if="!entries.length" class="rounded-2xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
        <p class="text-text-muted dark:text-text-muted">Нет записей в сервисной книжке</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="entry in entries"
          :key="entry.id"
          class="rounded-2xl border border-border bg-bg p-5 dark:border-border-dark dark:bg-bg-dark"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
              <div class="text-sm font-semibold text-yellow-400 uppercase">
                {{ entry.type }}
              </div>
              <div class="mt-2 text-text dark:text-text-dark">
                {{ entry.description }}
              </div>
              <div class="mt-3 flex gap-6 text-sm">
                <div class="flex items-center gap-2">
                  <span class="text-text-muted">Пробег:</span>
                  <span class="text-text dark:text-text-dark font-medium">
                    {{ entry.mileage.toLocaleString() }} км
                  </span>
                </div>
                <div v-if="entry.order_number" class="flex items-center gap-2">
                  <span class="text-text-muted">Заказ:</span>
                  <span class="text-text dark:text-text-dark font-medium">
                    {{ entry.order_number }}
                  </span>
                </div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm text-text-muted dark:text-text-muted">
                {{ formatDate(entry.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
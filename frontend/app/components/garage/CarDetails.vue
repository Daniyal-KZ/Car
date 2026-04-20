<script setup lang="ts">
import type { Car } from "~/components/garage/CarRow.vue"

const props = defineProps<{
  car: Car
  showOwner?: boolean
  canEdit?: boolean
  serviceBookUrl?: string
}>()

const { t } = useI18n()

const emit = defineEmits<{
  (e: "edit"): void
}>()

const config = useRuntimeConfig()
const apiBase = computed(() => config.public.apiBase || "http://127.0.0.1:8000")

const activeIndex = ref(0)

const images = computed(() => props.car.images ?? [])

watch(
  () => props.car.id,
  () => {
    activeIndex.value = 0
  },
  { immediate: true }
)

const activeImage = computed(() => {
  const current = images.value[activeIndex.value]
  if (!current?.file_path) return null
  return `${apiBase.value}${current.file_path}`
})

const ownerLabel = computed(() => {
  if (!props.showOwner) return ""
  const o = props.car.owner
  if (o?.username) return o.username
  if (o?.email) return o.email
  if (props.car.owner_id != null) return `ID: ${props.car.owner_id}`
  return "—"
})
</script>

<template>
  <section class="space-y-6">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-[1.45fr_1fr]">
      <div class="rounded-3xl border border-border bg-bg p-4 dark:border-border-dark dark:bg-bg-dark">
        <div class="overflow-hidden rounded-2xl border border-border bg-white dark:border-border-dark dark:bg-bg-dark">
          <img
            v-if="activeImage"
            :src="activeImage"
            alt="car"
            class="h-[280px] w-full object-cover sm:h-[360px] lg:h-[460px]"
          />

          <div
            v-else
            class="flex h-[280px] w-full items-center justify-center bg-slate-100 text-lg text-text-muted sm:h-[360px] lg:h-[460px] dark:bg-bg-dark dark:text-text-muted"
          >
            {{ t('garage_no_photo') }}
          </div>
        </div>

        <div v-if="images.length" class="mt-4 flex gap-3 overflow-x-auto pb-1">
          <button
            v-for="(image, index) in images"
            :key="image.id"
            type="button"
            class="shrink-0 overflow-hidden rounded-xl border transition"
            :class="index === activeIndex ? 'border-yellow-400' : 'border-border hover:border-slate-400 dark:border-border-dark dark:hover:border-slate-600'"
            @click="activeIndex = index"
          >
            <img
              :src="`${apiBase}${image.file_path}`"
              :alt="image.file_name"
              class="h-20 w-28 object-cover"
            />
          </button>
        </div>
      </div>

      <div class="rounded-3xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
        <div class="mb-5">
          <h1 class="text-3xl font-bold text-text dark:text-text-dark">
            {{ car.brand }} {{ car.model }}
          </h1>

          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
            {{ car.year }} {{ t('garage_year_suffix') }}
          </p>
        </div>

        <div class="space-y-4">
          <div class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark">
            <div class="text-sm text-text-muted">VIN</div>
            <div class="mt-1 text-base font-semibold text-text">
              {{ car.vin || t('garage_not_specified') }}
            </div>
          </div>

          <div class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark">
            <div class="text-sm text-text-muted">{{ t('garage_mileage') }}</div>
            <div class="mt-1 text-xl font-semibold text-text">
              {{ car.mileage.toLocaleString() }} {{ t('garage_km_short') }}
            </div>
          </div>

          <div
            v-if="showOwner"
            class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark"
          >
            <div class="text-sm text-text-muted">{{ t('garage_owner') }}</div>
            <div class="mt-1 text-base font-medium text-text">
              {{ ownerLabel }}
            </div>
          </div>
        </div>

        <div class="mt-6 space-y-3">
          <button
            v-if="canEdit"
            class="w-full rounded-2xl bg-yellow-400 px-4 py-3 font-medium text-black transition hover:opacity-90 dark:text-text-dark"
            @click="emit('edit')"
          >
            {{ t('garage_edit') }}
          </button>

          <button
            v-if="serviceBookUrl"
            class="w-full rounded-2xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:opacity-90"
            @click="$router.push(serviceBookUrl)"
          >
            {{ t('garage_service_book') }}
          </button>
        </div>
      </div>
    </div>



    <div class="rounded-3xl border border-border bg-bg p-6 dark:border-border-dark dark:bg-bg-dark">
      <h2 class="mb-4 text-xl font-semibold text-text dark:text-text-dark">
        {{ t('garage_specs') }}
      </h2>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark">
          <div class="text-sm text-text-muted">{{ t('garage_brand') }}</div>
          <div class="mt-1 font-medium text-text">
            {{ car.brand }}
          </div>
        </div>

        <div class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark">
          <div class="text-sm text-text-muted">{{ t('garage_model') }}</div>
          <div class="mt-1 font-medium text-text">
            {{ car.model }}
          </div>
        </div>

        <div class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark">
          <div class="text-sm text-text-muted">{{ t('garage_year') }}</div>
          <div class="mt-1 font-medium text-text">
            {{ car.year }}
          </div>
        </div>

        <div class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark">
          <div class="text-sm text-text-muted">VIN</div>
          <div class="mt-1 font-medium text-text">
            {{ car.vin || t('garage_not_specified') }}
          </div>
        </div>

        <div class="rounded-2xl bg-white px-4 py-4 text-text dark:bg-bg-dark dark:text-text-dark">
          <div class="text-sm text-text-muted">{{ t('garage_mileage') }}</div>
          <div class="mt-1 font-medium text-text">
            {{ car.mileage.toLocaleString() }} {{ t('garage_km_short') }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
<script setup lang="ts">
import type { Car } from "~/components/garage/CarRow.vue"

const props = defineProps<{
  car: Car
  showOwner?: boolean
  canEdit?: boolean
}>()

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
      <div class="rounded-3xl border border-gray-800 bg-gray-950 p-4">
        <div class="overflow-hidden rounded-2xl border border-gray-800 bg-gray-900">
          <img
            v-if="activeImage"
            :src="activeImage"
            alt="car"
            class="h-[280px] w-full object-cover sm:h-[360px] lg:h-[460px]"
          />

          <div
            v-else
            class="flex h-[280px] w-full items-center justify-center bg-gray-900 text-lg text-gray-500 sm:h-[360px] lg:h-[460px]"
          >
            Нет фото
          </div>
        </div>

        <div v-if="images.length" class="mt-4 flex gap-3 overflow-x-auto pb-1">
          <button
            v-for="(image, index) in images"
            :key="image.id"
            type="button"
            class="shrink-0 overflow-hidden rounded-xl border transition"
            :class="index === activeIndex ? 'border-yellow-400' : 'border-gray-800 hover:border-gray-600'"
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

      <div class="rounded-3xl border border-gray-800 bg-gray-950 p-6">
        <div class="mb-5">
          <h1 class="text-3xl font-bold text-gray-100">
            {{ car.brand }} {{ car.model }}
          </h1>

          <p class="mt-2 text-sm text-gray-400">
            {{ car.year }} год
          </p>
        </div>

        <div class="space-y-4">
          <div class="rounded-2xl bg-gray-900 px-4 py-4">
            <div class="text-sm text-gray-400">Пробег</div>
            <div class="mt-1 text-xl font-semibold text-gray-100">
              {{ car.mileage.toLocaleString() }} км
            </div>
          </div>

          <div class="rounded-2xl bg-gray-900 px-4 py-4">
            <div class="text-sm text-gray-400">Пробег при последнем ТО</div>
            <div class="mt-1 text-xl font-semibold text-gray-100">
              {{ car.last_service ?? "—" }}
            </div>
          </div>

          <div
            v-if="showOwner"
            class="rounded-2xl bg-gray-900 px-4 py-4"
          >
            <div class="text-sm text-gray-400">Владелец</div>
            <div class="mt-1 text-base font-medium text-gray-100">
              {{ ownerLabel }}
            </div>
          </div>
        </div>

        <div v-if="canEdit" class="mt-6">
          <button
            class="w-full rounded-2xl bg-yellow-400 px-4 py-3 font-medium text-black transition hover:opacity-90"
            @click="emit('edit')"
          >
            Редактировать
          </button>
        </div>
      </div>
    </div>

    <div class="rounded-3xl border border-gray-800 bg-gray-950 p-6">
      <h2 class="mb-4 text-xl font-semibold text-gray-100">
        Характеристики
      </h2>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div class="rounded-2xl bg-gray-900 px-4 py-4">
          <div class="text-sm text-gray-400">Марка</div>
          <div class="mt-1 font-medium text-gray-100">
            {{ car.brand }}
          </div>
        </div>

        <div class="rounded-2xl bg-gray-900 px-4 py-4">
          <div class="text-sm text-gray-400">Модель</div>
          <div class="mt-1 font-medium text-gray-100">
            {{ car.model }}
          </div>
        </div>

        <div class="rounded-2xl bg-gray-900 px-4 py-4">
          <div class="text-sm text-gray-400">Год</div>
          <div class="mt-1 font-medium text-gray-100">
            {{ car.year }}
          </div>
        </div>

        <div class="rounded-2xl bg-gray-900 px-4 py-4">
          <div class="text-sm text-gray-400">Пробег</div>
          <div class="mt-1 font-medium text-gray-100">
            {{ car.mileage.toLocaleString() }} км
          </div>
        </div>

        <div class="rounded-2xl bg-gray-900 px-4 py-4 md:col-span-2">
          <div class="text-sm text-gray-400">Пробег при последнем ТО</div>
          <div class="mt-1 font-medium text-gray-100">
            {{ car.last_service ?? "—" }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
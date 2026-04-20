<script setup lang="ts">
type Owner = {
  id: number
  username?: string | null
  email?: string | null
}

export type CarImage = {
  id: number
  car_id: number
  file_path: string
  file_name: string
}

export type Car = {
  id: number
  brand: string
  model: string
  vin?: string | null
  year: number
  mileage: number
  last_service?: number | null
  owner?: Owner | null
  owner_id?: number | null
  images?: CarImage[]
}

const props = defineProps<{
  car: Car
  showOwner?: boolean
}>()

const { t } = useI18n()

const emit = defineEmits<{
  (e: "open", id: number): void
}>()

const config = useRuntimeConfig()

const apiBase = computed(() => config.public.apiBase || "http://127.0.0.1:8000")

const ownerLabel = computed(() => {
  if (!props.showOwner) return ""
  const o = props.car.owner
  if (o?.username) return o.username
  if (o?.email) return o.email
  if (props.car.owner_id != null) return `ID: ${props.car.owner_id}`
  return "—"
})

const previewImage = computed(() => {
  const first = props.car.images?.[0]
  if (!first?.file_path) return null
  return `${apiBase.value}${first.file_path}`
})

const open = () => emit("open", props.car.id)

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault()
    open()
  }
}
</script>

<template>
  <tr
    class="border-b border-border hover:bg-slate-100 dark:border-border-dark dark:hover:bg-slate-800 transition cursor-pointer"
    role="button"
    tabindex="0"
    @click="open"
    @keydown="onKeydown"
  >
    <td class="py-3 px-4">
      <div class="h-14 w-20 overflow-hidden rounded-lg border border-border bg-white dark:border-border-dark dark:bg-bg-dark">
        <img
          v-if="previewImage"
          :src="previewImage"
          alt="car"
          class="h-full w-full object-cover"
        />
        <div
          v-else
          class="flex h-full w-full items-center justify-center text-[11px] text-text-muted dark:text-text-muted"
        >
          {{ t('garage_no_photo') }}
        </div>
      </div>
    </td>

    <td class="py-3 px-4 whitespace-nowrap text-text font-medium">
      {{ car.brand }}
    </td>

    <td class="py-3 px-4 text-text-muted">
      {{ car.model }}
    </td>

    <td class="py-3 px-4 text-text-muted whitespace-nowrap">
      {{ car.year }}
    </td>

    <td class="py-3 px-4 text-text-muted whitespace-nowrap">
      {{ car.vin || "—" }}
    </td>

    <td class="py-3 px-4 text-text-muted whitespace-nowrap">
      {{ car.mileage.toLocaleString() }} {{ t('garage_km_short') }}
    </td>

    <td class="py-3 px-4 text-text-muted dark:text-text-muted whitespace-nowrap">
      {{ car.last_service ?? "—" }}
    </td>

    <td v-if="showOwner" class="py-3 px-4 text-text-muted">
      {{ ownerLabel }}
    </td>
  </tr>
</template>
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
    class="border-b border-gray-800 hover:bg-gray-900/50 transition cursor-pointer"
    role="button"
    tabindex="0"
    @click="open"
    @keydown="onKeydown"
  >
    <td class="py-3 px-4">
      <div class="h-14 w-20 overflow-hidden rounded-lg border border-gray-800 bg-gray-900">
        <img
          v-if="previewImage"
          :src="previewImage"
          alt="car"
          class="h-full w-full object-cover"
        />
        <div
          v-else
          class="flex h-full w-full items-center justify-center text-[11px] text-gray-500"
        >
          Нет фото
        </div>
      </div>
    </td>

    <td class="py-3 px-4 whitespace-nowrap text-gray-100 font-medium">
      {{ car.brand }}
    </td>

    <td class="py-3 px-4 text-gray-200">
      {{ car.model }}
    </td>

    <td class="py-3 px-4 text-gray-300 whitespace-nowrap">
      {{ car.year }}
    </td>

    <td class="py-3 px-4 text-gray-300 whitespace-nowrap">
      {{ car.mileage.toLocaleString() }} км
    </td>

    <td class="py-3 px-4 text-gray-400 whitespace-nowrap">
      {{ car.last_service ?? "—" }}
    </td>

    <td v-if="showOwner" class="py-3 px-4 text-gray-300">
      {{ ownerLabel }}
    </td>
  </tr>
</template>
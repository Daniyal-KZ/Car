<script setup lang="ts">
import CarRow, { type Car } from "~/components/garage/CarRow.vue"

const props = defineProps<{
  title?: string
  cars: Car[]
  showOwner?: boolean
  loading?: boolean
  error?: string | null
}>()

const emit = defineEmits<{
  (e: "open", id: number): void
}>()

const q = ref("")

const filtered = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return props.cars

  return props.cars.filter((c) => {
    const base =
      `${c.brand} ${c.model} ${c.year} ${c.mileage} ${c.last_service ?? ""}`.toLowerCase()

    const owner = props.showOwner
      ? `${c.owner?.username ?? ""} ${c.owner?.email ?? ""} ${c.owner_id ?? ""}`.toLowerCase()
      : ""

    return (base + " " + owner).includes(query)
  })
})

const colSpan = computed(() => (props.showOwner ? 6 : 5))
</script>

<template>
  <section class="w-full">
    <div class="flex items-center justify-between gap-3 mb-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">
          {{ title ?? "Гараж" }}
        </h1>
        <p class="text-gray-400 text-sm mt-1">
          Машины: {{ filtered.length }}
        </p>
      </div>
    </div>

    <div class="flex items-center gap-3 mb-4">
      <input
        v-model="q"
        type="text"
        placeholder="Поиск по марке / модели / году / пробегу..."
        class="w-full max-w-xl px-4 py-2 rounded-xl bg-gray-900 border border-gray-800 text-gray-100 outline-none focus:border-gray-600"
      />
    </div>

    <div v-if="loading" class="p-6 rounded-2xl bg-gray-950 border border-gray-800 text-gray-300">
      Загрузка...
    </div>

    <div v-else-if="error" class="p-6 rounded-2xl bg-red-950/40 border border-red-900 text-red-200">
      {{ error }}
    </div>

    <div v-else class="rounded-2xl overflow-hidden border border-gray-800 bg-gray-950">
      <table class="w-full text-left">
        <thead class="bg-gray-900">
          <tr class="text-gray-300 text-sm">
            <th class="py-3 px-4 font-semibold">Марка</th>
            <th class="py-3 px-4 font-semibold">Модель</th>
            <th class="py-3 px-4 font-semibold">Год</th>
            <th class="py-3 px-4 font-semibold">Пробег</th>
            <th class="py-3 px-4 font-semibold">ТО</th>
            <th v-if="showOwner" class="py-3 px-4 font-semibold">Владелец</th>
          </tr>
        </thead>

        <tbody>
          <CarRow
            v-for="car in filtered"
            :key="car.id"
            :car="car"
            :showOwner="showOwner"
            @open="emit('open', $event)"
          />

          <tr v-if="filtered.length === 0">
            <td class="py-8 px-4 text-gray-400" :colspan="colSpan">
              Ничего не найдено.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
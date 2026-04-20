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
      `${c.brand} ${c.model} ${c.vin ?? ''} ${c.year} ${c.mileage}`.toLowerCase()

    const owner = props.showOwner
      ? `${c.owner?.username ?? ""} ${c.owner?.email ?? ""} ${c.owner_id ?? ""}`.toLowerCase()
      : ""

    return (base + " " + owner).includes(query)
  })
})

const colSpan = computed(() => (props.showOwner ? 9 : 8))
</script>

<template>
  <section class="w-full">
    <div class="mb-4 flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-text dark:text-text-dark">
          {{ title ?? "Гараж" }}
        </h1>
        <p class="mt-1 text-sm text-text-muted dark:text-text-muted">
          Машины: {{ filtered.length }}
        </p>
      </div>
    </div>

    <div class="mb-4 flex items-center gap-3">
      <input
        v-model="q"
        type="text"
        placeholder="Поиск по марке / модели / VIN / году / пробегу..."
        class="w-full max-w-xl rounded-xl border border-border bg-white px-4 py-2 text-text outline-none focus:border-primary dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
      />
    </div>

    <div
      v-if="loading"
      class="rounded-2xl border border-border bg-bg p-6 text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
    >
      Загрузка...
    </div>

    <div
      v-else-if="error"
      class="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-red-200"
    >
      {{ error }}
    </div>

    <div
      v-else
      class="overflow-hidden rounded-2xl border border-border bg-bg dark:border-border-dark dark:bg-bg-dark"
    >
      <table class="w-full text-left">
        <thead class="bg-slate-100 dark:bg-bg-dark">
          <tr class="text-sm text-text-muted dark:text-text-muted">
            <th class="py-3 px-4 font-semibold">Фото</th>
            <th class="py-3 px-4 font-semibold">Марка</th>
            <th class="py-3 px-4 font-semibold">Модель</th>
            <th class="py-3 px-4 font-semibold">Год</th>
            <th class="py-3 px-4 font-semibold">VIN</th>
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
            <td class="py-8 px-4 text-text-muted dark:text-text-muted" :colspan="colSpan">
              Ничего не найдено.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
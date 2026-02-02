<script setup lang="ts">
const config = useRuntimeConfig()
const { data: cars } = await useFetch(`${config.public.apiBase}/cars`)
const selectedCar = ref(null)
</script>

<template>
  <div class="h-screen flex flex-col items-center justify-center bg-gray-900 gap-4 p-8">
    <h1 class="text-6xl font-bold text-white">Список машин</h1>

    <div v-if="cars && cars.length > 0" class="flex flex-col gap-2 mt-4">
      <button
          v-for="car in cars"
          :key="car.id"
          @click="selectedCar = car"
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white"
      >
        {{ car.brand }} {{ car.model }} ({{ car.year }})
      </button>
    </div>

    <div v-if="selectedCar" class="mt-4 text-white text-2xl">
      Выбрана машина: {{ selectedCar.brand }} {{ selectedCar.model }} ({{ selectedCar.year }})
      — Пробег: {{ selectedCar.mileage }} км
      — Последнее ТО: {{ selectedCar.last_service }} км
    </div>
  </div>
</template>

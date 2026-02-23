<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">Мой гараж</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="car in cars"
        :key="car.id"
        class="bg-white p-6 rounded-lg shadow-md"
      >
        <h2 class="text-xl font-semibold mb-2">{{ car.brand }} {{ car.model }}</h2>
        <p class="text-gray-600 mb-1">Год: {{ car.year }}</p>
        <p class="text-gray-600 mb-4">Пробег: {{ car.mileage }} км</p>
        <button
          @click="sendToService(car.id)"
          class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Отправить в СТО
        </button>
      </div>
    </div>
    <div v-if="cars.length === 0" class="text-center text-gray-500 mt-10">
      У вас нет машин. Добавьте машину через API.
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['auth', 'role']
})

const authStore = useAuthStore()
const cars = ref([])
const loading = ref(true)

const fetchCars = async () => {
  try {
    const response = await $fetch('/api/cars', {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    cars.value = response
  } catch (err) {
    console.error('Error fetching cars:', err)
  } finally {
    loading.value = false
  }
}

const sendToService = async (carId: number) => {
  const type = prompt('Тип заявки (например, repair, maintenance):')
  if (!type) return

  const comment = prompt('Комментарий (опционально):') || null

  try {
    await $fetch('/api/service-requests', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        car_id: carId,
        type,
        comment
      })
    })
    alert('Заявка отправлена!')
  } catch (err) {
    console.error('Error sending request:', err)
    alert('Ошибка при отправке заявки')
  }
}

onMounted(() => {
  fetchCars()
})
</script>
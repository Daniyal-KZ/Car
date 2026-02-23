<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">Гараж СТО</h1>
    <div class="space-y-4">
      <div
        v-for="request in requests"
        :key="request.id"
        class="bg-white p-6 rounded-lg shadow-md"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h2 class="text-xl font-semibold">Машина ID: {{ request.car_id }}</h2>
            <p class="text-gray-600">Тип: {{ request.type }}</p>
            <p v-if="request.comment" class="text-gray-600">Комментарий: {{ request.comment }}</p>
            <p class="text-sm text-gray-500">Создано: {{ new Date(request.created_at).toLocaleString() }}</p>
          </div>
          <span
            :class="statusClasses[request.status]"
            class="px-3 py-1 rounded-full text-sm font-medium"
          >
            {{ statusLabels[request.status] }}
          </span>
        </div>
        <div class="flex space-x-2">
          <button
            v-if="request.status === 'submitted'"
            @click="updateStatus(request.id, 'accepted')"
            class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          >
            Принять
          </button>
          <button
            v-if="request.status === 'accepted'"
            @click="updateStatus(request.id, 'in_progress')"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Начать работу
          </button>
          <button
            v-if="request.status === 'in_progress'"
            @click="updateStatus(request.id, 'done')"
            class="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
          >
            Завершить
          </button>
          <button
            v-if="request.status !== 'done' && request.status !== 'cancelled'"
            @click="updateStatus(request.id, 'cancelled')"
            class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Отменить
          </button>
        </div>
      </div>
    </div>
    <div v-if="requests.length === 0" class="text-center text-gray-500 mt-10">
      Нет активных заявок.
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['auth', 'role']
})

const authStore = useAuthStore()
const requests = ref([])
const loading = ref(true)

const statusClasses = {
  submitted: 'bg-yellow-100 text-yellow-800',
  accepted: 'bg-green-100 text-green-800',
  in_progress: 'bg-blue-100 text-blue-800',
  done: 'bg-gray-100 text-gray-800',
  cancelled: 'bg-red-100 text-red-800'
}

const statusLabels = {
  submitted: 'Отправлена',
  accepted: 'Принята',
  in_progress: 'В работе',
  done: 'Завершена',
  cancelled: 'Отменена'
}

const fetchRequests = async () => {
  try {
    const response = await $fetch('/api/service-requests/active', {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    requests.value = response
  } catch (err) {
    console.error('Error fetching requests:', err)
  } finally {
    loading.value = false
  }
}

const updateStatus = async (requestId: number, status: string) => {
  try {
    await $fetch(`/api/service-requests/${requestId}/status`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status })
    })
    await fetchRequests() // Обновить список
  } catch (err) {
    console.error('Error updating status:', err)
    alert('Ошибка при обновлении статуса')
  }
}

onMounted(() => {
  fetchRequests()
})
</script>
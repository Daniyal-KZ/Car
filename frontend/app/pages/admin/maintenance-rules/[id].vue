<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
})

const config = useRuntimeConfig()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const ruleId = computed(() => String(route.params.id || ""))

// ===== FETCH =====
const { data, pending, refresh } = useFetch(
  () => `${config.public.apiBase}/maintenance-rules/${ruleId.value}`,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [ruleId, auth.token],
  }
)

const rule = computed(() => data.value ?? null)

// ===== FORM =====
const formData = reactive({
  brand: '',
  model: '',
  status: 'draft',
  year_from: null as number | null,
  year_to: null as number | null,
  mileage_from: null as number | null,
  mileage_to: null as number | null,
})

// SYNC
watch(rule, (val) => {
  if (!val) return

  formData.brand = val.brand
  formData.model = val.model
  formData.status = val.status
  formData.year_from = val.year_from
  formData.year_to = val.year_to
  formData.mileage_from = val.mileage_from
  formData.mileage_to = val.mileage_to
}, { immediate: true })

// ===== UPDATE =====
const loading = ref(false)

const updateRule = async () => {
  loading.value = true
  try {
    await $fetch(`${config.public.apiBase}/maintenance-rules/${ruleId.value}`, {
      method: 'PUT',
      body: formData,
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : "",
      },
    })

    await refresh()
  } catch (e) {
    console.error(e)
    alert('Ошибка обновления')
  } finally {
    loading.value = false
  }
}

// ===== DELETE =====
const deleteRule = async () => {
  if (!confirm('Удалить регламент?')) return

  try {
    await $fetch(`${config.public.apiBase}/maintenance-rules/${ruleId.value}`, {
      method: 'DELETE',
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : "",
      },
    })

    router.push('/admin/maintenance-rules')
  } catch (e) {
    console.error(e)
    alert('Ошибка удаления')
  }
}

// ===== TASKS =====
const showAddTaskModal = ref(false)

const newTask = reactive({
  mileage_interval: 0,
  title: '',
  description: '',
  duration_minutes: undefined as number | undefined
})

const addTask = async () => {
  if (!newTask.title.trim()) return

  await $fetch(`${config.public.apiBase}/maintenance-rules/${ruleId.value}/tasks`, {
    method: 'POST',
    body: newTask,
    headers: {
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    },
  })

  Object.assign(newTask, {
    mileage_interval: 0,
    title: '',
    description: '',
    duration_minutes: undefined
  })

  showAddTaskModal.value = false
  await refresh()
}

const removeTask = async (taskId: number) => {
  if (!confirm('Удалить работу?')) return

  await $fetch(`${config.public.apiBase}/maintenance-rules/${ruleId.value}/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    },
  })

  await refresh()
}
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">

    <!-- HEADER -->
    <div class="mb-8 flex items-start justify-between">
      <div>
        <h1 class="text-3xl font-bold">Регламент #{{ rule?.id }}</h1>
      </div>

      <div class="flex gap-2">
  <button
    @click="router.push('/admin/maintenance-rules')"
    class="rounded-xl border border-border px-4 py-2 text-sm hover:border-cyan-400 hover:text-cyan-300">Назад</button>

  <button
    @click="updateRule"
    :disabled="loading"
    class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-black hover:bg-cyan-300"
  >
    {{ loading ? 'Сохранение...' : 'Сохранить' }}
  </button>

  <button
    @click="deleteRule"
    class="rounded-xl border border-red-500/30 px-4 py-2 text-sm text-red-400 hover:bg-red-500/10"
  >
    Удалить
  </button>
</div>
    </div>

    <!-- STATUS -->
    <div class="mb-6 flex gap-2">
      <button
        @click="formData.status = 'active'"
        :class="[
          'px-4 py-2 rounded-xl border',
          formData.status === 'active'
            ? 'bg-green-400 text-black'
            : 'border-border text-text-muted'
        ]"
      >
        Active
      </button>

      <button
        @click="formData.status = 'archived'"
        :class="[
          'px-4 py-2 rounded-xl border',
          formData.status === 'archived'
            ? 'bg-yellow-400 text-black'
            : 'border-border text-text-muted'
        ]"
      >
        Archived
      </button>

      <button
        @click="formData.status = 'draft'"
        :class="[
          'px-4 py-2 rounded-xl border',
          formData.status === 'draft'
            ? 'bg-gray-400 text-black'
            : 'border-border text-text-muted'
        ]"
      >
        Draft
      </button>
    </div>

    <!-- FORM -->
    <div class="grid gap-4 md:grid-cols-4 mb-6">
      <input v-model="formData.brand" placeholder="Марка" class="border rounded-xl px-3 py-2" />
      <input v-model="formData.model" placeholder="Модель" class="border rounded-xl px-3 py-2" />
      <input v-model.number="formData.mileage_from" type="number" placeholder="Пробег от" class="border rounded-xl px-3 py-2" />
      <input v-model.number="formData.mileage_to" type="number" placeholder="Пробег до" class="border rounded-xl px-3 py-2" />
    </div>

    <!-- TASKS -->
    <div class="rounded-2xl border p-6">
      <h2 class="mb-4 text-lg font-semibold">Работы</h2>

      <div class="space-y-3">
        <div
          v-for="task in rule?.tasks ?? []"
          :key="task.id"
          class="border rounded-xl p-3 flex justify-between"
        >
          <div>
            {{ task.mileage_interval }} км — {{ task.title }}
          </div>

          <button @click="removeTask(task.id)" class="text-red-400">
            Удалить
          </button>
        </div>
      </div>

      <button
        @click="showAddTaskModal = true"
        class="mt-4 w-full border rounded-xl py-2 hover:border-cyan-400"
      >
        + Добавить работу
      </button>
    </div>
  </div>

  <!-- MODAL -->
  <div v-if="showAddTaskModal" class="fixed inset-0 flex items-center justify-center bg-black/50">
    <div class="bg-white p-6 rounded-2xl w-full max-w-md">
      <input v-model.number="newTask.mileage_interval" type="number" placeholder="Пробег" class="w-full border p-2 mb-2" />
      <input v-model="newTask.title" placeholder="Название" class="w-full border p-2 mb-2" />
      <textarea v-model="newTask.description" placeholder="Описание" class="w-full border p-2 mb-2" />

      <button @click="addTask" class="w-full bg-cyan-400 py-2 rounded-xl">
        Добавить
      </button>
    </div>
  </div>
</template>
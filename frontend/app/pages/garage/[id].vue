<script setup lang="ts">
import CarForm from "~/components/garage/CarForm.vue"
import type { Car } from "~/components/garage/CarRow.vue"

definePageMeta({ middleware: ["auth"] })

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()

const id = computed(() => Number(route.params.id))
const isEdit = computed(() => route.query.edit === "1")

// ✅ admin vs user endpoint
const role = computed(() => auth.user?.role ?? "user")
const isAdmin = computed(() => role.value === "admin")

const getEndpoint = computed(() => {
  return isAdmin.value
    ? `${config.public.apiBase}/cars/admin/${id.value}`
    : `${config.public.apiBase}/cars/${id.value}`
})

const { data, pending, error, refresh } = await useFetch<Car>(
  () => getEndpoint.value,
  {
    headers: computed(() => ({
      Authorization: auth.token ? `Bearer ${auth.token}` : "",
    })),
    watch: [getEndpoint],
  }
)

const mode = computed(() => (isEdit.value ? "edit" : "view"))

const saving = ref(false)

const submit = async (payload: any) => {
  // если ты запретил админу редактировать — просто не даём сохранить
  if (isAdmin.value) return

  saving.value = true
  try {
    await $fetch(`${config.public.apiBase}/cars/${id.value}`, {
      method: "PUT",
      body: payload,
      headers: {
        Authorization: auth.token ? `Bearer ${auth.token}` : "",
      },
    })
    await refresh()
    await navigateTo(`/garage/${id.value}`) // убрать ?edit=1
  } finally {
    saving.value = false
  }
}

const cancel = () => navigateTo(`/garage/${id.value}`)

const goEdit = () => {
  // админ не редактирует
  if (isAdmin.value) return
  navigateTo(`/garage/${id.value}?edit=1`)
}

const errText = computed(() => (error.value ? "Не удалось загрузить машину" : null))
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-10">
    <div class="mb-6">
      <NuxtLink to="/garage" class="text-sm text-gray-400 hover:text-cyan-400">
        ← Назад в гараж
      </NuxtLink>
    </div>

    <div v-if="pending" class="p-6 rounded-2xl bg-gray-950 border border-gray-800 text-gray-300">
      Загрузка...
    </div>

    <div v-else-if="errText" class="p-6 rounded-2xl bg-red-950/40 border border-red-900 text-red-200">
      {{ errText }}
    </div>

    <CarForm
      v-else
      :mode="mode"
      :initial="data as any"
      :loading="saving"
      @submit="submit"
      @cancel="cancel"
      @edit="goEdit"
    />
  </div>
</template>
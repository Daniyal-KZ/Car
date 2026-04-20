<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const router = useRouter()
const auth = useAuthStore()
const config = useRuntimeConfig()

const role = computed(() => auth.user?.role ?? 'user')

const carsEndpoint = computed(() => {
  if (role.value === 'admin' || role.value === 'dev') return `${config.public.apiBase}/cars/admin/all`
  return `${config.public.apiBase}/cars`
})

const ordersEndpoint = computed(() => {
  if (role.value === 'mechanic') return `${config.public.apiBase}/service-orders/mechanic/queue`
  return `${config.public.apiBase}/service-orders/my`
})

const invoicesEndpoint = computed(() => {
  if (role.value === 'admin' || role.value === 'dev') return `${config.public.apiBase}/invoices/admin/all`
  return `${config.public.apiBase}/invoices/my`
})

const commonHeaders = computed(() => ({
  Authorization: auth.token ? `Bearer ${auth.token}` : "",
}))

const { data: carsData } = useFetch<any[]>(
  () => carsEndpoint.value,
  {
    headers: commonHeaders,
    watch: [carsEndpoint, () => auth.token],
    default: () => [],
  }
)

const { data: ordersData } = useFetch<any[]>(
  () => ordersEndpoint.value,
  {
    headers: commonHeaders,
    watch: [ordersEndpoint, () => auth.token],
    default: () => [],
  }
)

const { data: invoicesData } = useFetch<any[]>(
  () => invoicesEndpoint.value,
  {
    headers: commonHeaders,
    watch: [invoicesEndpoint, () => auth.token],
    default: () => [],
  }
)

const carsCount = computed(() => carsData.value?.length ?? 0)
const activeOrders = computed(() => {
  const list = ordersData.value ?? []
  if (role.value === 'mechanic') return list.length
  return list.filter((item: any) => ['new', 'accepted', 'in_progress'].includes(String(item.status))).length
})
const completedOrders = computed(() => {
  const list = ordersData.value ?? []
  return list.filter((item: any) => String(item.status) === 'completed').length
})
const invoicesTotal = computed(() => invoicesData.value?.length ?? 0)
const invoicesPaid = computed(() => (invoicesData.value ?? []).filter((item: any) => item.status === 'paid').length)
const invoicesOpen = computed(() => (invoicesData.value ?? []).filter((item: any) => item.status !== 'paid').length)

const logout = () => {
  auth.logout()
  router.push("/login")
}

const profile = computed(() => ({
  id: auth.user?.id ?? 1,
  username: auth.user?.username ?? "User",
  email: auth.user?.email ?? "-",
  role: auth.user?.role ?? "user",
}))

const aiKeyInput = ref('')
const aiKeyMasked = ref<string | null>(null)
const aiKeyLoading = ref(false)
const aiKeySaving = ref(false)
const aiKeyRemoving = ref(false)
const aiKeyMessage = ref('')
const hasAiKey = computed(() => Boolean(aiKeyMasked.value))

const loadAiKeyStatus = async () => {
  if (!auth.token) return
  aiKeyLoading.value = true
  aiKeyMessage.value = ''
  try {
    const data = await $fetch<{ has_key: boolean; masked_key: string | null }>(
      `${config.public.apiBase}/users/me/ai-key`,
      {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      }
    )
    aiKeyMasked.value = data.has_key ? data.masked_key : null
  } catch (error) {
    console.error(error)
    aiKeyMessage.value = 'Не удалось загрузить статус API ключа.'
  } finally {
    aiKeyLoading.value = false
  }
}

const saveAiKey = async () => {
  if (!auth.token) return
  if (!aiKeyInput.value.trim()) {
    aiKeyMessage.value = 'Введите API ключ.'
    return
  }
  aiKeySaving.value = true
  aiKeyMessage.value = ''
  try {
    const data = await $fetch<{ has_key: boolean; masked_key: string | null }>(
      `${config.public.apiBase}/users/me/ai-key`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
        body: {
          api_key: aiKeyInput.value.trim(),
        },
      }
    )
    aiKeyMasked.value = data.masked_key
    aiKeyInput.value = ''
    aiKeyMessage.value = 'API ключ сохранен.'
  } catch (error) {
    console.error(error)
    aiKeyMessage.value = 'Ошибка сохранения API ключа.'
  } finally {
    aiKeySaving.value = false
  }
}

const removeAiKey = async () => {
  if (!auth.token || !hasAiKey.value) return
  aiKeyRemoving.value = true
  aiKeyMessage.value = ''
  try {
    await $fetch(`${config.public.apiBase}/users/me/ai-key`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    })
    aiKeyMasked.value = null
    aiKeyInput.value = ''
    aiKeyMessage.value = 'API ключ удален.'
  } catch (error) {
    console.error(error)
    aiKeyMessage.value = 'Ошибка удаления API ключа.'
  } finally {
    aiKeyRemoving.value = false
  }
}

onMounted(() => {
  loadAiKeyStatus()
})

watch(() => auth.token, () => {
  loadAiKeyStatus()
})

const roleLabel = computed(() => {
  if (profile.value.role === 'admin') return 'Администратор'
  if (profile.value.role === 'mechanic') return 'Механик'
  if (profile.value.role === 'dev') return 'Разработчик'
  return 'Клиент'
})

const currentRouteLabel = computed(() => {
  if (profile.value.role === 'admin' || profile.value.role === 'dev') return 'Панель управления'
  if (profile.value.role === 'mechanic') return 'Очередь механика'
  return 'Личный кабинет клиента'
})

const garageLink = computed(() => {
  if (profile.value.role === 'admin' || profile.value.role === 'dev') return '/admin/garage'
  if (profile.value.role === 'mechanic') return '/mechanic/orders'
  return '/user/garage'
})

const invoicesLink = computed(() => {
  if (profile.value.role === 'admin' || profile.value.role === 'dev') return '/admin/estimate'
  if (profile.value.role === 'mechanic') return '/mechanic/orders'
  return '/user/invoices'
})
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Профиль</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Рабочая информация аккаунта и текущие показатели системы.
      </p>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1fr_1.2fr]">
      <div class="space-y-6">
        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <div class="flex items-center gap-4">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-500/15 text-2xl font-bold text-cyan-300">
              {{ profile.username.charAt(0).toUpperCase() }}
            </div>

            <div>
              <h2 class="text-xl font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.username }}</h2>
              <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ profile.email }}</p>
              <p class="mt-2 inline-flex rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                {{ roleLabel }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Действия</h3>

          <div class="mt-5 space-y-3">
            <NuxtLink
              :to="garageLink"
              class="block rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-sm text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
            >
              Открыть рабочий раздел
            </NuxtLink>

            <NuxtLink
              :to="invoicesLink"
              class="block rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-sm text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
            >
              Открыть финансы и заявки
            </NuxtLink>

            <button
              @click="logout"
              class="w-full rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark transition hover:bg-red-700"
            >
              Выйти
            </button>
          </div>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Системный контекст</h3>
          <div class="mt-4 space-y-3 text-sm">
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark p-3">
              <p class="text-text-muted dark:text-text-muted">Текущий раздел</p>
              <p class="mt-1 font-medium text-text dark:text-text-dark">{{ currentRouteLabel }}</p>
            </div>
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark p-3">
              <p class="text-text-muted dark:text-text-muted">Роль доступа</p>
              <p class="mt-1 font-medium text-text dark:text-text-dark">{{ roleLabel }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="grid gap-4 md:grid-cols-3">
          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Машин</p>
            <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ carsCount }}</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Активных заявок</p>
            <p class="mt-2 text-2xl font-bold text-cyan-300">{{ activeOrders }}</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Завершённых</p>
            <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ completedOrders }}</p>
          </div>
        </div>

        <div class="grid gap-4 md:grid-cols-3">
          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Счетов всего</p>
            <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoicesTotal }}</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Открытые счета</p>
            <p class="mt-2 text-2xl font-bold text-amber-300">{{ invoicesOpen }}</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Оплачено</p>
            <p class="mt-2 text-2xl font-bold text-emerald-300">{{ invoicesPaid }}</p>
          </div>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Данные аккаунта</h3>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">ID пользователя</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.id }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Роль</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ roleLabel }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4 md:col-span-2">
              <p class="text-sm text-text-muted dark:text-text-muted">Email</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.email }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Настройки ИИ</h3>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
            Персональный API ключ хранится на сервере в зашифрованном виде.
          </p>

          <div class="mt-5 space-y-3">
            <label class="block text-sm text-text-muted dark:text-text-muted">API ключ</label>
            <input
              v-model="aiKeyInput"
              type="password"
              autocomplete="off"
              placeholder="Введите API ключ"
              class="w-full rounded-xl border border-border bg-bg px-4 py-3 text-sm text-text outline-none transition focus:border-cyan-400 dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
            />

            <p v-if="aiKeyLoading" class="text-xs text-text-muted dark:text-text-muted">Загрузка статуса ключа...</p>
            <p v-else-if="hasAiKey" class="text-xs text-emerald-300">Ключ сохранен: {{ aiKeyMasked }}</p>
            <p v-else class="text-xs text-text-muted dark:text-text-muted">Ключ не сохранен.</p>

            <p v-if="aiKeyMessage" class="text-xs text-cyan-300">{{ aiKeyMessage }}</p>

            <div class="flex flex-wrap gap-2">
              <button
                class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
                :disabled="aiKeySaving"
                @click="saveAiKey"
              >
                {{ aiKeySaving ? 'Сохранение...' : 'Сохранить ключ' }}
              </button>
              <button
                class="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-300 transition hover:bg-red-500/20 disabled:opacity-50"
                :disabled="!hasAiKey || aiKeyRemoving"
                @click="removeAiKey"
              >
                {{ aiKeyRemoving ? 'Удаление...' : 'Удалить ключ' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
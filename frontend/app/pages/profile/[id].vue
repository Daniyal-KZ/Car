<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const router = useRouter()
const auth = useAuthStore()

const logout = () => {
  auth.logout()
  router.push("/login")
}

const profile = computed(() => ({
  id: auth.user?.id ?? 1,
  username: auth.user?.username ?? "Daniyal",
  email: auth.user?.email ?? "daniyal@example.com",
  role: auth.user?.role ?? "user",
  carsCount: 3,
  activeRequests: 2,
  completedOrders: 8,
}))
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Профиль</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Личная информация, активность и быстрые действия по аккаунту.
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
                {{ profile.role }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Действия</h3>

          <div class="mt-5 space-y-3">
            <NuxtLink
              to="/user/garage"
              class="block rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-sm text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
            >
              Перейти в гараж
            </NuxtLink>

            <NuxtLink
              to="/user/invoices"
              class="block rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-sm text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
            >
              Открыть счета
            </NuxtLink>

            <button
              @click="logout"
              class="w-full rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark transition hover:bg-red-700"
            >
              Выйти из аккаунта
            </button>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="grid gap-4 md:grid-cols-3">
          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Машин</p>
            <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.carsCount }}</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Активных заявок</p>
            <p class="mt-2 text-2xl font-bold text-cyan-300">{{ profile.activeRequests }}</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Завершённых</p>
            <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.completedOrders }}</p>
          </div>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">О пользователе</h3>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">ID пользователя</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.id }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Роль</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.role }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4 md:col-span-2">
              <p class="text-sm text-text-muted dark:text-text-muted">Email</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ profile.email }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
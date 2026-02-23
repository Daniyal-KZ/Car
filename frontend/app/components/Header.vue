<template>
  <header class="w-full border-b border-slate-800 bg-slate-950 text-slate-200">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

      <!-- Лого -->
      <NuxtLink to="/" class="text-2xl font-semibold tracking-tight">
        Car<span class="text-cyan-400">Service</span>
      </NuxtLink>

      <!-- Навигация -->
      <nav class="hidden md:flex items-center gap-8 text-sm font-medium">

        <!-- MECHANIC -->
        <template v-if="role === 'admin'">
          <NuxtLink to="/garage" class="nav-link">Гараж</NuxtLink>
          <NuxtLink to="/inspection" class="nav-link">Тех. осмотр</NuxtLink>
          <NuxtLink to="/diagnostics" class="nav-link">Диагностика</NuxtLink>
          <NuxtLink to="/defects" class="nav-link">Детекция дефектов</NuxtLink>
          <NuxtLink to="/assistant" class="nav-link">ИИ ассистент</NuxtLink>
          <NuxtLink to="/inspections-ref" class="nav-link">Регламенты ТО</NuxtLink>
          <NuxtLink to="/estimate" class="nav-link">Расчёт сметы</NuxtLink>
        </template>

        <!-- USER -->
        <template v-else-if="role === 'user'">
          <NuxtLink to="/my-garage" class="nav-link">Мой гараж</NuxtLink>
          <NuxtLink to="/inspection" class="nav-link">Регламентное ТО</NuxtLink>
          <NuxtLink to="/inspection-request" class="nav-link">Записаться</NuxtLink>
          <NuxtLink to="/diagnostics-request" class="nav-link">Диагностика</NuxtLink>
          <NuxtLink to="/upload-damage" class="nav-link">Повреждения</NuxtLink>
          <NuxtLink to="/assistant" class="nav-link">ИИ ассистент</NuxtLink>
          <NuxtLink to="/invoices" class="nav-link">Счета</NuxtLink>
        </template>

        <!-- DEV -->
        <template v-else-if="role === 'dev'">
          <NuxtLink to="/garage" class="nav-link">Гараж</NuxtLink>
          <NuxtLink to="/inspection" class="nav-link">Осмотр</NuxtLink>
          <NuxtLink to="/diagnostics" class="nav-link">Диагностика</NuxtLink>
          <NuxtLink to="/defects" class="nav-link">Дефекты</NuxtLink>
          <NuxtLink to="/estimate" class="nav-link">Сметы</NuxtLink>
          <NuxtLink to="/assistant" class="nav-link">ИИ ассистент</NuxtLink>
          <NuxtLink to="/dev-panel" class="nav-link text-cyan-400">Dev Panel</NuxtLink>
        </template>

      </nav>

      <div class="flex items-center gap-5">

        <template v-if="auth.isAuth">
          <NuxtLink
            :to="`/profile/${auth.user?.id}`"
            class="text-sm text-slate-400 hover:text-cyan-400 transition"
          >
            {{ auth.user?.username }}
          </NuxtLink>
        </template>

        <template v-else>
          <NuxtLink
            to="/login"
            class="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-black rounded-lg text-sm font-semibold transition"
          >
            Войти
          </NuxtLink>
        </template>

      </div>

    </div>
  </header>
</template>

<script setup lang="ts">
const auth = useAuthStore()


const role = computed(() => auth.user?.role)
</script>

<style scoped>
.nav-link {
  @apply text-slate-400 hover:text-cyan-400 transition duration-200;
}
</style>
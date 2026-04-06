<template>
  <header class="w-full border-b border-border bg-bg dark:bg-bg-dark dark:bg-bg text-text dark:text-text-dark dark:border-border dark:border-border-dark dark:text-text">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

      <!-- LOGO -->
      <NuxtLink to="/" class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-white text-sm font-semibold text-black border border-slate-200 shadow-sm transition hover:bg-slate-100 dark:bg-slate-800 dark:text-white dark:border-slate-600/30 dark:hover:bg-slate-700/40">
        CS
      </NuxtLink>

      <!-- NAV -->
      <nav class="hidden md:flex items-center gap-8 text-sm font-medium">
        <NuxtLink
          v-for="item in menuItems"
          :key="item.to"
          :to="localePath(item.to)"
          class="nav-link"
        >
          {{ t(item.label) }}
        </NuxtLink>
      </nav>

      <!-- RIGHT SIDE -->
      <div class="flex items-center gap-4">

        <!-- LANGUAGE, THEME, USER -->
        <div class="flex items-center gap-2">
          <select
            v-model="selectedLocale"
            class="h-10 rounded-full px-3 text-sm font-semibold text-text dark:text-text-dark bg-bg dark:bg-bg-dark border border-slate-300/30 dark:border-slate-600/30 focus:outline-none focus:ring-2 focus:ring-cyan-300/50 dark:focus:ring-cyan-400/30 transition"
          >
            <option v-for="item in localeOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
          <button
            @click="toggleTheme"
            type="button"
            aria-label="Toggle theme"
            class="h-10 w-10 rounded-full inline-flex items-center justify-center text-sm font-semibold transition text-text dark:text-text-dark bg-transparent border border-slate-300/30 dark:border-slate-600/30 hover:bg-slate-100/60 dark:hover:bg-slate-700/40"
          >
            {{ isDark ? '🌙' : '☀️' }}
          </button>
          <NuxtLink
            v-if="auth.isAuth"
            :to="localePath(`/profile/${auth.user?.id}`)"
            class="h-10 w-10 rounded-full inline-flex items-center justify-center text-sm font-semibold text-text dark:text-text-dark bg-transparent border border-slate-300/30 dark:border-slate-600/30 hover:bg-slate-100/60 dark:hover:bg-slate-700/40"
          >
            {{ userInitials }}
          </NuxtLink>
        </div>

      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#i18n'

const auth = useAuthStore()

// 💥 ВАЖНО: setLocale
const { t, locale, setLocale } = useI18n()
const localePath = useLocalePath()

const localeOptions = [
  { value: 'kz', label: 'KZ' },
  { value: 'ru', label: 'RU' },
  { value: 'en', label: 'EN' },
]

const selectedLocale = computed({
  get: () => locale.value,
  set: (value: string) => setLocale(value),
})

const userInitials = computed(() => {
  const username = auth.user?.username ?? ''
  const parts = username.split(/\s+/).filter(Boolean)
  if (parts.length === 0) return ''
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[1][0]).toUpperCase()
})

const navByRole = {
  user: [
    { label: 'garage', to: '/user/garage' },
    { label: 'maintenance', to: '/user/maintenance' },
    { label: 'booking', to: '/user/booking' },
    { label: 'diagnostics', to: '/user/diagnostics' },
    { label: 'damages', to: '/user/damages' },
    { label: 'assistant', to: '/user/assistant' },
    { label: 'invoices', to: '/user/invoices' },
  ],
  admin: [
    { label: 'garage', to: '/admin/garage' },
    { label: 'inspection', to: '/admin/inspection' },
    { label: 'diagnostics', to: '/admin/diagnostics' },
    { label: 'defects', to: '/admin/defects' },
    { label: 'assistant', to: '/admin/assistant' },
    { label: 'maintenance_rules', to: '/admin/maintenance-rules' },
    { label: 'estimate', to: '/admin/estimate' },
  ],
  dev: [
    { label: 'garage', to: '/admin/garage' },
    { label: 'inspection', to: '/admin/inspection' },
    { label: 'diagnostics', to: '/admin/diagnostics' },
    { label: 'defects', to: '/admin/defects' },
    { label: 'assistant', to: '/admin/assistant' },
    { label: 'maintenance_rules', to: '/admin/maintenance-rules' },
    { label: 'estimate', to: '/admin/estimate' },
    { label: 'dev_panel', to: '/dev-panel' },
  ],
}

const role = computed(() => auth.user?.role ?? 'user')
const menuItems = computed(() => navByRole[role.value] ?? navByRole.user)

const isDark = ref(false)

onMounted(() => {
  isDark.value = localStorage.getItem('theme') === 'dark'
})

const toggleTheme = () => {
  isDark.value = !isDark.value

  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

</script>

<style scoped>
.nav-link {
  @apply text-text-muted dark:text-text-muted hover:text-cyan-400 transition duration-200;
}
</style>
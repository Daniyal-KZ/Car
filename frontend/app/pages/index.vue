<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  middleware: ["auth", "role"],
})

const auth = useAuthStore()
const { t } = useI18n()

const dashboardLink = computed(() => {
  if (auth.user?.role === "admin" || auth.user?.role === "dev") {
    return "/admin/garage"
  }
  if (auth.user?.role === "mechanic") {
    return "/mechanic/orders"
  }
  return "/user/garage"
})
</script>

<template>
  <div class="mx-auto w-full max-w-4xl px-4 py-16">
    <section>
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-text dark:text-text-dark dark:text-text dark:text-text-dark sm:text-5xl">
          {{ t('home_title_line1') }}
          <span class="text-cyan-300">{{ t('home_title_line2') }}</span>
        </h1>

        <p class="mt-5 max-w-2xl text-base leading-7 text-text-muted dark:text-text-muted">
          {{ t('home_subtitle') }}
        </p>

        <div class="mt-8 flex flex-wrap gap-4">
          <NuxtLink
            :to="dashboardLink"
            class="rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
          >
            {{ t('home_enter') }}
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>
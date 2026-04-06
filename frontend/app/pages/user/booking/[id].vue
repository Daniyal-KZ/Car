<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const item = computed(() => ({
  id: route.params.id,
  code: `B-${route.params.id}`,
  car: "Toyota Camry 70",
  service: "Регламентное ТО",
  date: "24.03.2026",
  time: "11:00",
  status: "Подтверждено",
  comment: "Плановое обслуживание по пробегу",
}))
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Запись {{ item.code }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Детали записи</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/booking')"
      >
        Назад
      </button>
    </div>

    <div class="grid gap-6 md:grid-cols-2">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Информация</h2>

        <div class="mt-5 space-y-4">
          <div><p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.car }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Услуга</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.service }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Дата и время</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.date }} • {{ item.time }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Статус</p><p class="mt-1 text-cyan-300">{{ item.status }}</p></div>
        </div>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Комментарий</h2>
        <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">{{ item.comment }}</p>
      </div>
    </div>
  </div>
</template>
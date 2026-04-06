<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const services = [
  "Регламентное ТО",
  "Компьютерная диагностика",
  "Диагностика подвески",
  "Осмотр повреждений",
]
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Новая запись в сервис</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Выберите машину, услугу и удобное время посещения.
      </p>
    </div>

    <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
      <div class="grid gap-4 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Автомобиль</label>
          <select class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none">
            <option>Toyota Camry 70</option>
            <option>Hyundai Elantra</option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Услуга</label>
          <select class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none">
            <option v-for="service in services" :key="service">{{ service }}</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Дата</label>
          <input type="date" class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none" />
        </div>

        <div>
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Время</label>
          <input type="time" class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none" />
        </div>

        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Комментарий</label>
          <textarea
            rows="5"
            placeholder="Комментарий к визиту..."
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />
        </div>
      </div>

      <div class="mt-6 flex gap-3">
        <button class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
          Создать запись
        </button>
        <button
          class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
          @click="navigateTo('/user/booking')"
        >
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const checklist = [
  "Проверка тормозной системы",
  "Осмотр подвески",
  "Проверка жидкостей",
  "Осмотр шин и дисков",
  "Проверка освещения",
]
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Осмотр I-{{ route.params.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Тех. осмотр автомобиля</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/admin/inspection')"
      >
        Назад
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Toyota Camry 70</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">VIN</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">JTNB11HK0XX123456</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Пробег</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">86 420 км</p>
      </div>
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Клиент</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Daniyal</p>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.2fr_0.9fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Чек-лист осмотра</h2>

        <div class="mt-5 space-y-3">
          <label
            v-for="item in checklist"
            :key="item"
            class="flex items-center gap-3 rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4 text-text dark:text-text-dark"
          >
            <input type="checkbox" class="h-4 w-4" />
            <span>{{ item }}</span>
          </label>
        </div>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Заключение</h2>

        <div class="mt-5 space-y-4">
          <select class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none">
            <option>Исправно</option>
            <option>Требуется обслуживание</option>
            <option>Нужен ремонт</option>
          </select>

          <textarea
            rows="8"
            placeholder="Комментарий по результатам осмотра..."
            class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />

          <button class="w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
            Сохранить осмотр
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
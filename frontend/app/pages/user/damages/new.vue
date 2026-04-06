<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const damageTypes = ["Царапина", "Вмятина", "Скол", "Трещина"]
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Новая заявка на осмотр повреждений</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Загрузите фото и отправьте машину на оценку повреждений.
      </p>
    </div>

    <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
      <div class="grid gap-4">
        <div>
          <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Автомобиль</label>
          <select class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none">
            <option>Toyota Camry 70</option>
            <option>Hyundai Elantra</option>
          </select>
        </div>

        <div class="rounded-3xl border border-dashed border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ px-6 py-16 text-center">
          <p class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Зона загрузки фото</p>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Позже подключим реальную загрузку файлов</p>
          <button class="mt-5 rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark px-5 py-3 text-sm text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300">
            Выбрать изображения
          </button>
        </div>
      </div>

      <div class="mt-6">
        <p class="mb-3 text-sm text-text-muted dark:text-text-muted">Тип повреждения</p>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="item in damageTypes"
            :key="item"
            class="rounded-full border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <div class="mt-6 flex gap-3">
        <button class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
          Отправить заявку
        </button>
        <button
          class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
          @click="navigateTo('/user/damages')"
        >
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const defects = [
  { type: "Царапина", zone: "Передний бампер", severity: "Средняя" },
  { type: "Вмятина", zone: "Правая часть бампера", severity: "Высокая" },
]
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Заявка F-{{ route.params.id }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Повреждения автомобиля</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/admin/defects')"
      >
        Назад
      </button>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Фото автомобиля</h2>

        <div class="mt-5 flex min-h-[420px] items-center justify-center rounded-3xl border border-dashed border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/">
          <div class="text-center">
            <p class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Область изображения</p>
            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Позже сюда подключим фото и разметку дефектов</p>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Найденные дефекты</h2>

          <div class="mt-5 space-y-3">
            <div
              v-for="item in defects"
              :key="`${item.type}-${item.zone}`"
              class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4"
            >
              <p class="font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.type }}</p>
              <p class="mt-1 text-sm text-text-muted dark:text-text-muted">{{ item.zone }}</p>
              <p class="mt-2 text-sm text-text dark:text-text-dark dark:text-slate-300">Степень: {{ item.severity }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Комментарий мастера</h2>

          <textarea
            rows="6"
            placeholder="Комментарий по повреждениям..."
            class="mt-5 w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none"
          />

          <button class="mt-4 w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
            Сохранить результат
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
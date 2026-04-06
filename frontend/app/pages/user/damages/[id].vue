<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const item = computed(() => ({
  id: route.params.id,
  code: `F-${route.params.id}`,
  car: "Toyota Camry 70",
  status: "Готово",
  zone: "Передний бампер / правая дверь",
  severity: "Средняя",
  result: "Требуется осмотр и расчёт сметы. Вероятны работы по восстановлению поверхности и локальной покраске.",
}))
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Заявка {{ item.code }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Результат осмотра повреждений</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/damages')"
      >
        Назад
      </button>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Фото и зона повреждения</h2>

        <div class="mt-5 flex min-h-[360px] items-center justify-center rounded-3xl border border-dashed border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/">
          <div class="text-center">
            <p class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Область изображения</p>
            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">Позже сюда подключим реальные фото</p>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Сводка</h2>

          <div class="mt-5 space-y-4">
            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.car }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Зона</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.zone }}</p>
            </div>

            <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
              <p class="text-sm text-text-muted dark:text-text-muted">Степень</p>
              <p class="mt-2 font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.severity }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Комментарий</h2>
          <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">{{ item.result }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
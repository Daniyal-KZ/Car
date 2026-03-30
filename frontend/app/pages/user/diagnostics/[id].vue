<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const item = computed(() => ({
  id: route.params.id,
  code: `D-${route.params.id}`,
  car: "Toyota Camry 70",
  vin: "JTNB11HK0XX123456",
  mileage: "86 420 км",
  symptom: "Стук в подвеске на неровностях",
  status: "Готово",
  result: "Вероятная проблема связана с элементами передней подвески. Рекомендуется проверить стойки, втулки стабилизатора и опоры.",
  priority: "Средний",
}))
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-slate-500">Заявка {{ item.code }}</p>
        <h1 class="mt-1 text-3xl font-bold text-white">Результат диагностики</h1>
      </div>

      <button
        class="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/diagnostics')"
      >
        Назад
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
        <p class="text-sm text-slate-400">Автомобиль</p>
        <p class="mt-2 font-semibold text-white">{{ item.car }}</p>
      </div>
      <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
        <p class="text-sm text-slate-400">VIN</p>
        <p class="mt-2 font-semibold text-white">{{ item.vin }}</p>
      </div>
      <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
        <p class="text-sm text-slate-400">Пробег</p>
        <p class="mt-2 font-semibold text-white">{{ item.mileage }}</p>
      </div>
      <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
        <p class="text-sm text-slate-400">Статус</p>
        <p class="mt-2 font-semibold text-cyan-300">{{ item.status }}</p>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
        <h2 class="text-lg font-semibold text-white">Симптомы</h2>
        <p class="mt-4 text-sm leading-6 text-slate-300">{{ item.symptom }}</p>
      </div>

      <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
        <h2 class="text-lg font-semibold text-white">Результат</h2>
        <p class="mt-4 text-sm leading-6 text-slate-300">{{ item.result }}</p>

        <div class="mt-5 rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
          <p class="text-sm text-slate-400">Приоритет</p>
          <p class="mt-2 font-medium text-white">{{ item.priority }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
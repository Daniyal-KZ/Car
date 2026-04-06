<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const request = computed(() => ({
  id: route.params.id,
  code: `D-${route.params.id}`,
  client: "Daniyal",
  car: "Toyota Camry 70",
  vin: "JTNB11HK0XX123456",
  mileage: "86 420 км",
  phone: "+7 777 000 00 00",
  symptom: "Стук в подвеске на неровностях, особенно спереди справа. Появился 2 дня назад.",
}))
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Заявка {{ request.code }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Диагностика автомобиля</h1>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Работа с конкретной заявкой клиента и оформление результата диагностики.
        </p>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/admin/diagnostics')"
      >
        Назад
      </button>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-4">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ request.car }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">VIN</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ request.vin }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Пробег</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ request.mileage }}</p>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-4">
        <p class="text-sm text-text-muted dark:text-text-muted">Клиент</p>
        <p class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ request.client }}</p>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.1fr_1.2fr]">
      <div class="space-y-6">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Описание клиента</h2>
          <p class="mt-4 text-sm leading-6 text-text dark:text-text-dark dark:text-slate-300">
            {{ request.symptom }}
          </p>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Контактные данные</h2>
          <p class="mt-4 text-sm text-text dark:text-text-dark dark:text-slate-300">Телефон: {{ request.phone }}</p>
        </div>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Результат диагностики</h2>

        <div class="mt-5 grid gap-4 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Предполагаемый узел</label>
            <input
              type="text"
              placeholder="Подвеска / рулевое управление"
              class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Приоритет</label>
            <select class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none focus:border-cyan-400">
              <option>Низкий</option>
              <option>Средний</option>
              <option>Высокий</option>
            </select>
          </div>

          <div>
            <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Статус</label>
            <select class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none focus:border-cyan-400">
              <option>Новая</option>
              <option>В работе</option>
              <option>Готово</option>
            </select>
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm text-text-muted dark:text-text-muted">Комментарий мастера</label>
            <textarea
              rows="8"
              placeholder="Опишите результат диагностики..."
              class="w-full rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-4 py-3 text-text dark:text-text-dark dark:text-text dark:text-text-dark outline-none focus:border-cyan-400"
            />
          </div>
        </div>

        <div class="mt-6 flex flex-wrap gap-3">
          <button class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
            Сохранить
          </button>
          <button class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg px-5 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300">
            Отправить клиенту
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
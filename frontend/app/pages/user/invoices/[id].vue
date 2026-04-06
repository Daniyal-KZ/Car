<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const route = useRoute()

const invoice = computed(() => ({
  id: route.params.id,
  code: `INV-${route.params.id}`,
  car: "Toyota Camry 70",
  service: "Регламентное ТО",
  date: "18.03.2026",
  amount: "45 000 ₸",
  status: "Ожидает оплаты",
  items: [
    { name: "Замена масла", price: "20 000 ₸" },
    { name: "Масляный фильтр", price: "8 000 ₸" },
    { name: "Осмотр ходовой части", price: "17 000 ₸" },
  ],
}))
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-text dark:text-slate-300">Счёт {{ invoice.code }}</p>
        <h1 class="mt-1 text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Детали счёта</h1>
      </div>

      <button
        class="rounded-xl border border-border dark:border-border dark:border-slate-700 px-4 py-2 text-sm text-text dark:text-text-dark dark:text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
        @click="navigateTo('/user/invoices')"
      >
        Назад
      </button>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Состав счёта</h2>

        <div class="mt-5 space-y-3">
          <div
            v-for="item in invoice.items"
            :key="item.name"
            class="flex items-center justify-between rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ px-4 py-3"
          >
            <span class="text-sm text-text dark:text-text-dark">{{ item.name }}</span>
            <span class="text-sm font-medium text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ item.price }}</span>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Сводка</h2>

        <div class="mt-5 space-y-4">
          <div><p class="text-sm text-text-muted dark:text-text-muted">Автомобиль</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoice.car }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Услуга</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoice.service }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Дата</p><p class="mt-1 text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoice.date }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Статус</p><p class="mt-1 text-cyan-300">{{ invoice.status }}</p></div>
          <div><p class="text-sm text-text-muted dark:text-text-muted">Итого</p><p class="mt-1 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoice.amount }}</p></div>
        </div>

        <button class="mt-6 w-full rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
          Оплатить
        </button>
      </div>
    </div>
  </div>
</template>
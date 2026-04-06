<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const invoices = [
  {
    id: 401,
    code: "INV-401",
    car: "Toyota Camry 70",
    service: "Регламентное ТО",
    date: "18.03.2026",
    amount: "45 000 ₸",
    status: "Ожидает оплаты",
  },
  {
    id: 402,
    code: "INV-402",
    car: "Hyundai Elantra",
    service: "Диагностика",
    date: "10.03.2026",
    amount: "12 000 ₸",
    status: "Оплачено",
  },
]

const openInvoice = (id: number) => navigateTo(`/user/invoices/${id}`)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Счета</h1>
      <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
        Все счета по вашим услугам и автомобилям.
      </p>
    </div>

    <div class="space-y-4">
      <button
        v-for="invoice in invoices"
        :key="invoice.id"
        class="w-full rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5 text-left transition hover:border-cyan-400"
        @click="openInvoice(invoice.id)"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">{{ invoice.code }}</h2>
              <span class="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
                {{ invoice.status }}
              </span>
            </div>

            <p class="mt-2 text-sm text-text-muted dark:text-text-muted">{{ invoice.car }} • {{ invoice.service }}</p>
            <p class="mt-3 text-sm text-text dark:text-text-dark dark:text-slate-300">{{ invoice.date }} • {{ invoice.amount }}</p>
          </div>

          <div class="text-sm font-medium text-cyan-300">Открыть →</div>
        </div>
      </button>
    </div>
  </div>
</template>
<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

const symptoms = [
  "Стук в подвеске",
  "Вибрация на скорости",
  "Горит Check Engine",
  "Шум при торможении",
]
</script>

<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-white">Новая заявка на диагностику</h1>
      <p class="mt-2 text-sm text-slate-400">
        Опишите проблему и отправьте автомобиль на диагностику.
      </p>
    </div>

    <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
      <div class="grid gap-4 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-slate-400">Автомобиль</label>
          <select class="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none">
            <option>Toyota Camry 70</option>
            <option>Hyundai Elantra</option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="mb-2 block text-sm text-slate-400">Описание проблемы</label>
          <textarea
            rows="7"
            placeholder="Опишите симптомы..."
            class="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
          />
        </div>
      </div>

      <div class="mt-6">
        <p class="mb-3 text-sm text-slate-400">Быстрые симптомы</p>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="item in symptoms"
            :key="item"
            class="rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
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
          class="rounded-2xl border border-slate-700 bg-slate-950 px-5 py-3 text-sm font-medium text-slate-200 transition hover:border-cyan-400 hover:text-cyan-300"
          @click="navigateTo('/user/diagnostics')"
        >
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "role"],
})

const auth = useAuthStore()

const dashboardLink = computed(() => {
  if (auth.user?.role === "admin" || auth.user?.role === "dev") {
    return "/admin/garage"
  }
  return "/user/garage"
})
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-10">
    <section class="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
      <div>
        <div
          class="mb-4 inline-flex rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-xs font-medium text-cyan-300"
        >
          Smart Car Service Platform
        </div>

        <h1 class="text-4xl font-bold tracking-tight text-text dark:text-text-dark dark:text-text dark:text-text-dark sm:text-5xl">
          Цифровая платформа
          <span class="text-cyan-300">автосервиса</span>
          для клиентов и механиков
        </h1>

        <p class="mt-5 max-w-2xl text-base leading-7 text-text-muted dark:text-text-muted">
          Единое пространство для работы с автомобилями: гараж, регламентное ТО,
          диагностика, повреждения, сметы, счета и ИИ-ассистент для ускорения
          сервиса и удобства клиента.
        </p>

        <div class="mt-8 flex flex-wrap gap-4">
          <NuxtLink
            :to="dashboardLink"
            class="rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
          >
            Перейти в систему
          </NuxtLink>

          <NuxtLink
            to="/about"
            class="rounded-2xl border border-border dark:border-border dark:border-slate-700 bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark px-6 py-3 text-sm font-medium text-text dark:text-text-dark transition hover:border-cyan-400 hover:text-cyan-300"
          >
            Подробнее о проекте
          </NuxtLink>
        </div>
      </div>

      <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Модулей системы</p>
            <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">7+</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Роли</p>
            <p class="mt-2 text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">User / Admin</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Стек</p>
            <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Nuxt 4 + FastAPI</p>
          </div>

          <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-bg-dark/ p-4">
            <p class="text-sm text-text-muted dark:text-text-muted">Фокус</p>
            <p class="mt-2 text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Автосервис</p>
          </div>
        </div>
      </div>
    </section>

    <section class="mt-14">
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Что умеет система</h2>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Основные возможности платформы для клиента и для механика.
        </p>
      </div>

      <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Гараж</h3>
          <p class="mt-3 text-sm leading-6 text-text-muted dark:text-text-muted">
            Хранение автомобилей пользователя, просмотр карточек машин и работа
            с данными по каждому авто.
          </p>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Регламентное ТО</h3>
          <p class="mt-3 text-sm leading-6 text-text-muted dark:text-text-muted">
            Подсказки по техническому обслуживанию на основе пробега, модели и
            состояния автомобиля.
          </p>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Диагностика</h3>
          <p class="mt-3 text-sm leading-6 text-text-muted dark:text-text-muted">
            Клиент описывает симптомы, а механик получает отдельную заявку и
            оформляет результат по конкретной машине.
          </p>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Повреждения</h3>
          <p class="mt-3 text-sm leading-6 text-text-muted dark:text-text-muted">
            Работа с фото автомобиля, предварительная оценка повреждений и
            переход к обработке заявок мастером.
          </p>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Сметы и счета</h3>
          <p class="mt-3 text-sm leading-6 text-text-muted dark:text-text-muted">
            Формирование сметы ремонта, расчёт стоимости работ и деталей, а
            также просмотр счетов клиентом.
          </p>
        </div>

        <div class="rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-6">
          <h3 class="text-lg font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">ИИ ассистент</h3>
          <p class="mt-3 text-sm leading-6 text-text-muted dark:text-text-muted">
            Помощник по диагностике, обслуживанию, сервисным сценариям и работе
            с клиентскими запросами.
          </p>
        </div>
      </div>
    </section>

    <section class="mt-14">
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Как устроена работа</h2>
        <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
          Поток от заявки клиента до результата сервиса.
        </p>
      </div>

      <div class="grid gap-4 md:grid-cols-4">
        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5">
          <p class="text-sm text-text dark:text-slate-300">Шаг 1</p>
          <h3 class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Клиент создаёт запрос</h3>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
            Запись, диагностика, повреждение или обслуживание.
          </p>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5">
          <p class="text-sm text-text dark:text-slate-300">Шаг 2</p>
          <h3 class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Сервис обрабатывает заявку</h3>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
            Механик открывает конкретную карточку машины и вносит результат.
          </p>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5">
          <p class="text-sm text-text dark:text-slate-300">Шаг 3</p>
          <h3 class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Формируется решение</h3>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
            Диагноз, регламент, смета ремонта или итог осмотра.
          </p>
        </div>

        <div class="rounded-2xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-5">
          <p class="text-sm text-text dark:text-slate-300">Шаг 4</p>
          <h3 class="mt-2 font-semibold text-text dark:text-text-dark dark:text-text dark:text-text-dark">Клиент получает результат</h3>
          <p class="mt-2 text-sm text-text-muted dark:text-text-muted">
            Через личный кабинет, счета и дальнейшие действия по машине.
          </p>
        </div>
      </div>
    </section>

    <section class="mt-14 rounded-3xl border border-border dark:border-border dark:border-border-dark bg-bg dark:bg-bg-dark dark:bg-bg dark:bg-card-dark/ p-8">
      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-2xl font-bold text-text dark:text-text-dark dark:text-text dark:text-text-dark">
            Проект готов к дальнейшему развитию
          </h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-text-muted dark:text-text-muted">
            Сейчас система уже имеет готовую структуру интерфейсов и страниц.
            Следующий этап — подключение FastAPI, бизнес-логики, VIN, заявок,
            сохранения результатов и полноценной работы с данными.
          </p>
        </div>

        <NuxtLink
          :to="dashboardLink"
          class="inline-flex w-fit rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        >
          Открыть рабочую часть
        </NuxtLink>
      </div>
    </section>
  </div>
</template>
<template>
  <footer class="border-t border-border bg-bg dark:bg-bg-dark text-text-muted">
    <div class="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row justify-between items-center text-sm gap-4">

      <a
        href="https://github.com/Daniyal-KZ/Car"
        target="_blank"
        rel="noopener noreferrer"
        class="transition hover:text-text"
      >
        Ссылка на репозиторий
      </a>

      <div class="flex gap-6">
        <NuxtLink
          to="/about"
          class="transition hover:text-text"
        >
          Документация
        </NuxtLink>
      </div>

    </div>
  </footer>
</template>
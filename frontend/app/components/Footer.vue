<script setup lang="ts">
</script>
<template>
  <footer class="border-t border-gray-800 bg-gray-950 text-gray-400">
    <div class="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row justify-between items-center text-sm gap-4">
      <a
          href="https://github.com/Daniyal-KZ/Car"
          target="_blank"
          rel="noopener noreferrer"
          class="hover:text-white transition"
        >
          Ссылка на репозиторий
        </a>
      <div>
      </div>

      <div class="flex gap-6">
        <NuxtLink to="/about" class="hover:text-white transition">
          Документация
        </NuxtLink>
      </div>
    </div>
  </footer>
</template>
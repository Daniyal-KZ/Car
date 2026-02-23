<template>
  <div class="min-h-[calc(100vh-64px)] bg-black text-white">
    <div class="mx-auto max-w-7xl px-4 py-6">
      <div class="grid grid-cols-12 gap-4">
        <!-- Sidebar -->
        <aside class="col-span-12 md:col-span-4 lg:col-span-3">
          <div class="h-[calc(100vh-140px)] rounded-2xl border border-white/10 bg-white/5 backdrop-blur">
            <slot name="sidebar" />
          </div>
        </aside>

        <!-- Main -->
        <main class="col-span-12 md:col-span-8 lg:col-span-9">
          <div class="h-[calc(100vh-140px)] rounded-2xl border border-white/10 bg-white/5 backdrop-blur overflow-hidden">
            <slot />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>
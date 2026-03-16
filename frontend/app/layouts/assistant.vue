<template>

<div class="flex h-screen flex-col">

  <Header />

  <div class="flex flex-1 overflow-hidden bg-white">

    <AssistantSidebar />

    <main class="flex min-w-0 flex-1 flex-col">
      <slot />
    </main>

  </div>

</div>

</template>
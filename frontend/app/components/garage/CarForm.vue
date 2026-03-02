<script setup lang="ts">
type CarPayload = {
  brand: string
  model: string
  year: number
  mileage: number
  last_service?: number | null
}

const props = defineProps<{
  mode: "create" | "edit" | "view"
  initial?: Partial<CarPayload>
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: "submit", payload: CarPayload): void
  (e: "cancel"): void
  (e: "edit"): void
}>()

const isView = computed(() => props.mode === "view")
const isEdit = computed(() => props.mode === "edit")
const isCreate = computed(() => props.mode === "create")

const form = reactive<CarPayload>({
  brand: props.initial?.brand ?? "",
  model: props.initial?.model ?? "",
  year: props.initial?.year ?? new Date().getFullYear(),
  mileage: props.initial?.mileage ?? 0,
  last_service: props.initial?.last_service ?? 0,
})

watch(
  () => props.initial,
  (v) => {
    if (!v) return
    form.brand = v.brand ?? ""
    form.model = v.model ?? ""
    form.year = v.year ?? new Date().getFullYear()
    form.mileage = v.mileage ?? 0
    form.last_service = v.last_service ?? 0
  },
  { deep: true }
)

const submit = () => {
  emit("submit", {
    brand: form.brand.trim(),
    model: form.model.trim(),
    year: Number(form.year),
    mileage: Number(form.mileage),
    last_service: form.last_service == null ? 0 : Number(form.last_service),
  })
}
</script>

<template>
  <section class="rounded-2xl border border-gray-800 bg-gray-950 p-6">
    <div class="flex items-start justify-between gap-4 mb-6">
      <div>
        <h2 class="text-xl font-bold text-gray-100">
          <span v-if="isCreate">Добавить машину</span>
          <span v-else-if="isEdit">Редактировать</span>
          <span v-else>Машина</span>
        </h2>
        <p class="text-gray-400 text-sm mt-1">
          Сейчас без фоток — добавим потом отдельным полем, форма не сломается.
        </p>
      </div>

      <button
        v-if="isView"
        class="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-100 text-sm"
        @click="emit('edit')"
      >
        Редактировать
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm text-gray-400 mb-1">Марка</label>
        <input
          v-model="form.brand"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-gray-900 border border-gray-800 text-gray-100 outline-none focus:border-gray-600 disabled:opacity-60"
          placeholder="Toyota"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-1">Модель</label>
        <input
          v-model="form.model"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-gray-900 border border-gray-800 text-gray-100 outline-none focus:border-gray-600 disabled:opacity-60"
          placeholder="Camry"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-1">Год</label>
        <input
          v-model.number="form.year"
          type="number"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-gray-900 border border-gray-800 text-gray-100 outline-none focus:border-gray-600 disabled:opacity-60"
          placeholder="2018"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-1">Пробег (км)</label>
        <input
          v-model.number="form.mileage"
          type="number"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-gray-900 border border-gray-800 text-gray-100 outline-none focus:border-gray-600 disabled:opacity-60"
          placeholder="120000"
        />
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm text-gray-400 mb-1">Пробег при последнем ТО</label>
        <input
          v-model.number="form.last_service"
          type="number"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-gray-900 border border-gray-800 text-gray-100 outline-none focus:border-gray-600 disabled:opacity-60"
          placeholder="0"
        />
      </div>
    </div>

    <div v-if="!isView" class="flex items-center justify-end gap-3 mt-6">
      <button
        class="px-4 py-2 rounded-xl border border-gray-700 hover:bg-gray-900 text-gray-100 text-sm"
        :disabled="loading"
        @click="emit('cancel')"
      >
        Отмена
      </button>

      <button
        class="px-4 py-2 rounded-xl bg-yellow-400 text-black font-medium hover:opacity-90 transition disabled:opacity-60"
        :disabled="loading"
        @click="submit"
      >
        <span v-if="isCreate">Создать</span>
        <span v-else>Сохранить</span>
      </button>
    </div>
  </section>
</template>
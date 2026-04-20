<script setup lang="ts">
type CarImage = {
  id: number
  car_id: number
  file_path: string
  file_name: string
}

type CarPayload = {
  brand: string
  model: string
  vin: string | null
  year: number
  mileage: number
}

const props = defineProps<{
  mode: "create" | "edit" | "view"
  initial?: Partial<CarPayload> & { images?: CarImage[] }
  loading?: boolean
}>()

const { t } = useI18n()

const emit = defineEmits<{
  (e: "submit", payload: CarPayload): void
  (e: "cancel"): void
  (e: "edit"): void
  (e: "files-change", files: File[]): void
}>()

const isView = computed(() => props.mode === "view")
const isEdit = computed(() => props.mode === "edit")
const isCreate = computed(() => props.mode === "create")

const config = useRuntimeConfig()
const apiBase = computed(() => config.public.apiBase || "http://127.0.0.1:8000")

const form = reactive<CarPayload>({
  brand: props.initial?.brand ?? "",
  model: props.initial?.model ?? "",
  vin: props.initial?.vin ?? "",
  year: props.initial?.year ?? new Date().getFullYear(),
  mileage: props.initial?.mileage ?? 0,
})

const selectedFiles = ref<File[]>([])

watch(
  () => props.initial,
  (v) => {
    if (!v) return
    form.brand = v.brand ?? ""
    form.model = v.model ?? ""
      form.vin = v.vin ?? ""
    form.year = v.year ?? new Date().getFullYear()
    form.mileage = v.mileage ?? 0
  },
  { deep: true }
)

const existingImages = computed(() => props.initial?.images ?? [])

const imageUrl = (path: string) => `${apiBase.value}${path}`

const onFilesChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  selectedFiles.value = files
  emit("files-change", files)
}

const removeSelectedFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
  emit("files-change", [...selectedFiles.value])
}

const submit = () => {
  emit("submit", {
    brand: form.brand.trim(),
    model: form.model.trim(),
    year: Number(form.year),
    mileage: Number(form.mileage),
    vin: form.vin?.trim() ? form.vin.trim().toUpperCase() : null,
  })
}
</script>

<template>
  <section class="rounded-2xl border border-border bg-bg dark:border-border-dark dark:bg-bg-dark p-6">
    <div class="flex items-start justify-between gap-4 mb-6">
      <div>
        <h2 class="text-xl font-bold text-text dark:text-text-dark">
          <span v-if="isCreate">{{ t('car_form_add_title') }}</span>
          <span v-else-if="isEdit">{{ t('garage_edit') }}</span>
          <span v-else>{{ t('car_form_car_title') }}</span>
        </h2>
        <p class="text-text-muted dark:text-text-muted text-sm mt-1">
          {{ t('car_form_subtitle') }}
        </p>
      </div>

      <button
        v-if="isView"
        class="px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 text-sm transition dark:bg-bg-dark dark:text-text-dark dark:hover:bg-slate-700"
        @click="emit('edit')"
      >
        {{ t('garage_edit') }}
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm text-text-muted dark:text-text-muted mb-1">{{ t('garage_brand') }}</label>
        <input
          v-model="form.brand"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-white text-text border border-border outline-none focus:border-primary dark:bg-bg-dark dark:text-text-dark dark:border-border-dark disabled:opacity-60"
          placeholder="Toyota"
        />
      </div>

      <div>
        <label class="block text-sm text-text-muted dark:text-text-muted mb-1">{{ t('garage_model') }}</label>
        <input
          v-model="form.model"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-white text-text border border-border outline-none focus:border-primary dark:bg-bg-dark dark:text-text-dark dark:border-border-dark disabled:opacity-60"
          placeholder="Camry"
        />
      </div>

      <div>
        <label class="block text-sm text-text-muted dark:text-text-muted mb-1">{{ t('garage_year') }}</label>
        <input
          v-model.number="form.year"
          type="number"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-white text-text border border-border outline-none focus:border-primary dark:bg-bg-dark dark:text-text-dark dark:border-border-dark disabled:opacity-60"
          placeholder="2018"
        />
      </div>
      <div>
        <label class="block text-sm text-text-muted dark:text-text-muted mb-1">VIN</label>
        <input
          v-model="form.vin"
          :disabled="isView"
          maxlength="17"
          class="w-full px-4 py-2 rounded-xl bg-white text-text border border-border outline-none focus:border-primary dark:bg-bg-dark dark:text-text-dark dark:border-border-dark disabled:opacity-60"
          placeholder="JTNB11HK0XX123456"
        />
      </div>

      <div>
        <label class="block text-sm text-text-muted dark:text-text-muted mb-1">{{ t('car_form_mileage_with_unit') }}</label>
        <input
          v-model.number="form.mileage"
          type="number"
          :disabled="isView"
          class="w-full px-4 py-2 rounded-xl bg-white text-text border border-border outline-none focus:border-primary dark:bg-bg-dark dark:text-text-dark dark:border-border-dark disabled:opacity-60"
          placeholder="120000"
        />
      </div>


      <div class="md:col-span-2">
        <label class="block text-sm text-text-muted dark:text-text-muted mb-2">{{ t('car_form_current_photos') }}</label>

        <div v-if="existingImages.length" class="flex flex-wrap gap-3">
          <img
            v-for="image in existingImages"
            :key="image.id"
            :src="imageUrl(image.file_path)"
            :alt="image.file_name"
            class="h-28 w-40 rounded-xl border border-border object-cover dark:border-border-dark"
          />
        </div>

        <div
          v-else
          class="flex h-28 w-40 items-center justify-center rounded-xl border border-dashed border-border bg-white text-sm text-text-muted dark:border-border-dark dark:bg-bg-dark dark:text-text-muted"
        >
          {{ t('garage_no_photo') }}
        </div>
      </div>

      <div v-if="!isView" class="md:col-span-2">
        <label class="block text-sm text-text-muted dark:text-text-muted mb-2">{{ t('car_form_add_new_photos') }}</label>

        <input
          type="file"
          accept="image/*"
          multiple
          class="block w-full rounded-xl border border-border bg-white px-4 py-3 text-sm text-text file:mr-4 file:rounded-lg file:border-0 file:bg-yellow-400 file:px-4 file:py-2 file:text-sm file:font-medium file:text-black dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
          @change="onFilesChange"
        />

        <div v-if="selectedFiles.length" class="mt-4 flex flex-wrap gap-2">
          <div
            v-for="(file, index) in selectedFiles"
            :key="file.name + index"
            class="flex items-center gap-2 rounded-xl border border-border bg-white px-3 py-2 text-sm text-text dark:border-border-dark dark:bg-bg-dark dark:text-text-dark"
          >
            <span class="max-w-[180px] truncate">{{ file.name }}</span>
            <button
              type="button"
              class="text-red-400 hover:text-red-300"
              @click="removeSelectedFile(index)"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!isView" class="flex items-center justify-end gap-3 mt-6">
      <button
        class="px-4 py-2 rounded-xl border border-border hover:bg-slate-100 text-text text-sm dark:border-border-dark dark:hover:bg-slate-800 dark:text-text-dark"
        :disabled="loading"
        @click="emit('cancel')"
      >
        {{ t('car_form_cancel') }}
      </button>

      <button
        class="px-4 py-2 rounded-xl bg-yellow-400 text-black dark:text-text-dark dark:text-text font-medium hover:opacity-90 transition disabled:opacity-60"
        :disabled="loading"
        @click="submit"
      >
        <span v-if="isCreate">{{ t('car_form_create') }}</span>
        <span v-else>{{ t('car_form_save') }}</span>
      </button>
    </div>
  </section>
</template>
<!-- src/components/ui/Field.vue -->
<script setup>
import { ref, watch, computed, onMounted, nextTick } from "vue"
import Icon from "./Icon.vue"
import AppInput from "./Input.vue"

// importa do seu forms/
import { inputValue } from "../../forms/input-map"
import { inputFormatter } from "../../forms/input-formatter"

const props = defineProps({
  name: { type: String, required: true },
  label: { type: String, default: "" },
  icon: { type: String, default: "" },
  placeholder: { type: String, default: "" },
  modelValue: { type: [String, Number], default: "" },
  type: { type: String, default: "text" },
  editing: { type: Boolean, default: false },
})

const emit = defineEmits(["update:modelValue"])

const inputRef = ref(null)
const errorRef = ref(null)
const inner = ref(String(props.modelValue ?? ""))
const cfg = ref(inputValue(props.name))

const labelText = computed(() => props.label || cfg.value.label || props.name)
const iconName  = computed(() => props.icon || cfg.value.icon || "")
const phText    = computed(() => props.placeholder || cfg.value.placeholder || "")

function wireUp() {
  const r = inputRef.value
  const el =
    r?.$el?.querySelector?.("input, textarea") ||
    r?.$el || 
    null

  if (!el) return

  el.setAttribute("data-input-name", props.name)

  const formEl = el.closest("form")

  cfg.value = inputFormatter(props.name, el, formEl, errorRef.value)
}

function onInput(val) {
  inner.value = String(val ?? "")
  emit("update:modelValue", inner.value)
}

watch(
  () => props.modelValue,
  (v) => { inner.value = String(v ?? "") }
)

watch(
  () => props.editing,
  async (isEditing) => {
    if (isEditing) {
      await nextTick()
      wireUp()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  if (props.editing) {
    await nextTick()
    wireUp()
  }
})
</script>

<template>
  <div data-field-root>
    <label class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-400">
      {{ labelText }}
    </label>

    <template v-if="!editing">
      <div class="min-w-0">
        <p
          class="rounded-lg border border-gray-200 dark:border-gray-700 px-1 text-gray-600 dark:text-gray-200
                flex items-center py-2 overflow-hidden"
        >
          <Icon
            v-if="iconName"
            :name="iconName"
            size="20"
            class="mr-3 pl-2 text-gray-600 dark:text-gray-200 shrink-0"
          />
          <span class="truncate block w-full" :title="String(modelValue || '')">
            {{ (modelValue ?? '') !== '' ? modelValue : '-' }}
          </span>
        </p>
      </div>
    </template>

    <template v-else>
      <AppInput
        ref="inputRef"
        :type="type"
        :model-value="inner"
        @update:model-value="onInput"
        :leftIcon="iconName"
        :placeholder="phText"
        aria-invalid="false"
      />
      <p ref="errorRef" class="field-error mt-1 text-xs text-red-600 dark:text-red-400" style="display:none;"></p>
    </template>
  </div>
</template>

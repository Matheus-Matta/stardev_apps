<script setup lang="ts">
import { ref, computed, onMounted, nextTick, getCurrentInstance } from "vue";
import { FwbInput } from "flowbite-vue";

const props = defineProps({
  modelValue: { type: [String, Number], default: "" },
  type: { type: String, default: "text" },
  placeholder: { type: String, default: "" },
  label: { type: String, default: "" },
  id: { type: String, default: "" },
  message: { type: String, default: "" },
  disabled: { type: Boolean, default: false },
  messageType: { type: String, default: "info" }, // 'info' | 'error' | 'success'
  min: { type: String, default: "" },
  autofocus: { type: Boolean, default: false },
  inputClass: { type: [String, Array, Object], default: "" },
});

const emit = defineEmits(["update:modelValue", "blur", "input", "focus", "enter"]);
const { uid } = getCurrentInstance();
const uniqueId = computed(() => props.id || `input-${uid}`);
const inputRef = ref<HTMLInputElement | null>(null);

const helpColor = computed(() => {
  if (props.messageType === "error") return "text-red-600 dark:text-red-500";
  if (props.messageType === "success") return "text-green-600 dark:text-green-500";
  return "text-gray-500 dark:text-gray-400";
});

const ringClass = computed(() => {
  if (props.messageType === "error")
    return "focus:ring-2 focus:ring-red-500 ring-1 ring-red-400";
  return "focus:ring-2 focus:ring-blue-500 ring-1 ring-gray-300 dark:ring-gray-600";
});

function onInput(e: Event) {
  const val = (e.target as HTMLInputElement)?.value ?? "";
  emit("update:modelValue", val);
  emit("input", e);
}
function onFocus(e: FocusEvent) { emit("focus", e); }
function onBlur(e: FocusEvent) { emit("blur", e); }
function onKeyup(e: KeyboardEvent) { if (e.key === "Enter") emit("enter", e); }

onMounted(() => {
  if (props.autofocus) {
    nextTick(() => inputRef.value?.focus());
  }
});
</script>

<template>
  <div class="relative flex flex-col gap-1">
    <label
      v-if="label"
      :for="uniqueId"
      class="mb-0.5 text-sm font-medium text-gray-800 dark:text-gray-100"
    >
      {{ label }}
    </label>

    <div class="relative">
      <slot name="prefix" />
      <FwbInput
        :id="uniqueId"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :min="['date','datetime-local','time'].includes(type) ? min : undefined"
        :model-value="modelValue"
        @update:modelValue="val => emit('update:modelValue', val)"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
        @keyup="onKeyup"
        ref="inputRef"
        class="text-sm"
        :class="[
          'h-10 px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
          'placeholder-gray-400 dark:placeholder-gray-500 rounded-lg outline-none',
          'transition-all duration-200',
          ringClass,
          inputClass,
        ]"
      />
    </div>

    <p v-if="message" class="text-xs mt-1 truncate" :class="helpColor">
      {{ message }}
    </p>
  </div>
</template>

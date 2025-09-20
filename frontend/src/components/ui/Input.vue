<script setup lang="ts">
import { ref, computed, onMounted, nextTick, getCurrentInstance } from "vue";
import Icon from "./Icon.vue";

type Variant = "default" | "solid" | "ghost";
type Size = "sm" | "md" | "lg";

const props = defineProps({
  modelValue: { type: [String, Number], default: "" },
  type: { type: String, default: "text" },
  placeholder: { type: String, default: "" },
  label: { type: String, default: "" },
  id: { type: String, default: "" },
  message: { type: String, default: "" },
  disabled: { type: Boolean, default: false },

  messageType: { type: String, default: "info" }, // 'info' | 'error' | 'success'

  variant: { type: String as () => Variant, default: "default" },
  size: { type: String as () => Size, default: "md" },
  rounded: { type: String, default: "rounded-lg" }, // ex: 'rounded-full'
  bordered: { type: Boolean, default: true },
  inputClass: { type: [String, Array, Object], default: "" },

  leftIcon: { type: String, default: "" },
  rightIcon: { type: String, default: "" },
  leftIconClass: { type: String, default: "" },
  rightIconClass: { type: String, default: "" },

  min: { type: String, default: "" },
  autofocus: { type: Boolean, default: false },
  togglePassword: { type: Boolean, default: true },
});

const emit = defineEmits([
  "update:modelValue",
  "blur",
  "input",
  "focus",
  "enter",
  "left-icon-click",
  "right-icon-click",
]);

const { uid } = getCurrentInstance();
const uniqueId = computed(() => props.id || `input-${uid}`);
const inputRef = ref<HTMLInputElement | null>(null);

const isPassword = computed(() => props.type === "password");
const revealing = ref(false);
const effectiveType = computed(() =>
  isPassword.value && props.togglePassword ? (revealing.value ? "text" : "password") : props.type
);

/* label/help cores */
const helpColor = computed(() => {
  if (props.messageType === "error") return "text-red-600 dark:text-red-500";
  if (props.messageType === "success") return "text-green-600 dark:text-green-500";
  return "text-gray-500 dark:text-gray-400";
});

/* tamanhos */
const sizeConf = computed(() => {
  return {
    sm: { h: "h-9", text: "text-sm", icon: "size-[18px]" },
    md: { h: "h-10", text: "text-sm", icon: "size-[20px]" },
    lg: { h: "h-11", text: "text-base", icon: "size-[22px]" },
  }[props.size];
});

/* presença de ícones */
const hasLeftIcon = computed(() => !!props.leftIcon);
const hasRightIcon = computed(() => !!props.rightIcon || (isPassword.value && props.togglePassword));

/* container (igual ao seu exemplo, mas com focus azul) */
const containerClass = computed(() => {
  const base =
    "group relative flex items-center transition-shadow focus-within:ring-2 focus-within:ring-blue-500";

  const bg =
    props.variant === "ghost"
      ? "bg-transparent"
      : props.variant === "solid"
      ? "bg-gray-200/40 dark:bg-gray-900/40"
      : "bg-gray-200/20 dark:bg-slate-900/40";

  const border = props.bordered
    ? (props.messageType === "error"
        ? "border border-red-400 dark:border-red-500"
        : "border border-slate-200 dark:border-slate-700")
    : "border-0";

  return [base, props.rounded, bg, border].join(" ");
});

/* input padding conforme ícones */
const inputPadding = computed(() => {
  const pl = hasLeftIcon.value ? "pl-10" : "pl-4";
  const pr = hasRightIcon.value ? "pr-10" : "pr-4";
  return `${pl} ${pr}`;
});

/* estado disabled sólido */
const disabledSolid = computed(() =>
  props.disabled
    ? "text-gray-700 dark:text-gray-300"
    : "bg-gray-200/ dark:bg-slate-900/40"
);

/* handlers */
function onInput(e: Event) {
  const val = (e.target as HTMLInputElement)?.value ?? "";
  emit("update:modelValue", val);
  emit("input", e);
}
function onFocus(e: FocusEvent) { emit("focus", e); }
function onBlur(e: FocusEvent) { emit("blur", e); }
function onKeyup(e: KeyboardEvent) { if (e.key === "Enter") emit("enter", e); }

function onLeftIconClick() { emit("left-icon-click"); }
function onRightIconClick() {
  if (isPassword.value && props.togglePassword) {
    revealing.value = !revealing.value;
    return;
  }
  emit("right-icon-click");
}

onMounted(() => {
  if (props.autofocus) nextTick(() => inputRef.value?.focus());
});
</script>

<template>
  <div class="relative flex flex-col gap-1">
    <!-- label -->
    <label
      v-if="label"
      :for="uniqueId"
      class="mb-0.5 text-sm font-medium dark:text-gray-100"
    >
      {{ label }}
    </label>

    <!-- WRAPPER (igual ao seu exemplo) -->
    <div :class="containerClass">
      <!-- left icon -->
      <button
        v-if="hasLeftIcon"
        type="button"
        class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 hover:text-slate-600 dark:text-slate-300 dark:hover:text-slate-100 z-10"
        @click="onLeftIconClick"
        tabindex="-1"
      >
        <Icon :name="leftIcon" :size="sizeConf.icon" :customClass="'text-gray-600 dark:text-slate-100'+leftIconClass" />
      </button>

      <!-- INPUT NATIVO -->
      <input
        :id="uniqueId"
        :type="effectiveType"
        :placeholder="placeholder"
        :disabled="disabled"
        :min="['date','datetime-local','time'].includes(type) ? min : undefined"
        :value="modelValue as any"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
        @keyup="onKeyup"
        ref="inputRef"
        :class="[
          'w-full border-0 bg-transparent outline-none placeholder-slate-400',
          'text-gray-600 dark:text-slate-100',
          sizeConf.h, sizeConf.text,
          inputPadding,
          disabledSolid,
          props.rounded, // para manter raio quando sem borda
          inputClass,
        ]"
      />

      <!-- right icon / eye -->
      <button
        v-if="hasRightIcon"
        type="button"
        class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 dark:text-slate-300 dark:hover:text-slate-100 z-10"
        @click="onRightIconClick"
        tabindex="-1"
      >
        <Icon
          v-if="isPassword && togglePassword"
          :name="revealing ? 'visibility_off' : 'visibility'"
          :size="sizeConf.icon"
        />
        <Icon
          v-else
          :name="rightIcon"
          :size="sizeConf.icon"
          :customClass="rightIconClass"
        />
      </button>
    </div>

    <!-- help -->
    <p v-if="message" class="text-xs mt-1 truncate" :class="helpColor">
      {{ message }}
    </p>
  </div>
</template>

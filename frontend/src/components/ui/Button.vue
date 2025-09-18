<script setup lang="ts">
import { computed } from "vue";
import { FwbButton, FwbSpinner } from "flowbite-vue";

/**
 * Mantém a mesma API externa
 * variant: 'solid' | 'outline' | 'ghost' | 'link'
 * color:   'blue' | 'red' | 'green' | 'gray' | 'yellow' | 'purple'
 * size:    'xs' | 'sm' | 'md' | 'lg'
 */
const props = defineProps({
  label: { type: [String, Number], default: "" },
  variant: { type: String, default: "solid" },
  color: { type: String, default: "blue" },
  size: { type: String, default: "md" },
  block: { type: Boolean, default: true },
  isLoading: { type: Boolean, default: false },
  type: { type: String, default: "button" },
  disabled: { type: Boolean, default: false },
});

/** map de tamanho: Flowbite usa xs/sm/md/lg/xl */
const sizeMap: Record<string, "xs" | "sm" | "md" | "lg" | "xl"> = {
  xs: "xs",
  sm: "sm",
  md: "md",
  lg: "lg",
};

/** map de cor para o FwbButton */
const colorMap: Record<string, string> = {
  blue: "blue",
  red: "red",
  green: "green",
  gray: "alternative",
  yellow: "yellow",
  purple: "purple",
};

const fbColor = computed(() => colorMap[props.color] ?? "blue");
const fbSize = computed(() => sizeMap[props.size] ?? "md");

/** outline/ghost/link -> propriedades/estilos equivalentes */
const isOutline = computed(() => props.variant === "outline");
const isLink = computed(() => props.variant === "link");
const isGhost = computed(() => props.variant === "ghost");

const extraClasses = computed(() => {
  const blocks = props.block ? "w-full" : "";
  const ghost =
    isGhost.value
      ? "bg-transparent border-0 shadow-none hover:bg-gray-50 dark:hover:bg-gray-800/40"
      : "";
  const link =
    isLink.value
      ? "bg-transparent border-0 shadow-none underline underline-offset-2 px-0"
      : "";
  return [blocks, ghost, link].join(" ").trim();
});
</script>

<template>
  <FwbButton
    :type="type"
    :disabled="disabled || isLoading"
    :outline="isOutline && !isLink && !isGhost"
    :color="fbColor"
    :size="fbSize"
    :href="undefined"
    :class="extraClasses"
  >
    <template #default>
      <div class="inline-flex items-center justify-center gap-2">
        <FwbSpinner
          v-if="isLoading"
          color="white"
          size="6"
          class="!w-5 !h-5"
        />
        <slot>{{ label }}</slot>
      </div>
    </template>
  </FwbButton>
</template>

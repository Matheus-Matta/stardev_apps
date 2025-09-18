<script setup>
import { computed } from "vue";
import { useRoute, RouterLink } from "vue-router";

const props = defineProps({
  to: { type: [String, Object], required: true },
  label: { type: String, required: true },
  icon: { type: [Object, Function], default: null }, // componente ou template
  exact: { type: Boolean, default: false },
  badgeText: { type: [String, Number], default: null },
  badgeTone: { type: String, default: "gray" }, // gray | blue | green | red
});

const emit = defineEmits(["click"]);
const route = useRoute();

const isActive = computed(() => {
  const target = typeof props.to === "string" ? props.to : props.to?.path ?? "";
  if (props.exact) return route.path === target;
  return route.path === target || route.path.startsWith(`${target}/`);
});

const base =
  "flex items-center p-2 text-gray-900 rounded-lg dark:text-white transition duration-75";
const hover = "hover:bg-gray-100 dark:hover:bg-gray-700";
const active = "bg-gray-100 dark:bg-gray-700";

const iconBase =
  "w-5 h-5 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white";
</script>

<template>
  <RouterLink :to="to" class="group block" @click="$emit('click')">
    <div :class="[base, hover, isActive ? active : '']">
      <slot name="icon" />
      <span class="ms-3 flex-1 whitespace-nowrap">{{ label }}</span>

      <span
        v-if="badgeText != null"
        class="inline-flex items-center justify-center px-2 ms-3 text-xs font-medium rounded-full"
        :class="{
          'text-gray-800 bg-gray-100 dark:bg-gray-700 dark:text-gray-300': badgeTone === 'gray',
          'text-blue-800 bg-blue-100 dark:bg-blue-900 dark:text-blue-300': badgeTone === 'blue',
          'text-green-800 bg-green-100 dark:bg-green-900 dark:text-green-300': badgeTone === 'green',
          'text-red-800 bg-red-100 dark:bg-red-900 dark:text-red-300': badgeTone === 'red',
        }"
      >
        {{ badgeText }}
      </span>
    </div>
  </RouterLink>
</template>

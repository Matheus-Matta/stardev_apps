<script setup lang="ts">
import { computed } from "vue";

const props = defineProps({
  src: { type: String, default: "" },
  displayName: { type: String, default: "" },
  username: { type: String, default: "U" },
  size: { type: String, default: "8" },              // "8", "10", "12", "24", "28", "32"...
  bg: { type: String, default: "bg-indigo-500" },
  textClass: { type: String, default: "text-white" },
});

// Tailwind precisa enxergar classes literais:
const sizeClass = computed(() => {
  const map: Record<string, string> = {
    "6": "w-6 h-6",
    "8": "w-8 h-8",
    "10": "w-10 h-10",
    "12": "w-12 h-12",
    "16": "w-16 h-16",
    "20": "w-20 h-20",
    "24": "w-24 h-24",
    "28": "w-28 h-28",
    "32": "w-32 h-32",
    "36": "w-36 h-36",
    "40": "w-40 h-40",
  };
  return map[props.size] || "w-8 h-8";
});

/** iniciais como fallback */
const initials = computed(() => {
  const name = props.displayName?.trim() || props.username?.trim() || "U";
  const parts = name.split(" ").filter(Boolean);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
});

// style seguro para background-image
const bgStyle = computed(() => {
  if (!props.src) return {};
  // Aspas protegem URLs com espaços/parênteses; funciona com data: e http(s)
  return {
    backgroundImage: `url("${props.src}")`,
  };
});
</script>

<template>
  <div>
    <!-- com imagem -->
    <div
      v-if="src"
      :style="bgStyle"
      :class="[
        sizeClass,
        'rounded-full bg-cover bg-top bg-no-repeat',
        'min-w-[2rem] min-h-[2rem]'
      ]"
      role="img"
      aria-label="avatar"
    />

    <!-- fallback com iniciais -->
    <div
      v-else
      :class="[sizeClass, 'rounded-full grid place-items-center font-semibold', bg, textClass]"
    >
      {{ initials }}
    </div>
  </div>
</template>

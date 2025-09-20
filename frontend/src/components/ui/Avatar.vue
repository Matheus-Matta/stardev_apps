<script setup lang="ts">
import { computed } from "vue";

const props = defineProps({
  src: { type: String, default: "" },            // URL da imagem
  displayName: { type: String, default: "" },    // Nome completo para gerar iniciais
  username: { type: String, default: "U" },      // Fallback se não houver displayName
  size: { type: String, default: "8" },          // Tailwind: 8 = 2rem, 10 = 2.5rem
  bg: { type: String, default: "bg-indigo-500" },// cor de fundo fallback
  textClass: { type: String, default: "text-white" }, // cor do texto
});

/** gera iniciais (primeira letra de até 2 palavras do displayName) */
const initials = computed(() => {
  const name = props.displayName?.trim() || props.username?.trim() || "U";
  const parts = name.split(" ").filter(Boolean);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
});
</script>

<template>
  <div>
    <img
      v-if="src"
      :src="src"
      :class="`w-${size} h-${size} rounded-full object-cover`"
      alt="avatar"
    />
    <div
      v-else
      :class="`w-${size} h-${size} rounded-full ${bg} grid place-items-center ${textClass} font-semibold`"
    >
      {{ initials }}
    </div>
  </div>
</template>

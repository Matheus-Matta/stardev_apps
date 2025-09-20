<template>
  <button
    type="button"
    :aria-pressed="isDark ? 'true' : 'false'"
    :aria-label="isDark ? 'Alternar para modo claro' : 'Alternar para modo escuro'"
    @click="toggle"
    class="inline-flex items-center gap-2 px-3 py-2 rounded-full border
           text-gray-700 dark:text-gray-200
           border-gray-200 dark:border-gray-700
           bg-white dark:bg-gray-800
           hover:bg-gray-100 dark:hover:bg-gray-700
           focus:outline-none focus:ring-2 focus:ring-indigo-400"
  >
    <Icon :name="isDark ? 'light_mode' : 'dark_mode'" class="text-[18px]" />
    <span v-if="!compact" class="text-sm">
      {{ isDark ? 'Light' : 'Dark' }}
    </span>
  </button>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import Icon from "../ui/Icon.vue"; // ajuste o caminho se precisar

const props = defineProps({
  compact: { type: Boolean, default: false }, // true = mostra só o ícone
});

const isDark = ref(false);
let mql;

function applyTheme() {
  const root = document.documentElement;
  if (isDark.value) {
    root.classList.add("dark");
    localStorage.setItem("color-theme", "dark");
  } else {
    root.classList.remove("dark");
    localStorage.setItem("color-theme", "light");
  }
}

function readInitialTheme() {
  const hasLS = localStorage.getItem("color-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  isDark.value = hasLS ? localStorage.getItem("color-theme") === "dark" : prefersDark;
  applyTheme();
}

function toggle() {
  isDark.value = !isDark.value;
  applyTheme();
}

onMounted(() => {
  readInitialTheme();
  mql = window.matchMedia("(prefers-color-scheme: dark)");
  mql.addEventListener?.("change", (e) => {
    if (!localStorage.getItem("color-theme")) {
      isDark.value = e.matches;
      applyTheme();
    }
  });
});

onBeforeUnmount(() => {
  mql?.removeEventListener?.("change", () => {});
});
</script>

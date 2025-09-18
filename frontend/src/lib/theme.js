import { ref, watchEffect } from "vue";

export const isDark = ref(false);

export function toggleTheme() {
  isDark.value = !isDark.value;
  applyTheme();
}

export function applyTheme() {
  if (isDark.value) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

watchEffect(applyTheme);

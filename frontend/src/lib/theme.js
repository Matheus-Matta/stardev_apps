import { ref } from 'vue'

const isDark = ref(false)

function setDark(on) {
  isDark.value = on
  document.documentElement.classList.toggle('dark', on)
  localStorage.setItem('ui.theme', on ? 'dark' : 'light')
}

export function initTheme() {
  const saved = localStorage.getItem('ui.theme')
  const prefers = window.matchMedia('(prefers-color-scheme: dark)').matches
  setDark(saved ? saved === 'dark' : prefers)
}

export function toggleTheme() {
  setDark(!isDark.value)
}

export function useTheme() {
  return { isDark, toggleTheme, initTheme, setDark }
}

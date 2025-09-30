<script setup>
import { ref, watch } from 'vue'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { useToastStore } from '../store/toast'

const store = useToastStore()
const toast = useToast()
const renderedIds = ref(new Set())

watch(
  () => store.items.slice(),
  (list) => {
    for (const t of list) {
      if (renderedIds.value.has(t.id)) continue
      renderedIds.value.add(t.id)
      toast.add({
        group: 'app',
        severity: mapSeverity(t.type),
        summary: t.title || '',
        detail:  t.message || '',
        life:    t.duration ?? 3000,
        closable: true,
        data: { id: t.id, type: t.type }
      })
    }
  },
  { immediate: true }
)

function mapSeverity(type) {
  return type === 'error' ? 'error'
       : type === 'warn'  ? 'warn'
       : type === 'info'  ? 'info'
       : 'success'
}
function iconBySeverity(s) {
  return s === 'error' ? 'pi pi-times-circle'
       : s === 'warn'  ? 'pi pi-exclamation-triangle'
       : s === 'info'  ? 'pi pi-info-circle'
       : 'pi pi-check-circle'
}
function toneText(s) {
  return s === 'error' ? 'text-rose-600'
       : s === 'warn'  ? 'text-amber-600'
       : s === 'info'  ? 'text-sky-600'
       : 'text-emerald-600'
}
function boxClass(s) {
  return s === 'error'
    ? 'border-rose-200/70 dark:border-rose-800/60'
    : s === 'warn'
    ? 'border-amber-200/70 dark:border-amber-800/60'
    : s === 'info'
    ? 'border-sky-200/70 dark:border-sky-800/60'
    : 'border-emerald-200/70 dark:border-emerald-800/60'
}

</script>

<template>
  <Toast
    group="app"
    position="top-right"
    :pt="{
      root: 'pointer-events-none z-[1100]',      
      message: 'p-0 m-0 bg-transparent border-0', 
      messageContent: 'p-0 m-0 border-0',
      buttonContainer: 'hidden',
    }"
  >
    <template #message="{ message }">
      <div
        class="pointer-events-auto rounded-xl border shadow-lg bg-white/95 dark:bg-zinc-900/95
               px-3 py-2 my-1 sm:px-3 sm:py-2 flex items-center gap-3 w-[92vw] max-w-sm"
        :class="boxClass(message.severity)"
        role="status"
        aria-live="polite"
      >
        <i :class="[iconBySeverity(message.severity), 'mt-0.5 text-lg', toneText(message.severity)]" />

        <div class="min-w-0 flex-1">
          <div v-if="message.summary" class="text-[13px] font-semibold text-zinc-900 dark:text-zinc-100">
            {{ message.summary }}
          </div>
          <div class="text-sm text-zinc-700 dark:text-zinc-200 whitespace-pre-line break-words">
            {{ message.detail }}
          </div>
        </div>
      </div>
    </template>
  </Toast>
</template>

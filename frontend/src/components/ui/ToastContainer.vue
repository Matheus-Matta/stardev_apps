<template>
  <teleport to="body">
    <div class="fixed top-4 right-4 z-[9999] space-y-3" aria-live="polite" role="status">
      <transition-group name="toast-fade" tag="div">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="w-80 rounded-md border shadow-lg px-4 my-2 py-3 flex items-start gap-3
                 bg-white border-gray-200 text-gray-900
                 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100"
        >
          <div :class="iconWrapClass(t.type)">
            <Icon :name="iconName(t.type)" class="text-[18px]" />
          </div>

          <div class="flex-1 text-sm leading-5">
            <p class="pt-1">{{ t.message }}</p>
          </div>

          <button
            class="shrink-0 rounded cursor-pointer hover:text-red-400"
            @click="remove(t.id)"
            aria-label="Fechar"
          >
            <Icon name="close" />
          </button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup>
import { computed } from "vue";
import { useToastStore } from "../../store/toast";
import Icon from "./Icon.vue";

const store = useToastStore();
const toasts = computed(() => store.items);
const remove = (id) => store.remove(id);

const iconName = (type) => {
  if (type === "success") return "check_circle";
  if (type === "error")   return "error";
  return "info"; // info
};
const iconWrapClass = (type) => {
  if (type === "success") return "text-emerald-600 dark:text-emerald-400";
  if (type === "error")   return "text-red-600 dark:text-red-400";
  return "text-blue-600 dark:text-blue-400";
};
</script>

<style scoped>
.toast-fade-enter-active, .toast-fade-leave-active { transition: all .18s ease; }
.toast-fade-enter-from { opacity: 0; transform: translateY(-6px); }
.toast-fade-leave-to   { opacity: 0; transform: translateY(-6px); }
</style>

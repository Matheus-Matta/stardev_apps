<script setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";

const props = defineProps({
  label: { type: String, required: true },
  icon: { type: [Object, Function], default: null },
  items: {
    type: Array,
    required: true,
  },
  defaultOpen: { type: Boolean, default: false },
});
const emit = defineEmits(["item:click"]);

const open = ref(props.defaultOpen);
</script>

<template>
  <div>
    <button
      type="button"
      class="flex items-center w-full p-2 text-gray-900 rounded-lg transition duration-75 group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700"
      :aria-expanded="open ? 'true' : 'false'"
      @click="open = !open"
    >
      <component v-if="icon" :is="icon" class="shrink-0 w-5 h-5 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white" />
      <slot v-else name="icon" />
      <span class="flex-1 ms-3 text-left whitespace-nowrap">{{ label }}</span>

      <svg class="w-3 h-3 transition-transform duration-200" :class="open ? 'rotate-180' : ''" aria-hidden="true" fill="none" viewBox="0 0 10 6">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4" />
      </svg>
    </button>

    <transition name="fade" mode="out-in">
      <ul v-show="open" class="py-2 space-y-2 ms-2">
        <li v-for="(item, idx) in items" :key="idx">
          <RouterLink
            :to="item.to"
            class="flex items-center w-full p-2 text-gray-900 transition duration-75 rounded-lg pl-11 group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700"
            @click="$emit('item:click', item)"
          >
            <span class="flex-1 whitespace-nowrap">{{ item.label }}</span>
            <span
              v-if="item.badgeText != null"
              class="inline-flex items-center justify-center px-2 ms-3 text-xs font-medium rounded-full"
              :class="{
                'text-gray-800 bg-gray-100 dark:bg-gray-700 dark:text-gray-300': (item.badgeTone ?? 'gray') === 'gray',
                'text-blue-800 bg-blue-100 dark:bg-blue-900 dark:text-blue-300': item.badgeTone === 'blue',
                'text-green-800 bg-green-100 dark:bg-green-900 dark:text-green-300': item.badgeTone === 'green',
                'text-red-800 bg-red-100 dark:bg-red-900 dark:text-red-300': item.badgeTone === 'red',
              }"
            >
              {{ item.badgeText }}
            </span>
          </RouterLink>
        </li>
      </ul>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-2px); }
.fade-enter-active, .fade-leave-active { transition: all .15s ease; }
</style>

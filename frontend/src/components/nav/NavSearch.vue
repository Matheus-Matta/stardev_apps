<template>
  <!-- wrapper controla variações md:hidden / md:block externamente via classe -->
  <div class="relative" :class="wrapperClass">
    <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
      <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" viewBox="0 0 20 20" fill="none">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
      </svg>
      <span class="sr-only">Search icon</span>
    </div>
    <input
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      class="block w-full p-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg
             bg-gray-50 focus:ring-blue-500 focus:border-blue-500
             dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
             dark:focus:ring-blue-500 dark:focus:border-blue-500"
      type="text"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: "" },
  placeholder: { type: String, default: "Search..." },
  wrapperClass: { type: String, default: "" }, // ex: "hidden md:block" ou "mt-3 md:hidden"
});
defineEmits(["update:modelValue"]);
</script>

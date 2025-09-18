<template>
  <ul
    class="flex flex-col p-4 md:p-0 mt-4 font-medium border border-gray-100 rounded-lg bg-gray-50
           md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 md:bg-transparent
           dark:bg-gray-800 md:dark:bg-transparent dark:border-gray-700"
  >
    <li v-for="(item, i) in items" :key="i">
      <RouterLink
        :to="item.to"
        class="block py-2 px-3 rounded-sm md:p-0"
        :class="[
          item.active
            ? 'text-white bg-blue-700 md:bg-transparent md:text-blue-700 md:dark:text-blue-500'
            : 'text-gray-900 hover:bg-gray-100 md:hover:bg-transparent md:hover:text-blue-700 dark:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent',
        ]"
        aria-current="page"
      >
        {{ item.label }}
      </RouterLink>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [
      { label: "Home", to: "/", active: true },
      { label: "About", to: "/about" },
      { label: "Services", to: "/services" },
    ],
  },
});
</script>

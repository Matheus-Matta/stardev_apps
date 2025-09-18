<template>
  <RouterLink :to="to" class="flex items-center space-x-3 rtl:space-x-reverse">
    <img :src="logo" class="h-8" :alt="alt" />
    <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">
      {{ title }}
    </span>
  </RouterLink>
</template>

<script setup>
defineProps({
  to: { type: [String, Object], default: "/" },
  logo: { type: String, required: true },
  alt: { type: String, default: "Logo" },
  title: { type: String, required: true },
});
</script>

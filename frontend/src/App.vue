<template class="custom-scroll ">
  <router-view />
  <ToastContainer />
</template>

<script setup>
import { onMounted } from 'vue'

import { initTheme  } from "./lib/theme";
import ToastContainer from './components/ToastContainer.vue'
onMounted(() => {
  initTheme()
})
</script>


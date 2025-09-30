<template>
  <div
    class="max-w-[1280px] mx-auto container min-h-screen h-full"
    :style="{
      '--header-h': headerHeight,
      '--footer-h': footerHeight
    }"
  >
    <header class="fixed inset-x-0 top-0 z-50 h-[var(--header-h)]">
      <Navbar />
    </header>

    <main class="pt-[var(--header-h)]">
      <div class="grid grid-cols-[16rem_auto] gap-4 ">
        <AppSidebar/>
        <div class="w-full overflow-auto ">
          <slot />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import AppSidebar from '../components/Sidebar.vue'

const headerHeight = '68px'    
const footerHeight = '12px'     
const showFooter = false 
</script>

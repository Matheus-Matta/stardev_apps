<script setup>
import { ref } from "vue";
import Navbar from "../components/Navbar.vue";
import Sidebar from "../components/Sidebar.vue";

// sidebar control (mobile)
const isSidebarOpen = ref(false);
</script>
<template>

  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <Navbar @toggle-sidebar="isSidebarOpen = !isSidebarOpen" />
    <Sidebar :open="isSidebarOpen" @close="isSidebarOpen = false" />
    <main class="p-4 sm:ml-64">
      <div class="mt-16"></div>
      <div class="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="flex items-center justify-center h-24 rounded-sm bg-gray-50 dark:bg-gray-800">
            <p class="text-gray-500 dark:text-gray-400">Card</p>
          </div>
          <div class="flex items-center justify-center h-24 rounded-sm bg-gray-50 dark:bg-gray-800">
            <p class="text-gray-500 dark:text-gray-400">Card</p>
          </div>
          <div class="flex items-center justify-center h-24 rounded-sm bg-gray-50 dark:bg-gray-800">
            <p class="text-gray-500 dark:text-gray-400">Card</p>
          </div>
        </div>

        <div class="flex items-center justify-center h-48 mb-4 rounded-sm bg-gray-50 dark:bg-gray-800">
          <p class="text-gray-500 dark:text-gray-400">Wide block</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div class="flex items-center justify-center rounded-sm bg-gray-50 h-28 dark:bg-gray-800">
            <p class="text-gray-500 dark:text-gray-400">Box</p>
          </div>
          <div class="flex items-center justify-center rounded-sm bg-gray-50 h-28 dark:bg-gray-800">
            <p class="text-gray-500 dark:text-gray-400">Box</p>
          </div>
          <div class="flex items-center justify-center rounded-sm bg-gray-50 h-28 dark:bg-gray-800">
            <p class="text-gray-500 dark:text-gray-400">Box</p>
          </div>
          <div class="flex items-center justify-center rounded-sm bg-gray-50 h-28 dark:bg-gray-800">
            <p class="text-gray-500 dark:text-gray-400">Box</p>
          </div>
        </div>

        <div class="flex items-center justify-center h-48 mb-4 rounded-sm bg-gray-50 dark:bg-gray-800">
          <p class="text-gray-500 dark:text-gray-400">Wide block</p>
        </div>
      </div>
    </main>
  </div>
</template>



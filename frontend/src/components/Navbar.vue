<template>
  <nav class="fixed top-0 z-50 w-full bg-white border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700">
    <div class="px-3 py-3 lg:px-5 lg:pl-3">
      <div class="flex items-center justify-between">
        <!-- Left: burger + brand -->
        <div class="flex items-center justify-start rtl:justify-end gap-2">
          <!-- mobile: open sidebar -->
          <button
            type="button"
            @click="$emit('toggle-sidebar')"
            class="inline-flex items-center p-2 text-sm text-gray-500 rounded-lg sm:hidden hover:bg-gray-100 focus:outline-none
                   focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
          >
            <span class="sr-only">Open sidebar</span>
            <svg class="w-6 h-6" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" clip-rule="evenodd"
                d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z"/>
            </svg>
          </button>

          <NavBrand
            :to="brand.to"
            :logo="brand.logo"
            :title="brand.title"
            :alt="brand.alt"
          />
        </div>

        <!-- Right: search (desktop) + user + search button (mobile) -->
        <div class="flex items-center gap-2 md:gap-4">
          <!-- Search desktop (fixa à esquerda do perfil) -->
          <NavSearch
            v-model="search"
            placeholder="Search..."
            wrapper-class="hidden md:block min-w-[220px]"
          />

          <!-- Mobile: botão da busca -->
          <button
            type="button"
            class="md:hidden inline-flex items-center p-2 text-sm text-gray-500 rounded-lg hover:bg-gray-100
                   focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400
                   dark:hover:bg-gray-700 dark:focus:ring-gray-600"
            :aria-expanded="mobileSearchOpen ? 'true' : 'false'"
            :aria-controls="mobileSearchId"
            @click="mobileSearchOpen = !mobileSearchOpen"
          >
            <span class="sr-only">Open search</span>
            <svg class="w-5 h-5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
            </svg>
          </button>

          <!-- User menu -->
          <UserMenu :user="user" @logout="logout" />
        </div>
      </div>

      <!-- Mobile: campo de busca colapsável (abaixo do perfil) -->
      <div :id="mobileSearchId" class="md:hidden mt-2" v-show="mobileSearchOpen">
        <NavSearch v-model="search" placeholder="Search..." />
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import NavBrand from "./nav/NavBrand.vue";
import NavSearch from "./nav/NavSearch.vue";
import UserMenu from "./nav/UserMenu.vue";
import { useAuthStore } from "../store/auth";

defineEmits(["toggle-sidebar"]);

const router = useRouter();
const auth = useAuthStore();

const search = ref("");
const mobileSearchOpen = ref(false);
const mobileSearchId = "navbar-mobile-search";

const brand = {
  to: "/",
  logo: "https://flowbite.com/docs/images/logo.svg",
  alt: "Starchats",
  title: "Starchats",
};

const user = computed(() => auth.user || {});
async function logout() {
  await auth.logout();
  router.push("/login");
}
</script>


<script setup>
import { ref, computed } from "vue";
import  Icon  from "../ui/Icon.vue"
import ChangePasswordModal from "../modals/ChangePasswordModal.vue";

const props = defineProps({
  user: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["logout"]);

const open = ref(false);

const displayName = computed(() => props.user?.name || props.user?.username || "Usuário");
const email = computed(() => props.user?.email || "");
const avatarUrl = computed(() => props.user?.avatar || props.user?.avatar_url || "");

const initials = computed(() => {
  const n = (displayName.value || "").trim();
  return n ? n.split(" ").map(p => p[0]).slice(0, 2).join("").toUpperCase() : "U";
});

async function onChangePassword({ currentPassword, newPassword }) {
  cpOpen.value = false;
}
function close() { open.value = false; }
function onLogout() { close(); emit("logout"); }
</script>
<template>
  <div class="relative">
    <button
      type="button"
      @click="open = !open"
      class="flex text-sm bg-gray-800 rounded-full focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600"
    >
      <span class="sr-only">Abrir menu do usuário</span>
      <img v-if="avatarUrl" :src="avatarUrl" class="w-8 h-8 rounded-full" alt="user photo" />
      <div
        v-else
        class="w-8 h-8 rounded-full bg-indigo-500 grid place-items-center text-white text-xs font-semibold"
      >
        {{ initials }}
      </div>
    </button>

    <!-- dropdown -->
    <div
      v-show="open"
      class="absolute right-0 mt-3 z-50 my-4 w-56 text-base list-none bg-white divide-y divide-gray-100
             rounded-sm shadow-sm dark:bg-gray-700 dark:divide-gray-600"
    >
      <div class="px-4 py-3 flex items-center">
        <button
            type="button"
            class="flex text-sm bg-gray-800 rounded-full focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600"
        >
            <img v-if="avatarUrl" :src="avatarUrl" class="w-8 h-8 rounded-full" alt="user photo" />
            <div
                v-else
                class="w-8 h-8 rounded-full bg-indigo-500 grid place-items-center text-white text-xs font-semibold"
            >
            {{ initials }}
            </div>
        </button>
        <div class="pl-3">
            <p class="text-sm text-gray-900 dark:text-white">{{ displayName }}</p>
            <p class="text-sm font-medium text-gray-900 truncate dark:text-gray-300">{{ email }}</p>
        </div>
      </div>
      <ul class="py-1">
        <li>
          <RouterLink
            to="/"
            class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100
                   dark:text-gray-300 dark:hover:bg-gray-600 dark:hover:text-white"
            @click="close()"
          > <icon name="lock" class="mr-1" /> Alterar senha</RouterLink>
        </li>
        <li>
          <RouterLink
            to="/settings"
            class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100
                   dark:text-gray-300 dark:hover:bg-gray-600 dark:hover:text-white"
            @click="close()"
          ><icon name="settings" class="mr-1" />Configurações</RouterLink>
        </li>
        <li>
          <button
            class="w-full text-red-500 text-left flex items-center px-4 py-2 text-sm hover:bg-gray-100
                    dark:hover:bg-gray-600 cursor-pointer"
            @click="onLogout"
          ><icon name="logout" class="mr-1 text-red-500" />Sair</button>
        </li>
      </ul>
    </div>

    <!-- click outside -->
    <div v-show="open" class="fixed inset-0 z-40" @click="close()" />
  </div>
</template>

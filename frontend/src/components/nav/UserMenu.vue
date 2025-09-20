<script setup>
import { ref, computed, watch } from "vue";
import { storeToRefs } from "pinia";
import { useUserStore } from "../../store/user";
import Icon from "../ui/Icon.vue";
import Avatar from "../ui/Avatar.vue";
import ChangePasswordModal from "../modals/ChangePasswordModal.vue";

const emit = defineEmits(["logout"]);

const { user } = storeToRefs(useUserStore());

const open = ref(false);
const cpOpen = ref(false);

const displayNameRef = ref("Usuário");
const emailRef = ref("");
const avatarSrc = ref("");
const bust = ref(0);

// computed final para bust cache
const avatarSrcFinal = computed(() => {
  if (!avatarSrc.value) return "";
  const sep = avatarSrc.value.includes("?") ? "&" : "?";
  return `${avatarSrc.value}${bust.value ? `${sep}v=${bust.value}` : ""}`;
});

// função para atualizar refs com base no user
function applyUser(u) {
  displayNameRef.value = u?.name || u?.display_name || u?.username || "Usuário";
  emailRef.value = u?.email || "";
  const nextUrl = u?.avatar_url || "";
  const changed = nextUrl !== avatarSrc.value;
  avatarSrc.value = nextUrl;
  if (changed) bust.value = Date.now();
}

// já aplica os valores iniciais (se tiver)
applyUser(user.value);

// e continua reagindo às mudanças
watch(
  user,
  (u, old) => {
    applyUser(u);
    if (u !== old) open.value = false;
  },
  { deep: true }
);

function openChangePassword() {
  open.value = false;
  cpOpen.value = true;
}
function close() { open.value = false; }
function onLogout() { close(); emit("logout"); }
</script>

<template>
  <div class="relative">
    <!-- botão abre dropdown -->
    <button type="button" @click="open = !open"
      class="flex text-sm rounded-full focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600">
      <span class="sr-only">Abrir menu do usuário</span>
      <Avatar :src="avatarSrcFinal" :displayName="displayNameRef" />
    </button>

    <!-- dropdown -->
    <div v-show="open"
         class="absolute right-0 mt-3 z-50 my-4 w-56 text-base list-none bg-white divide-y divide-gray-100
                rounded-sm shadow-sm dark:bg-gray-700 dark:divide-gray-600">
      <div class="px-4 py-3 flex items-center">
        <Avatar :src="avatarSrcFinal" :displayName="displayNameRef" size="10" />
        <div class="pl-3">
          <p class="text-sm text-gray-900 dark:text-white">{{ displayNameRef }}</p>
          <p class="text-sm font-medium text-gray-900 truncate dark:text-gray-300">{{ emailRef }}</p>
        </div>
      </div>

      <ul class="py-1">
        <li>
          <button type="button"
            class="w-full flex items-center px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100
                   dark:text-gray-300 dark:hover:bg-gray-600 dark:hover:text-white"
            @click="openChangePassword">
            <Icon name="lock" class="mr-2" /> Alterar senha
          </button>
        </li>
        <li>
          <RouterLink to="/settings"
            class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100
                   dark:text-gray-300 dark:hover:bg-gray-600 dark:hover:text-white"
            @click="close()">
            <Icon name="settings" class="mr-2" /> Configurações
          </RouterLink>
        </li>
        <li>
          <button
            class="w-full text-red-500 text-left flex items-center px-4 py-2 text-sm hover:bg-gray-100
                   dark:hover:bg-gray-600 cursor-pointer"
            @click="onLogout">
            <Icon name="logout" class="mr-2 text-red-500" /> Sair
          </button>
        </li>
      </ul>
    </div>

    <div v-show="open" class="fixed inset-0 z-40" @click="close()" />
    <ChangePasswordModal :open="cpOpen" :user="user" @close="cpOpen = false" @submitted="cpOpen = false" />
  </div>
</template>

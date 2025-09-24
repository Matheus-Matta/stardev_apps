<!-- src/components/ProfileCard.vue -->
<script setup>
import { reactive, computed, ref, watch } from "vue";
import { FwbButton } from "flowbite-vue";
import Avatar from "../ui/Avatar.vue";
import Field from "../ui/Field.vue";
import Icon from "../ui/Icon.vue";
import EditActions from "../ui/EditActions.vue";

import { useUserStore } from "../../store/user";
import { useAuthStore } from "../../store/auth";

const userStore = useUserStore();
const auth = useAuthStore();

const props = defineProps({
  user: { type: Object, default: () => ({}) },
});

const fileInput = ref(null);
const pickedFile = ref(null);
const avatarPreview = ref("");

const currentUser = computed(
  () => (props.user && props.user.id ? props.user : auth.user) || {}
);

const original = ref({
  display_name: "",
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  bio: "",
  avatar: "",
  created_at: "",
  last_login: "",
});

const form = reactive({ ...original.value });

watch(
  currentUser,
  (val) => {
    if (!val) return;
    const base = {
      display_name: val.display_name || "",
      username: val.username || "",
      first_name: val.first_name || "",
      last_name: val.last_name || "",
      email: val.email || "",
      phone: val.phone || "",
      bio: val.bio || "",
      avatar: val.avatar_url || val.avatar || "",
      created_at: val.created_at || val.date_joined || "",
      last_login: val.last_login || "",
    };
    original.value = base;
    Object.assign(form, base);
    avatarPreview.value = base.avatar || "";
  },
  { immediate: true, deep: true }
);

function formatDate(value) {
  if (!value) return "Nunca";
  const d = new Date(value);
  if (isNaN(d.getTime())) return "—";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(d);
}
const createdAtFmt = computed(() => formatDate(original.value.created_at));
const lastLoginFmt = computed(() => formatDate(original.value.last_login));

const editingInfo = ref(false);
const savingInfo = ref(false);
const savingAvatar = ref(false);

function diffPayload(current, base) {
  const out = {};
  for (const k of Object.keys(current)) {
    if (current[k] !== base[k]) out[k] = current[k];
  }
  return out;
}

function startEditInfo() {
  Object.assign(form, original.value);
  editingInfo.value = true;
}
function cancelEditInfo() {
  Object.assign(form, original.value);
  editingInfo.value = false;
}

async function saveInfo() {
  const id = currentUser.value && currentUser.value.id;
  if (!id) return;

  const payload = diffPayload(form, original.value);
  if (!Object.keys(payload).length) {
    editingInfo.value = false;
    return;
  }

  try {
    savingInfo.value = true;
    const updated = await userStore.updateUser(id, payload);
    Object.assign(form, {
      display_name: updated.display_name ?? form.display_name,
      username: updated.username ?? form.username,
      first_name: updated.first_name ?? form.first_name,
      last_name: updated.last_name ?? form.last_name,
      email: updated.email ?? form.email,
      phone: updated.phone ?? form.phone,
      bio: updated.bio ?? form.bio,
      avatar: updated.avatar_url ?? "",
      created_at: updated.created_at ?? updated.date_joined ?? form.created_at,
      last_login: updated.last_login ?? form.last_login,
    });
    original.value = { ...form };
    editingInfo.value = false;
  } finally {
    savingInfo.value = false;
  }
}

function openAvatarPicker() {
  fileInput.value?.click?.();
}

async function onPickAvatar(e) {
  const file = e?.target?.files?.[0] || null;
  if (!file) return;

  const id = currentUser.value && currentUser.value.id;
  if (!id) return;

  const previous = form.avatar || "";
  pickedFile.value = file;
  const reader = new FileReader();
  reader.onload = () => {
    avatarPreview.value = String(reader.result);
  };
  reader.readAsDataURL(file);

  try {
    savingAvatar.value = true;
    const { user: updatedUser } = await userStore.uploadAndSetAvatar({
      userId: id,
      file,
    });
    const finalUrl =
      updatedUser?.avatar_url || updatedUser?.avatar || form.avatar;

    form.avatar = finalUrl;
    avatarPreview.value = finalUrl;
    original.value.avatar = finalUrl;
  } catch (err) {
    avatarPreview.value = previous;
  } finally {
    savingAvatar.value = false;
    pickedFile.value = null;
    if (fileInput.value) fileInput.value.value = "";
  }
}

const iconMap = {
  display_name: "badge",
  username: "account_circle",
  first_name: "person",
  last_name: "person",
  email: "email",
  phone: "phone",
  bio: "info",
};

const fields = [
  { key: "display_name", type: "text" },
  { key: "username", type: "text" },
  { key: "first_name", type: "text" },
  { key: "last_name", type: "text" },
  { key: "email", type: "email" },
  { key: "phone", type: "text" },
  { key: "bio", type: "text", colSpan: 2 },
];
</script>

<template>
  <div class="space-y-8">

    <div class="rounded-2xl border border-gray-200 bg-white/70 backdrop-blur-sm shadow-sm
                dark:border-gray-700 dark:bg-gray-800/60">
      <div class="h-20 rounded-t-2xl bg-gradient-to-r from-indigo-500 via-blue-500 to-cyan-500
                  dark:from-indigo-600 dark:via-blue-600 dark:to-cyan-600" />

      <div class="-mt-12 px-6 pb-6 pt-0">
        <div class="flex flex-col items-center text-center gap-4">
          <Avatar
            :src="avatarPreview || form.avatar"
            :displayName="form.display_name"
            :username="form.username"
            size="28"
          />

          <div class="space-y-1">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ form.display_name || form.username }}
            </h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              @{{ form.username }}
            </p>
          </div>

          <div class="flex items-center gap-3">
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="onPickAvatar"
            />
            <FwbButton
              size="sm"
              color="light"
              class="flex items-center cursor-pointer hover:dark:bg-gray-700 hover:bg-gray-200
                     rounded-xl px-4 py-2"
              @click="openAvatarPicker"
              :disabled="savingAvatar"
              :aria-busy="savingAvatar ? 'true' : 'false'"
            >
              <Icon name="photo" class="mr-2" size="16px" />
              <span>{{ savingAvatar ? 'Enviando...' : 'Alterar foto do perfil' }}</span>
            </FwbButton>
          </div>

          <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
            <div class="flex items-center gap-1">
              <Icon name="event" class="opacity-70" />
              <span>Criado recentemente</span>
            </div>
            <span class="opacity-40">•</span>
            <div class="flex items-center gap-1">
              <Icon name="bolt" class="opacity-70" />
              <span>Perfil atualizado ao salvar</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CARD: informações pessoais -->
    <div class="rounded-2xl border border-gray-200 bg-white/70 backdrop-blur-sm shadow-sm
                dark:border-gray-700 dark:bg-gray-800/60">
      <!-- título e ações -->
      <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-white">Informações pessoais</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Edite seus dados. Clique em <span class="font-medium">Salvar</span> para aplicar.
          </p>
        </div>

        <EditActions
          :editing="editingInfo"
          :saving="savingInfo"
          form="profile-form"            
          @edit="startEditInfo"
          @cancel="cancelEditInfo"
          @save=""                       
        />
      </div>

      <!-- formulário -->
      <form id="profile-form" class="px-6 py-5" @submit.prevent="saveInfo">
        <div class="space-y-6">
          <!-- bloco 1: identidade -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-3">
              Identidade
            </h4>
            <div class="grid gap-3 sm:grid-cols-2">
              <Field
                v-for="f in fields.slice(0, 2)"
                :key="f.key"
                :name="f.key"         
                :type="f.type"
                :editing="editingInfo"
                v-model="form[f.key]"
              />
            </div>
          </div>

          <!-- bloco 2: nome e contato -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-3">
              Nome & Contato
            </h4>
            <div class="grid gap-3 sm:grid-cols-2">
              <Field
                v-for="f in fields.slice(2, 6)"
                :key="f.key"
                :name="f.key"
                :type="f.type"
                :editing="editingInfo"
                v-model="form[f.key]"
              />
            </div>
          </div>

          <!-- bloco 3: bio -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-3">
              Sobre você
            </h4>
            <div class="grid gap-3">
              <Field
                v-for="f in fields.slice(6)"
                :key="f.key"
                :name="f.key"
                :type="f.type"
                :editing="editingInfo"
                v-model="form[f.key]"
                class="sm:col-span-2"
              />
            </div>
          </div>
        </div>

        <!-- barra de status / dica -->
        <div class="mt-6 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div class="flex items-center gap-2">
            <Icon name="info" class="opacity-70" />
            <span>Algumas alterações podem exigir atualização da sessão.</span>
          </div>
          <div v-if="savingInfo" class="animate-pulse">Salvando…</div>
        </div>
      </form>
    </div>

  </div>
</template>

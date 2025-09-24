<!-- src/components/tabs/TabAccount.vue -->
<script setup>
import { reactive, watch, onMounted, computed, ref } from "vue";
import Field from "../ui/Field.vue";
import Icon from "../ui/Icon.vue";
import EditActions from "../ui/EditActions.vue";
import { useAccountStore } from "../../store/account";
import { useUserStore } from "../../store/user";

const props = defineProps({
  accountId: { type: String, required: true },
});

const accountStore = useAccountStore();
const userStore = useUserStore();

const editing = ref(false);
const saving = ref(false);

const original = ref({
  display_name: "",
  legal_name: "",
  slug: "",
  time_zone: "",
});

const form = reactive({ ...original.value });

async function ensureAccount() {
  if (!props.accountId) return;
  const acc = await accountStore.ensure(props.accountId, { force: false });
  if (acc) {
    const base = {
      display_name: acc.display_name || "",
      legal_name: acc.legal_name || "",
      slug: acc.slug || "",
      time_zone: acc.time_zone || "",
    };
    original.value = base;
    Object.assign(form, base);
  }
}

onMounted(ensureAccount);

watch(
  () => accountStore.account,
  (acc) => {
    if (!acc) return;
    const base = {
      display_name: acc.display_name || "",
      legal_name: acc.legal_name || "",
      slug: acc.slug || "",
      time_zone: acc.time_zone || "",
    };
    original.value = base;
    Object.assign(form, base);
  },
  { deep: true }
);

function diffPayload(current, base) {
  const out = {};
  for (const k of Object.keys(current)) {
    if (current[k] !== base[k]) out[k] = current[k];
  }
  return out;
}

function startEdit() {
  Object.assign(form, original.value);
  editing.value = true;
}

function cancelEdit() {
  Object.assign(form, original.value);
  editing.value = false;
}

async function save() {
  const id = props.accountId;
  if (!id) return;
  const payload = diffPayload(form, original.value);
  if (!Object.keys(payload).length) {
    editing.value = false;
    return;
  }
  try {
    saving.value = true;
    await accountStore.updateById(id, payload);
    original.value = { ...form };
    editing.value = false;
  } finally {
    saving.value = false;
  }
}

const fields = [
  { key: "display_name", type: "text" },
  { key: "legal_name", type: "text" },
  { key: "slug", type: "text" },
];

const canEdit = computed(() => userStore.hasPermissions(["change_account"]));
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-base font-semibold text-gray-900 dark:text-white">Minha Conta</h2>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          Gerencie os dados da sua conta.
        </p>
      </div>

      <!-- ações reutilizáveis -->
      <EditActions
        :editing="editing"
        :saving="saving"
        form="account-form"
        :show-edit="canEdit"
        @edit="startEdit"
        @cancel="cancelEdit"
        @save=""   
      />
    </div>

    <!-- Formulário -->
    <form id="account-form" class="space-y-6" @submit.prevent="save">
      <div class="grid gap-3 sm:grid-cols-2">
        <Field
          v-for="f in fields"
          :key="f.key"
          :name="f.key"
          :type="f.type"
          :editing="editing && canEdit"
          v-model="form[f.key]"
          :class="f.colSpan === 2 ? 'sm:col-span-2' : ''"
        />
      </div>

      <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
        <span><Icon name="info" class="opacity-70" /> Alterações podem exigir atualização da sessão.</span>
        <span v-if="saving" class="animate-pulse">Salvando…</span>
      </div>
    </form>
  </div>
</template>

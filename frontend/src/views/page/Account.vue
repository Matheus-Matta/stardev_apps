<script setup>
import { reactive, ref, onMounted } from "vue";
import BaseView from "../../layout/BaseView.vue";
import SchemaForm from "../../components/forms/SchemaForm.vue";
import Button from "primevue/button";
import { accountSchema } from "../../schemas/update/account";
import { useAccountStore } from "../../store/auth/account";
import { useUserStore } from "../../store/auth/user";
import router from "../../router";

const userStore = useUserStore();
const accountStore = useAccountStore();

const model = reactive({
  id: null,
  slug: "",
  legal_name: "",
  display_name: "",
  email_principal: "",
  phone_principal: "",
  site_url: "",
  logo_url: ""
});

const schemaRef = ref(null);
const formKey = ref(0);     // força re-mount após hidratar
const loading = ref(false);
const isSubmitting = ref(false);
const error = ref(null);
const saved = ref(false);

// Copia somente as chaves existentes no schema
function assignFromSchemaKeys(schema, target, source) {
  if (!schema?.sections) return;
  for (const sec of schema.sections) {
    for (const row of (sec.rows || [])) {
      for (const f of (row.cols || [])) {
        const k = f.key;
        if (k in source && source[k] !== undefined) {
          target[k] = source[k] ?? "";
        }
      }
    }
  }
  if ("id" in source && source.id != null) target.id = source.id;
}

onMounted(async () => {
  const hasPermission = userStore.hasPermission('view_account');
  if(!hasPermission) router.push('/home');

  loading.value = true;
  try {
    accountStore.hydrate?.();
    const acc = await accountStore.fetch({ force: false }).catch(() => accountStore.account);
    if (acc) {
      assignFromSchemaKeys(accountSchema, model, acc);
      formKey.value++; // garante valores iniciais nos inputs/masks
    }
  } catch (e) {
    error.value = e?.message || "Falha ao carregar conta";
  } finally {
    loading.value = false;
  }
});

async function handleSubmit() {
  if (!schemaRef.value) return;
  isSubmitting.value = true;
  error.value = null;

  try {
    // valida todas as seções
    const ok = schemaRef.value.validateAll?.() ?? true;
    if (!ok) { isSubmitting.value = false; return; }

    // coleta payload achatado
    const payload = schemaRef.value.collectAllPayload?.() || {};
    await accountStore.update(payload); // seu store já usa o id interno
    saved.value = true;
    setTimeout(() => (saved.value = false), 1500);
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || "Falha ao salvar conta";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <BaseView>
    <div class="mx-auto flex">
      <div class="flex-1 min-w-0">
        <!-- Cabeçalho -->
        <div class="w-full flex justify-between items-center px-2 mb-2">
          <div class="flex my-4 mx-2 items-center gap-2">
            <i :class="(accountSchema.icon || 'pi pi-briefcase') + ' text-2xl text-zinc-700 dark:text-zinc-200'"></i>
            <h1 class="text-zinc-700 dark:text-zinc-200 font-semibold">
              {{ accountSchema.title || (model.id ? 'Editar Conta' : 'Configurações da Conta') }}
            </h1>
          </div>
          <div class="flex items-center gap-2">
            <Button
              :label="accountSchema.submitLabel || (model.id ? 'Salvar' : 'Criar')"
              severity="contrast"
              size="small"
              raised
              class="py-1 text-[12px]"
              :pt="{ icon: 'text-[12px]' }"
              :loading="isSubmitting"
              :disabled="isSubmitting"
              @click="handleSubmit"
            />
          </div>
        </div>

        <!-- Form -->
        <div class="h-[calc(93vh-var(--header-h)-var(--footer-h))] overflow-auto pr-2 scrollbar-thin-zinc">
          <div v-if="loading" class="px-2 text-sm text-zinc-500">Carregando...</div>

          <template v-else>
            <SchemaForm
              :key="formKey"
              ref="schemaRef"
              :schema="accountSchema"
              v-model="model"
              :loading="isSubmitting"
              mode="update"
            />
          </template>
        </div>
      </div>
    </div>
  </BaseView>
</template>

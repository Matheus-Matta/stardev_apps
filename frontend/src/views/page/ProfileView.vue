<script setup>
import { reactive, ref, onMounted } from "vue";
import BaseView from "../../layout/BaseView.vue";
import SchemaForm from "../../components/forms/SchemaForm.vue";
import Button from "primevue/button";
import { settingsSchema } from "../../schemas/update/user";
import { useUserStore } from "../../store/auth/user";

const userStore = useUserStore();

const model = reactive({
  id: null,
  username: "",
  email: "",
  first_name: "",
  last_name: "",
  display_name: "",
  phone: "",
  bio: "",
});

const schemaRef = ref(null);
const formKey = ref(0);     
const loading = ref(false);
const isSubmitting = ref(false);
const error = ref(null);
const saved = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    userStore.hydrate?.();
    const me = await userStore.fetch({ force: false }).catch(() => userStore.user);
    if (me) {
      Object.assign(model, me);   // mantém referência reativa
      formKey.value++;            // garante valores iniciais após hidratar
    }
  } catch (e) {
    error.value = e?.message || "Falha ao carregar usuário";
  } finally {
    loading.value = false;
  }
});

async function handleSubmit() {
  console.log("submit profile");
  if (!schemaRef.value) return;
  isSubmitting.value = true;
  error.value = null;

  try {
    const ok = schemaRef.value.validateAll?.() ?? true;
    if (!ok) { isSubmitting.value = false; return; }

    const payload = schemaRef.value.collectAllPayload?.() || {};
    await userStore.update(payload);
    saved.value = true;
    setTimeout(() => (saved.value = false), 1500);
  } catch (e) {
    error.value = e?.message || "Falha ao salvar perfil";
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
            <i :class="(settingsSchema.icon || 'pi pi-user') + ' text-2xl text-zinc-700 dark:text-zinc-200'"></i>
            <h1 class="text-zinc-700 dark:text-zinc-200 font-semibold">
              {{ settingsSchema.title || 'Minha Conta' }}
            </h1>
          </div>
          <div class="flex items-center gap-2">
            <Button
              :label="settingsSchema.submitLabel || 'Salvar'"
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
              :schema="settingsSchema"
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

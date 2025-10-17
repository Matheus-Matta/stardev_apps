<script setup>
import { reactive, ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";
import ConfirmAction from '../../components/dialog/ConfirmAction.vue';
import BaseView from "../../layout/BaseView.vue";
import SchemaForm from "../../components/forms/SchemaForm.vue";
import SectionRail from "../../components/SectionRail.vue";
import { useStore } from "../../store/index";
import { getCreateSchema } from "../../schemas/forms";
import { useFormModel } from "../../composables/form/useFormModel";
import { keyFromSection } from "../../composables/form/formHelpers";
import { useUserStore } from "../../store/auth/user";

const route = useRoute();
const router = useRouter();

const modelName = computed(() => (route.params.model || "").toString());
const recordId  = computed(() => route.params.id);
const mode      = computed(() => (recordId.value ? "update" : "create"));
const isCreateMode = computed(() => mode.value === "create");
const isUpdateMode = computed(() => mode.value === "update");

function resolveSchema(name) {
  const s = getCreateSchema?.(name);
  if (!s) throw new Error(`Schema não encontrado para '${name}'.`);
  return s;
}
const userStore = useUserStore();
const schema = computed(() => resolveSchema(modelName.value));

const permBase = computed(() => schema.value?.id || modelName.value);

const canView   = computed(() => userStore.hasPermission?.(`view_${permBase.value}`));
const canCreate = computed(() => userStore.hasPermission?.(`add_${permBase.value}`));
const canChange = computed(() => userStore.hasPermission?.(`change_${permBase.value}`));
const canDelete = computed(() => userStore.hasPermission?.(`delete_${permBase.value}`));

const formKey = computed(() => `${modelName.value}:${recordId.value || 'new'}`);

const pageTitle = computed(() => {
  if (isUpdateMode.value) {
    return schema.value?.editTitle ||
           schema.value?.title?.replace(/^Criar\b/i, "Editar") ||
           "Editar";
  }
  return schema.value?.title || "Criar";
});

const submitLabel = computed(() => {
  if (isUpdateMode.value) {
    return schema.value?.editSubmitLabel || "Salvar";
  }
  return schema.value?.submitLabel || "Criar";
});

const model = reactive({});
const loading = ref(false);
const isSubmitting = ref(false);
const error = ref(null);
const formRef = ref(null);
const confirmActionRef = ref(null)

const sectionItems = computed(() =>
  (schema.value?.sections || []).map((sec, idx) => ({
    id: `sec-${idx}`,
    title: sec.title || `Seção ${idx + 1}`,
  }))
);

const activeSectionId = ref(null);
let intersectionObserver;

function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setupIntersectionObserver() {
  cleanupObserver();
  const opts = { root: null, rootMargin: "0px 0px -60% 0px", threshold: 0 };
  intersectionObserver = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((e) => e.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (visible?.target?.id) activeSectionId.value = visible.target.id;
  }, opts);
  sectionItems.value.forEach((s) => {
    const el = document.getElementById(s.id);
    if (el) intersectionObserver.observe(el);
  });
}

function cleanupObserver() {
  if (intersectionObserver) {
    intersectionObserver.disconnect();
    intersectionObserver = null;
  }
}
function clearModel() {
  Object.keys(model).forEach((k) => delete model[k]);
}

async function loadRecordForUpdate() {
  const storeName = schema.value?.store;
  const id = recordId.value;
  if (!storeName || !id) throw new Error("Store ou ID não definidos.");

  const api = useStore(storeName);
  const tryMethods = ["getById", "fetchById", "get"];
  let record = null;
  for (const method of tryMethods) {
    if (typeof api?.[method] === "function") {
      record = await api[method](id, { force: true }).catch(() => null);
      if (record) break;
    }
  }
  if (!record) throw new Error("Registro não encontrado.");

  const { hydrateFromRecord } = useFormModel();
  hydrateFromRecord(
    schema.value?.sections || [],
    record,
    model,
    (sec, i) => keyFromSection(sec, i)
  );
}

async function handleSubmit() {
  if (isUpdateMode.value && !canChange.value) return;

  const isValid = formRef.value?.validateAll?.();
  if (!isValid) {
    error.value = "Preencha os campos obrigatórios.";
    return;
  }

  const storeName = schema.value?.store;
  if (!storeName) {
    error.value = "Store não definido no schema.";
    return;
  }

  isSubmitting.value = true;
  error.value = null;

  try {
    const api = useStore(storeName);
    const payload =
      formRef.value?.collectGroupedPayload?.() ??
      formRef.value?.collectAllPayload?.() ??
      {};

    if (isCreateMode.value) {
      await api.create(payload);
      router.push(`/${storeName}/list`);
    } else {
      const id = recordId.value;
      if (!id) throw new Error("ID ausente para update.");
      await api.update(id, payload);
    }
  } catch (e) {
    console.error(`[${mode.value.toUpperCase()} ERROR]`, e);
    error.value = e?.message || "Falha ao salvar";
  } finally {
    isSubmitting.value = false;
  }
}

async function handleDelete() {
  if (!isUpdateMode.value || !canDelete.value) return

  const ok = await confirmActionRef.value?.ask({
    title: `Excluir ${schema.value?.title}`,
    description: 'Esta ação não pode ser desfeita. Deseja continuar?',
    mode: 'delete',
  })

  if (!ok) return

  const storeName = schema.value?.store
  const id = recordId.value
  if (!storeName || !id) return

  try {
    const api = useStore(storeName)
    const tryMethods = ['delete', 'remove', 'destroy']
    let done = false
    for (const m of tryMethods) {
      if (typeof api?.[m] === 'function') {
        await api[m](id)
        done = true
        break
      }
    }
    if (!done) throw new Error('Store não possui método de remoção compatível.')
    router.push(`/${storeName}/list`)
  } catch (e) {
    error.value = e?.message || 'Falha ao remover'
  }
}

async function initialize() {
  loading.value = true;
  error.value = null;

  if (!canView.value) {
    router.push("/home");
    loading.value = false;
    return;
  }
  if (isCreateMode.value && !canCreate.value) {
    router.push("/home");
    loading.value = false;
    return;
  }

  try {
    clearModel();
    if (isUpdateMode.value) await loadRecordForUpdate();
    await nextTick();
    setupIntersectionObserver();
  } catch (e) {
    console.error("[FORM INIT ERROR]", e);
    error.value = e?.message || "Falha ao carregar";
  } finally {
    loading.value = false;
  }
  await nextTick();
  formRef.value?.snapshotAll?.();
  console.log('model', model);
}


onMounted(initialize);
watch([modelName, recordId], async () => {
  cleanupObserver();
  await initialize();
});
onBeforeUnmount(cleanupObserver);
</script>

<template>
  <BaseView>
    <div class="mx-auto flex">
      <!-- Main Content -->
      <div class="flex-1 min-w-0">
        <!-- Header -->
        <div class="w-full flex justify-between items-center px-2 mb-2">
          <div class="flex my-4 mx-2 items-center gap-2">
            <i :class="[(schema.icon || 'pi pi-cog'),'text-2xl text-zinc-700 dark:text-zinc-200']"></i>
            <h1 class="text-zinc-700 dark:text-zinc-200 font-semibold">{{ pageTitle }}</h1>
          </div>

          <div class="flex items-center gap-2">
            <Button
              :label="submitLabel"
              severity="contrast"
              size="small"
              raised
              class="py-1 text-[12px]"
              :pt="{ icon: 'text-[12px]' }"
              :loading="isSubmitting"
              :disabled="isSubmitting || loading || (isUpdateMode && !canChange)"
              @click="handleSubmit"
            />
            <Button
                v-if="isUpdateMode && canDelete"
                severity="danger"
                icon="pi pi-trash"
                size="small"
                raised
                variant="text"
                class="py-1 text-[12px] bg-red-500 text-white hover:bg-red-600 border-red-500 hover:border-red-600"
                :disabled="isSubmitting || loading"
                @click="handleDelete"
                />
          </div>
        </div>

        <!-- Form -->
        <div class="h-[calc(93vh-var(--header-h)-var(--footer-h))] overflow-auto pr-2 scrollbar-thin-zinc">
          <SchemaForm
            v-if="!loading"
            :key="formKey"
            ref="formRef"
            :schema="schema"
            v-model="model"
            :loading="loading || isSubmitting"
            :mode="mode"
            :perm-base="permBase"  
          />
        </div>
      </div>

      <!-- Section Rail -->
      <SectionRail
        title="Seções"
        :items="sectionItems"
        :active-id="activeSectionId"
        @navigate="scrollToSection"
      />
    </div>
    <ConfirmAction ref="confirmActionRef" />
  </BaseView>
</template>

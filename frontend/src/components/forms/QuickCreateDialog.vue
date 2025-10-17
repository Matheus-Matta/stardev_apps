<!-- src/components/forms/QuickCreateDialog.vue -->
<script setup>
import { ref, computed, reactive, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import SchemaSection from "./SchemaSection.vue";
import { getCreateSchema } from "../../schemas/forms";
import { useStore } from "../../store/index";

const props = defineProps({
  modelname: { type: String, required: true },
  visible:   { type: Boolean, default: false },

  /** opcional: pré-preencher campos do formulário */
  prefill:   { type: Object, default: () => ({}) },

  /** opcional: usar outra seção do schema (default 0 = primeira) */
  sectionIndex: { type: Number, default: 0 },

  /** opcional: forçar o store usado no create */
  store: { type: String, default: "" },

  /** opcional: título customizado */
  title: { type: String, default: "" },

  /** opcional: mapear o item criado para option {label,value} do Select */
  optionMapper: {
    type: Function,
    default: (item) => ({
      label: item?.name ?? item?.code ?? String(item?.id ?? ""),
      value: item?.id,
    }),
  },
});

const emit = defineEmits(["update:visible", "created", "error"]);

const router = useRouter();
const sectionRef = ref(null);
const formData = reactive({});
const isSubmitting = ref(false);

/** schema completo do create */
const schemaRef = computed(() => getCreateSchema(props.modelname) || {});

/** “recorte” de schema para quick-create (uma única seção) */
const quickSchema = computed(() => {
  const base = schemaRef.value || {};
  const sections = Array.isArray(base.sections) ? base.sections : [];
  const sec = sections[props.sectionIndex] || sections[0];
  return {
    ...base,
    sections: sec ? [sec] : [],
    submitLabel: "Criar",
  };
});

const firstSection = computed(() => quickSchema.value.sections?.[0]);
const dialogTitle = computed(() =>
  props.title || quickSchema.value?.title || "Criar Registro"
);

/** inicializa/limpa form */
function clearForm() {
  Object.keys(formData).forEach((k) => delete formData[k]);
}

function applyPrefill() {
  if (!props.prefill) return;
  Object.entries(props.prefill).forEach(([k, v]) => (formData[k] = v));
}

/** abrir/fechar dialog */
function handleClose() {
  emit("update:visible", false);
  nextTick(() => clearForm());
}

watch(
  () => props.visible,
  async (v) => {
    if (v) {
      // (re)monta form para cada abertura
      clearForm();
      applyPrefill();
      await nextTick(); // garante SchemaSection montado antes de defaults
    }
  }
);

/** submit rápido */
async function handleQuickSubmit() {
  const isValid = sectionRef.value?.validate?.() ?? true;

  if (!isValid) {
    emit("error", { message: "Preencha os campos obrigatórios." });
    return;
  }

  // SchemaSection.collectPayload já normaliza e ignora campos em branco (na sua versão atual)
  const payload = sectionRef.value?.collectPayload?.() ?? {};

  // Descobre o store: prioridade props.store > seção > schema > modelname
  const storeName =
    props.store ||
    firstSection.value?.store ||
    quickSchema.value?.store ||
    props.modelname;

  if (!storeName) {
    emit("error", { message: "Store não definido." });
    return;
  }

  isSubmitting.value = true;

  try {
    const apiStore = useStore(storeName);
    const createdItem = await apiStore.create(payload);

    // Mapeia o item criado para option { label, value } do Select
    const option = props.optionMapper(createdItem);

    emit("created", { item: createdItem, option, payload });
    emit("update:visible", false);
    clearForm();
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || "Falha ao criar item";
    emit("error", { message: msg, raw: e });
  } finally {
    isSubmitting.value = false;
  }
}

function goToFullCreate() {
  router.push(`/${props.modelname}/create`);
  emit("update:visible", false);
  clearForm();
}
</script>

<template>
  <Dialog
    v-model:visible="(/* two-way */ $props.visible)"
    :header="dialogTitle"
    modal
    :closable="true"
    :close-on-escape="true"
    :style="{ width: '48rem' }"
    class="p-fluid"
    @update:visible="val => (!val && handleClose())"
  >
    <SchemaSection
      v-if="firstSection"
      ref="sectionRef"
      :section="firstSection"
      :modelValue="formData"
      :loading="isSubmitting"
      mode="create"
      @update:modelValue="(val) => Object.assign(formData, val)"
    />

    <div v-else class="text-sm text-zinc-500 text-center py-4">
      Nenhuma seção disponível para criação rápida.
    </div>

    <template #footer>
      <div class="flex justify-between gap-2 w-full">
        <Button
          label="Edição Completa"
          severity="secondary"
          size="small"
          iconPos="right"
          raised
          variant="text"
          icon="pi pi-external-link"
          class="py-1.5 text-[12px]"
          :pt="{ icon: 'text-[12px]' }"
          @click="goToFullCreate"
          :disabled="isSubmitting"
        />
        <Button
          :label="quickSchema?.submitLabel || 'Criar'"
          severity="contrast"
          raised
          class="py-1.5 text-[12px]"
          :pt="{ icon: 'text-[12px]' }"
          size="small"
          :loading="isSubmitting"
          @click="handleQuickSubmit"
          :disabled="!firstSection || isSubmitting"
        />
      </div>
    </template>
  </Dialog>
</template>

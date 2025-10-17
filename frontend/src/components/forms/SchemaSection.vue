<script setup>
import { onMounted, watch, nextTick, reactive } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../../store/auth/user";
import { rowClass } from "../../composables/form/formHelpers";
import { useFormModel } from "../../composables/form/useFormModel";
import { useFormValidation } from "../../composables/form/useFormValidation";
import { useSelectOptions } from "../../composables/form/useSelectOptions";

import FieldText from "./fields/FieldText.vue";
import FieldMask from "./fields/FieldMask.vue";
import FieldSelect from "./fields/FieldSelect.vue";
import FieldToggle from "./fields/FieldToggle.vue";
import FieldRelationTable from "./fields/FieldRelationTable.vue";

const props = defineProps({
  section: { type: Object, required: true },
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  mode: {
    type: String,
    default: "create",
    validator: (v) => ["create", "update"].includes(v),
  },
  permBase: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue"]);

const router = useRouter();
const userStore = useUserStore();

const { normalizeForField, normalizeForSave, normalizeOnInput, applyDefaults } =
  useFormModel();

const isEmpty = (v) =>
  v === undefined || v === null || (typeof v === "string" && v.trim() === "");

const initial = reactive({});
const toNullIfBlank = (v) => (v === "" ? null : v);
const shallowEq = (a, b) => {
  if (a === b || (a == null && b == null)) return true;
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    const idOf = (x) =>
      x && typeof x === "object" ? x.id ?? x.value ?? x.pk ?? x : x;
    const A = a.map(idOf);
    const B = b.map(idOf);
    return A.every((v, i) => String(v) === String(B[i]));
  }
  return false;
};

function snapshotInitial() {
  Object.keys(initial).forEach((k) => delete initial[k]);
  props.section?.rows?.forEach((row) =>
    row.cols?.forEach((field) => {
      const raw = props.modelValue[field.key];
      let val;
      if (field.type === "relation") {
        const idOf = (x) =>
          x && typeof x === "object" ? x.id ?? x.value ?? x.pk ?? x : x;
        val = Array.isArray(raw) ? raw.map(idOf) : [];
      } else {
        val = toNullIfBlank(normalizeForSave(field, raw));
      }
      initial[field.key] = val;
    })
  );
}

if (props.mode === "create") {
  applyDefaults(props.section, props.modelValue, { treatEmptyAsUnset: true });
  emit("update:modelValue", { ...props.modelValue });
}

watch(
  () => [props.mode, props.section],
  () => {
    if (props.mode === "create") {
      applyDefaults(props.section, props.modelValue, {
        treatEmptyAsUnset: true,
      });
      emit("update:modelValue", { ...props.modelValue });
    }
    nextTick(() => snapshotInitial());
  }
);

const validation = useFormValidation();
const selectOpts = useSelectOptions(props.modelValue);

function sectionEditable() {
  const baseOK = props.permBase
    ? userStore.hasPermission?.(`change_${props.permBase}`)
    : true;
  const specific = props.section?.permission
    ? userStore.hasPermission?.(props.section.permission)
    : true;
  return !!(baseOK && specific);
}

function getFieldValue(field) {
  const current = props.modelValue[field.key];
  const when = field.defaultWhen || "create";
  let base;
  if (!isEmpty(current)) {
    base = current;
  } else {
    const def = field.defaultValue ?? field.default;
    base =
      when === "always"
        ? def
        : when === "create" && props.mode === "create"
        ? def
        : current;
  }
  if (field.type === "relation") {
    return Array.isArray(base) ? base : [];
  }
  return normalizeForField(field, base);
}

function setFieldValue(key, value, field) {
  let next = normalizeOnInput(field, value);
  if (["checkbox", "toggle"].includes(field?.type)) next = !!value;
  if (field?.type === "select") next = normalizeForField(field, value);
  if (field?.type === "relation") next = Array.isArray(value) ? value : [];
  props.modelValue[key] = next;
  emit("update:modelValue", props.modelValue);
  validation.touch(key);
}

function handleBlur(field) {
  validation.touch(field.key);
}

function handleSelectAdd(field) {
  const storeName = field.store || field.optionsStore;
  if (!storeName) return;
  router.push(`/${storeName}/create`);
}

function collectPayload() {
  const payload = {};
  props.section?.rows?.forEach((row) =>
    row.cols?.forEach((field) => {
      const raw = props.modelValue[field.key];
      let curr;
      if (field.type === "relation") {
        if (typeof field.serialize === "function") {
          curr = field.serialize(raw);
        } else {
          const idOf = (x) =>
            x && typeof x === "object" ? x.id ?? x.value ?? x.pk ?? x : x;
          curr = Array.isArray(raw) ? raw.map(idOf) : [];
        }
      } else {
        curr = toNullIfBlank(normalizeForSave(field, raw));
      }
      const prev = initial[field.key];
      if (shallowEq(prev, curr)) return;
      if (curr === null && field?.sendWhenCleared === false) return;
      payload[field.key] = curr;
    })
  );
  return payload;
}

function validate() {
  return validation.validateSection(props.section, props.modelValue);
}

onMounted(() => {
  props.section?.rows?.forEach((row) =>
    row.cols?.forEach((field) => {
      if (field.type === "select") selectOpts.setupField(field);
    })
  );
  snapshotInitial();
});

defineExpose({ validate, collectPayload, snapshotInitial });
</script>

<template>
  <div class="space-y-4">
    <div v-for="(row, ri) in section.rows" :key="ri" :class="rowClass(row)">
      <div v-for="field in row.cols" :key="field.key">
        <!-- Mask Field -->
        <FieldMask
          v-if="field.type === 'mask' && field.mask"
          :label="field.label"
          :modelValue="getFieldValue(field)"
          :mask="field.mask"
          :placeholder="field.placeholder"
          :disabled="!sectionEditable()"
          :iconLeft="field.iconLeft"
          :iconRight="field.iconRight"
          :addonLeft="field.addonLeft"
          :addonRight="field.addonRight"
          :pt="{ root: { class: 'w-full' }, input: { class: 'w-full' } }"
          @update:modelValue="(val) => setFieldValue(field.key, val, field)"
          @blur="handleBlur(field)"
        />

        <!-- Select Field -->
        <FieldSelect
          v-else-if="field.type === 'select'"
          :label="field.label"
          :modelValue="getFieldValue(field)"
          :options="selectOpts.options[field.key] || []"
          :loading="!!selectOpts.loading[field.key]"
          :placeholder="selectOpts.loading[field.key] ? 'Carregando...' : field.placeholder || 'Selecione...'"
          :disabled="!sectionEditable()"
          :iconLeft="field.iconLeft"
          :iconRight="field.iconRight"
          :addonLeft="field.addonLeft"
          :addonRight="field.addonRight"
          :showAdd="!!(field.store && userStore.hasPermission?.(`add_${field.store}`))"
          addLabel="Adicionar"
          addIcon="pi pi-plus"
          @update:modelValue="(val) => setFieldValue(field.key, val, field)"
          @show="() => selectOpts.handleShow(field)"
          @focus="() => selectOpts.handleFocus(field)"
          @blur="handleBlur(field)"
          @add="() => handleSelectAdd(field)"
          @search="(e) => selectOpts.handleSearch(field, e)"
        />

        <!-- Relation Field -->
        <FieldRelationTable
          v-else-if="field.type === 'relation'"
          :label="field.label"
          :modelValue="getFieldValue(field)"
          :columns="field.columns || []"
          :rows="field.rows"
          :disabled="!sectionEditable()"
          :pkField="field.pk || 'id'"
          :displayField="field.display || 'name'"
          :showAdd="field.showAdd !== false"
          :showEdit="field.showEdit === true"
          :createRoute="field.createRoute || ''"
          :perm-base="permBase"
          :context-id="modelValue?.id"
          :relation-perm-base="(field.schema || field.store || permBase)"
          @update:modelValue="(val) => setFieldValue(field.key, val, field)"
          @reload="field.onReload?.()"
        />

        <!-- Toggle Field -->
        <FieldToggle
          v-else-if="['checkbox', 'toggle'].includes(field.type)"
          :label="field.label"
          :modelValue="getFieldValue(field)"
          :disabled="!sectionEditable()"
          @update:modelValue="(val) => setFieldValue(field.key, val, field)"
        />

        <!-- Text Field -->
        <FieldText
          v-else
          :label="field.label"
          :modelValue="getFieldValue(field)"
          :placeholder="field.placeholder"
          :disabled="!sectionEditable()"
          :iconLeft="field.iconLeft"
          :iconRight="field.iconRight"
          :addonLeft="field.addonLeft"
          :addonRight="field.addonRight"
          :inputProps="field.props"
          :keyfilter="field.directives?.keyfilter"
          @update:modelValue="(val) => setFieldValue(field.key, val, field)"
          @blur="handleBlur(field)"
        />

        <p v-if="validation.shouldShowError(field, modelValue)" class="mt-2 pl-1 text-red-400 text-sm">
          {{ validation.getFieldErrorText(field, modelValue) }}
        </p>
      </div>
    </div>
  </div>
</template>


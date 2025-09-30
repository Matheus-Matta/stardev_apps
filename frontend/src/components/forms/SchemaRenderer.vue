<!-- src/components/forms/SchemaRenderer.vue -->
<script setup>
import { reactive, ref } from "vue";

import InputText from "primevue/inputtext";
import InputMask from "primevue/inputmask";
import InputGroup from "primevue/inputgroup";
import InputGroupAddon from "primevue/inputgroupaddon";
import Button from "primevue/button";

import { useStore } from "../../store/index";
import { useUserStore } from "../../store/user";

const userStore = useUserStore();

const props = defineProps({
  schema: { type: Object, required: true },
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  submitLabel: { type: String, default: "Salvar" },
  method: { type: String, default: null },
  ids: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["update:modelValue", "submit", "success", "error"]);

const state = reactive({ touched: {} });
const localLoading = ref(false);

// helpers UI
function hasGroup(field) {
  return !!(
    field.iconLeft ||
    field.iconRight ||
    field.addonLeft ||
    field.addonRight
  );
}

function setModel(k, v, field) {
  const next = field?.normalizeOnInput ? field.normalizeOnInput(v) : v;
  props.modelValue[k] = next;
  emit("update:modelValue", props.modelValue);
  state.touched[k] = true;
}

function normalizeForSave(field, v) {
  return field?.normalizeOnSave ? field.normalizeOnSave(v) : v;
}

function isValid(field) {
  const v = props.modelValue[field.key];
  return typeof field.validate === "function" ? !!field.validate(v) : true;
}

function errText(field) {
  return isValid(field) ? "" : field.error || "Valor inválido.";
}

function toPrimeMask(mask) {
  if (Array.isArray(mask)) return mask.map((m) => m.replace(/\[9\]/g, "?9"));
  return mask ? mask.replace(/\[9\]/g, "?9") : null;
}

const GRID_COLS = {
  1: "grid-cols-1",
  2: "grid-cols-2",
  3: "grid-cols-3",
  4: "grid-cols-4",
  5: "grid-cols-5",
  6: "grid-cols-6",
};

function rowClass(row) {
  const per = Math.max(
    1,
    Math.min(6, row?.colsPer || (row?.cols?.length ?? 1))
  );
  const colsClass = GRID_COLS[per] || GRID_COLS[1];
  return `grid ${colsClass} gap-3 w-full`;
}

function sectionEditable(section) {
  const perm = section?.permission;
  return perm ? userStore.hasPermission(perm) : true;
}

function allSectionsDisabled() {
  const sections = props.schema.sections || [];
  if (!sections.length) return true;
  return sections.every((sec) => !sectionEditable(sec));
}

// --- payloads ---
function collectAllPayload() {
  const payload = {};
  props.schema.sections?.forEach((sec) =>
    sec.rows?.forEach((row) =>
      row.cols?.forEach((field) => {
        payload[field.key] = normalizeForSave(
          field,
          props.modelValue[field.key]
        );
      })
    )
  );
  return payload;
}

function collectPerSectionPayload(section) {
  const payload = {};
  section?.rows?.forEach((row) =>
    row.cols?.forEach((field) => {
      payload[field.key] = normalizeForSave(field, props.modelValue[field.key]);
    })
  );
  return payload;
}

function validateAll() {
  let hasError = false;
  props.schema.sections?.forEach((sec) =>
    sec.rows?.forEach((row) =>
      row.cols?.forEach((field) => {
        state.touched[field.key] = true;
        if (!isValid(field)) hasError = true;
      })
    )
  );
  return !hasError;
}

async function persistBySections() {
  const resultsByStore = {};

  for (const section of props.schema.sections || []) {
    if (!section.store) continue;

    if (!sectionEditable(section)) continue;

    const api = useStore(section.store);
    const data = collectPerSectionPayload(section);

    try {
      if (props.method === "update") {
        const id = props.ids?.[section.store];
        if (!id)
          throw new Error(`ID ausente para update de '${section.store}'`);
        const res = await api.update(id, data);
        resultsByStore[section.store] = res;
      } else if (props.method === "create") {
        const res = await api.create(data);
        resultsByStore[section.store] = res;
      }
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || "Falha ao salvar";
      emit("error", { store: section.store, message: msg, raw: e });
      throw e;
    }
  }

  return resultsByStore;
}

async function onSubmitClick() {
  if (!validateAll()) return;

  if (!props.method) {
    const payload = collectAllPayload();
    emit("submit", payload);
    return;
  }

  if (allSectionsDisabled()) {
    emit("error", { message: "Você não tem permissão para esta ação." });
    return;
  }

  localLoading.value = true;
  try {
    const resultsByStore = await persistBySections();
    const totalPayload = collectAllPayload();
    emit("success", { resultsByStore, payload: totalPayload });
  } catch (e) {
  } finally {
    localLoading.value = false;
  }
}
</script>

<template>
  <div class="space-y-6 bg-white dark:bg-zinc-900 rounded-2xl">
    <div v-for="(section, si) in schema.sections" :key="si" class="space-y-4">
      <div class="px-4 pt-4 rounded-t-2xl">
        <div class="text-1xl font-medium text-zinc-700 dark:text-zinc-300">
          {{ section.title }}
        </div>
        <div v-if="section.description" class="text-xs text-zinc-500 mt-1">
          {{ section.description }}
        </div>
      </div>

      <div
        v-for="(row, ri) in section.rows"
        :key="ri"
        :class="rowClass(row) + ' px-4'"
      >
        <div v-for="field in row.cols" :key="field.key">
          <label class="block text-[12px] font-medium mb-1">{{
            field.label
          }}</label>

          <template v-if="hasGroup(field)">
            <InputGroup class="w-full">
              <InputGroupAddon
                class="dark:bg-zinc-800 bg-zinc-200 text-zinc-600 border-0 dark:text-zinc-400 rounded-l-lg"
                v-if="field.iconLeft || field.addonLeft"
              >
                <i v-if="field.iconLeft" :class="field.iconLeft"></i>
                <span v-else>{{ field.addonLeft }}</span>
              </InputGroupAddon>

              <InputMask
                v-if="field.type === 'mask' && field.mask"
                v-model="modelValue[field.key]"
                :mask="toPrimeMask(field.mask)"
                size="small"
                :placeholder="field.placeholder"
                :class="[
                  'w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950',
                  {
                    'rounded-r-lg': !(field.iconRight || field.addonRight),
                    'p-invalid': state.touched[field.key] && !isValid(field),
                  },
                ]"
                :pt="{ root: { class: 'w-full' }, input: { class: 'w-full' } }"
                :disabled="!sectionEditable(section)"
                @input="(e) => setModel(field.key, e.value, field)"
                @blur="state.touched[field.key] = true"
                v-bind="field.props"
              />

              <InputText
                v-else
                v-model="modelValue[field.key]"
                :placeholder="field.placeholder"
                size="small"
                :disabled="!sectionEditable(section)"
                :class="[
                  'w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950',
                  {
                    'rounded-r-lg': !(field.iconRight || field.addonRight),
                    'p-invalid': state.touched[field.key] && !isValid(field),
                  },
                ]"
                @input="(e) => setModel(field.key, e.target.value, field)"
                @blur="state.touched[field.key] = true"
                v-bind="field.props"
                v-keyfilter="field.directives?.keyfilter"
              />

              <InputGroupAddon
                class="dark:bg-zinc-800 bg-zinc-200 text-zinc-600 border-0 dark:text-zinc-400 rounded-r-lg"
                v-if="field.iconRight || field.addonRight"
              >
                <i v-if="field.iconRight" :class="field.iconRight"></i>
                <span v-else>{{ field.addonRight }}</span>
              </InputGroupAddon>
            </InputGroup>
          </template>

          <template v-else>
            <InputMask
              v-if="field.type === 'mask' && field.mask"
              v-model="modelValue[field.key]"
              :mask="toPrimeMask(field.mask)"
              size="small"
              :placeholder="field.placeholder"
              class="w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950"
              :pt="{ root: { class: 'w-full' }, input: { class: 'w-full' } }"
              :disabled="!sectionEditable(section)"
              :class="
                state.touched[field.key] && !isValid(field) ? 'p-invalid' : ''
              "
              @input="(e) => setModel(field.key, e.value, field)"
              @blur="state.touched[field.key] = true"
              v-bind="field.props"
            />
            <InputText
              v-else
              v-model="modelValue[field.key]"
              class="w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950"
              size="small"
              :placeholder="field.placeholder"
              :disabled="!sectionEditable(section)"
              :class="
                state.touched[field.key] && !isValid(field) ? 'p-invalid' : ''
              "
              @input="(e) => setModel(field.key, e.target.value, field)"
              @blur="state.touched[field.key] = true"
              v-bind="field.props"
              v-keyfilter="field.directives?.keyfilter"
            />
          </template>

          <p
            v-if="state.touched[field.key] && !isValid(field)"
            class="mt-2 pl-1 text-red-400 text-sm"
          >
            {{ errText(field) }}
          </p>
        </div>
      </div>
    </div>

    <div
      class="flex bg-zinc-100 px-4 py-3 rounded-b-2xl dark:bg-zinc-800 justify-between items-center"
    >
      <h1 class="text-zinc-500 text-sm">Salve as alterações</h1>
      <Button
        :label="submitLabel || schema.submitLabel"
        severity="contrast"
        size="small"
        raised
        class="py-1 text-[12px]"
        :loading="localLoading || loading"
        :disabled="allSectionsDisabled()"
        @click="onSubmitClick"
      />
    </div>
  </div>
</template>

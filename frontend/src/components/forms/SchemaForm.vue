<script setup>
import { ref } from "vue";
import SchemaSection from "./SchemaSection.vue";
import { keyFromSection } from "../../composables/form/formHelpers";

const props = defineProps({
  schema: { type: Object, required: true },
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

const sectionRefs = ref([]);

function assignSectionRef(si) {
  return (el) => {
    if (!sectionRefs.value) sectionRefs.value = [];
    sectionRefs.value[si] = el;
  };
}

function validateAll() {
  let isValid = true;
  (sectionRefs.value || []).forEach((ref) => {
    if (ref?.validate && !ref.validate()) isValid = false;
  });
  return isValid;
}

function collectSectionPayload(idx) {
  const ref = sectionRefs.value?.[idx];
  return ref?.collectPayload ? ref.collectPayload() : {};
}

function collectAllPayload() {
  const payload = {};
  (sectionRefs.value || []).forEach((ref) => {
    if (ref?.collectPayload) Object.assign(payload, ref.collectPayload());
  });
  return payload;
}

function collectGroupedPayload() {
  const sections = props.schema?.sections || [];
  const out = {};
  sections.forEach((section, i) => {
    const secPayload = collectSectionPayload(i);
    if (!secPayload || typeof secPayload !== "object") return;
    if (i === 0) {
      Object.assign(out, secPayload);
    } else {
      const key = keyFromSection(section, i);
      if (Object.keys(secPayload).length > 0) {
        out[key] = secPayload;
      }
    }
  });
  return out;
}

function snapshotAll() {
  (sectionRefs.value || []).forEach((r) => r?.snapshotInitial?.());
}

defineExpose({
  validateAll,
  collectSectionPayload,
  collectAllPayload,
  collectGroupedPayload,
  snapshotAll,
});
</script>

<template>
  <div class="space-y-6">
    <div
      v-for="(section, si) in schema.sections"
      :key="si"
      :id="`sec-${si}`"
      class="bg-white dark:bg-zinc-900 shadow-md rounded-2xl space-y-4 scroll-mt-24"
    >
      <div class="px-4 pt-4 rounded-t-2xl">
        <div class="text-1xl font-medium text-zinc-700 dark:text-zinc-300">
          {{ section.title }}
        </div>
        <div v-if="section.description" class="text-xs text-zinc-500 mt-1">
          {{ section.description }}
        </div>
      </div>

      <div class="px-4 pb-4">
        <SchemaSection
          :ref="assignSectionRef(si)"
          :section="section"
          :modelValue="modelValue"
          :loading="loading"
          :mode="mode"
          :perm-base="permBase"
          @update:modelValue="$emit('update:modelValue', $event)"
        />
      </div>
    </div>
  </div>
</template>

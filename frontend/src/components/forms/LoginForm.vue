<template>
  <form @submit.prevent="handleSubmit" class="flex flex-col gap-2 w-full">
    <div v-for="field in schema" :key="field.key" class="flex flex-col gap-2 w-full">
      <label
        v-if="field.label"
        :for="idFor(field.key)"
        class="text-sm font-semibold"
      >
        {{ field.label }}
      </label>

      <!-- TEXT / EMAIL -->
      <InputText
        v-if="field.type === 'text' || field.type === 'email'"
        :id="idFor(field.key)"
        v-model="model[field.key]"
        :type="field.type"
        :placeholder="field.placeholder || ''"
        :disabled="loading || field.disabled"
        :class="[
          'w-full focus:!ring-zinc-500 focus:!border-zinc-500',
          touched[field.key] && errors[field.key] ? 'p-invalid' : ''
        ]"
        @blur="onBlur(field.key)"
        size="small"
      />

      <!-- PASSWORD -->
      <Password
        v-else-if="field.type === 'password'"
        :inputId="idFor(field.key)"
        v-model="model[field.key]"
        :placeholder="field.placeholder || ''"
        :toggleMask="true"
        :feedback="false"
        :disabled="loading || field.disabled"
        input-class='w-full focus:ring-2 focus:!ring-zinc-500 focus:!border-zinc-500'
        :class="touched[field.key] && errors[field.key] ? 'p-invalid' : ''"
        @blur="onBlur(field.key)"
        size="small"
      />

      <slot v-else :name="`field-${field.key}`" :model="model" :field="field" />

      <!-- Error -->
      <small v-if="touched[field.key] && errors[field.key]" class="text-red-500">
        {{ errors[field.key] }}
      </small>
    </div>

    <slot name="extras" :model="model" />

    <Button
      class="mt-4"
      :label="submitLabel"
      icon="pi pi-user"
      :disabled="loading"
      severity="contrast"
      type="submit"
      size="small"
    />
  </form>
</template>
<script setup>
import { reactive, toRaw } from 'vue'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'

const props = defineProps({
  schema: { type: Array, required: true },
  initial: { type: Object, default: () => ({}) },
  submitLabel: { type: String, default: 'Submit' },
  loading: { type: Boolean, default: false }
})
const emit = defineEmits(['submit'])

const model = reactive({})
const touched = reactive({})
const errors = reactive({})

function init() {
  for (const f of props.schema) {
    const def = f.type === 'checkbox' ? false : ''
    model[f.key] = props.initial[f.key] ?? def
    touched[f.key] = false
    errors[f.key] = null
  }
}
init()

function idFor(key) {
  return `fld_${key}`
}

function validateField(key) {
  const field = props.schema.find(f => f.key === key)
  if (!field || !field.rules?.length) {
    errors[key] = null
    return true
  }
  for (const rule of field.rules) {
    const res = rule(model[key])
    if (res !== true) {
      errors[key] = typeof res === 'string' ? res : 'Invalid value'
      return false
    }
  }
  errors[key] = null
  return true
}

function validateAll() {
  let ok = true
  for (const f of props.schema) {
    const v = validateField(f.key)
    if (!v) ok = false
  }
  return ok
}

function onBlur(key) {
  touched[key] = true
  validateField(key)
}

function handleSubmit() {
  if (!validateAll()) {
    for (const f of props.schema) touched[f.key] = true
    return
  }
  emit('submit', toRaw(model))
}
</script>

<style scoped>
.p-invalid :deep(input) {
  border-color: rgb(239 68 68);
  box-shadow: none;
}
</style>
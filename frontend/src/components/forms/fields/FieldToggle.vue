<script setup>
import ToggleSwitch from "primevue/toggleswitch";
import { computed } from 'vue'

const props = defineProps({
  label: String,
  name: String,
  modelValue: [Boolean, Number],
  disabled: Boolean,
})
const emit = defineEmits(["update:modelValue"])

// name acessível/reativo
const labelName = computed(() =>
  (props.label || 'field').toLowerCase().replace(/\s+/g, '_')
)

// checado como booleano
const checked = computed(() => props.modelValue === true)
</script>

<template>
  <label v-if="label" class="block text-[12px] font-medium mb-1">{{ label }}</label>
  <div class="flex items-center mt-2.5 gap-2">
    <ToggleSwitch
      :modelValue="checked"
      :name="labelName"
      :disabled="disabled"
      @update:modelValue="(v) => emit('update:modelValue', !!v)"  
      :pt="{
        slider: { class: checked ? 'bg-zinc-900 dark:bg-zinc-50' : 'bg-zinc-300 dark:bg-zinc-700' },
        handle: { class: 'bg-white dark:bg-zinc-900' }
      }"
    />
  </div>
</template>

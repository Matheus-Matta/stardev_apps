<script setup>
import Icon from "./Icon.vue"
import AppInput from "./Input.vue"

const props = defineProps({
  label: { type: String, required: true },
  icon: { type: String, default: "" },
  modelValue: { type: [String, Number], default: "" },
  placeholder: { type: String, default: "" },
  type: { type: String, default: "text" },
  editing: { type: Boolean, default: false },
})

const emit = defineEmits(["update:modelValue"])
</script>

<template>
  <div>
    <label class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-400">
      {{ label }}
    </label>

    <!-- modo leitura -->
    <template v-if="!editing">
      <p class="rounded-lg border-1 border-gray-200 dark:border-gray-700 px-1 text-gray-600 dark:text-gray-200 flex items-center py-2">
        <Icon v-if="icon" :name="icon" size="20" class="mr-3 pl-2 text-gray-600 dark:text-gray-200" />
        {{ (modelValue ?? '') !== '' ? modelValue : '-' }}
      </p>
    </template>

    <!-- modo edição -->
    <template v-else>
      <AppInput
        :type="type"
        :model-value="modelValue"
        @update:model-value="emit('update:modelValue', $event)"
        :leftIcon="icon"
        :placeholder="placeholder"
      />
    </template>
  </div>
</template>

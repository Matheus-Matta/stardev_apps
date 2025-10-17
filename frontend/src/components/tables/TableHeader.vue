<script setup>
import { ref } from "vue";
import QuickCreateDialog from "../forms/QuickCreateDialog.vue";

const props = defineProps({
  schema: Object,
  dateRange: [Array, null],
  onDateChange: Function,
  showAddButton: Boolean,
  modelname: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['add-click', 'quick-created', 'quick-error']);
const visibleQuick = ref(false);

function handleDateChange(value) {
  props.onDateChange?.(value);
}

function handleAddClick() {
  try {
    emit('add-click');
    visibleQuick.value = true;
  } catch (error) {
    console.error('Erro ao lidar com add-click:', error);
    emit('quick-error', { message: 'Falha ao abrir criação rápida', raw: error });
  }
}

function onQuickCreated(data) {
  visibleQuick.value = false;
  emit('quick-created', data); 
}

function onQuickError(err) {
  visibleQuick.value = false; 
  emit('quick-error', err);
}
</script>

<template>
  <div class="flex justify-between">
    <div class="flex my-4 mx-2 items-center gap-4">
      <i :class="schema.icon + ' text-2xl text-zinc-700 dark:text-zinc-200'"></i>
      <h1 class="text-zinc-700 dark:text-zinc-200 font-semibold">
        {{ schema.title }}
      </h1>
    </div>
    
    <div class="flex items-center gap-4">
      <DatePicker
        :modelValue="dateRange"
        @update:modelValue="handleDateChange"
        placeholder="Filtre a data aqui!"
        :manualInput="false"
        size="small"
        class="h-7.5 m-0 p-0"
        selectionMode="range"
        showIcon
        dateFormat="dd/mm/yy"
        iconDisplay="input"
        variant="filled"
        inputId="in_label"
      />
      
      <Button
        v-if="showAddButton"
        label="Adicionar"
        severity="contrast"
        size="small"
        raised
        class="py-1 text-[12px]"
        :pt="{ icon: 'text-[12px]' }"
        @click="handleAddClick"
      />

      <QuickCreateDialog
        :modelname="modelname"
        :visible="visibleQuick"
        @update:visible="visibleQuick = $event"
        @created="onQuickCreated"
        @error="onQuickError"
      />
    </div>
  </div>
</template>
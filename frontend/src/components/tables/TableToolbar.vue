<script setup>
const props = defineProps({
  searchValue: String,
  searchLoading: Boolean,
  onSearchEnter: Function,
  onClearAll: Function
});

const emit = defineEmits(['update:searchValue']);

function handleInput(e) {
  emit('update:searchValue', e.target.value);
}
</script>

<template>
  <div class="flex items-center gap-2 px-2 py-2">
    <IconField class="flex-1">
      <InputIcon class="pi pi-search" />
      <InputText
        :modelValue="searchValue"
        @input="handleInput"
        @keydown.enter="onSearchEnter"
        placeholder="Procurar..."
        size="small"
        variant="filled"
        class="w-full pl-10 pr-16 py-1 rounded-full bg-white dark:bg-zinc-800 border dark:border-zinc-700 text-sm dark:text-zinc-200
               dark:placeholder-zinc-400 focus:outline-none focus:ring-2 dark:focus:ring-zinc-700 focus:ring-zinc-100 dark:focus:border-zinc-600 focus:border-zinc-300"
      />
      <InputIcon v-if="searchLoading" class="pi pi-spin pi-spinner" />
    </IconField>

    <div class="flex items-center gap-2">
      <Button
        label="Limpar"
        icon="pi pi-filter-slash"
        variant="text"
        size="small"
        raised
        severity="secondary"
        class="py-1 text-[12px] rounded-2xl"
        :pt="{ icon: 'text-[12px]' }"
        @click="onClearAll"
      />
      
      <Button
        label="Colunas"
        icon="pi pi-list"
        variant="text"
        size="small"
        raised
        severity="secondary"
        class="py-1 text-[12px] rounded-2xl"
        :pt="{ icon: 'text-[12px]' }"
      />
    </div>
  </div>
</template>
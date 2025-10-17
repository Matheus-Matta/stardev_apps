// composables/useTableSorting.js
import { ref } from 'vue';

export function useTableSorting(schema, resetPagination, onLoad) {
  const sortField = ref(schema.value?.defaultSort?.field || '');
  const sortOrder = ref(schema.value?.defaultSort?.order || 1); // 1 asc, -1 desc

  function toggleSort(col) {
    const field = col.sortField || col.field;
    if (!field) return;

    if (sortField.value === field) {
      sortOrder.value = sortOrder.value === 1 ? -1 : 1;
    } else {
      sortField.value = field;
      sortOrder.value = 1;
    }

    resetPagination();
    onLoad();
  }

  function ariaSortFor(col) {
    const field = col.sortField || col.field;
    if (!field || field !== sortField.value) return 'none';
    return sortOrder.value === 1 ? 'ascending' : 'descending';
  }

  function resetSorting() {
    sortField.value = schema.value?.defaultSort?.field || '';
    sortOrder.value = schema.value?.defaultSort?.order || 1;
  }

  return {
    sortField,
    sortOrder,
    toggleSort,
    ariaSortFor,
    resetSorting
  };
}
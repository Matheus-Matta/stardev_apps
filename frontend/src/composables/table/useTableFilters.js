// composables/table/useTableFilters.js
import { ref, reactive } from 'vue';

export function useTableFilters(schema, resetPagination, onLoad) {
  const searchValue = ref('');
  const searchLoading = ref(false);
  const dateRange = ref(null);

  const extra = reactive({
    [(schema.value.server && schema.value.server.startParam) || 'start_date']: null,
    [(schema.value.server && schema.value.server.endParam)   || 'end_date']: null,
  });

  async function onSearchEnter() {
    searchLoading.value = true;
    resetPagination();
    await onLoad();
    searchLoading.value = false;
  }

  function clearAll() {
    searchValue.value = '';
    dateRange.value = null;
    resetPagination();
    onLoad();
  }

  function onFilterDebounced() {
    resetPagination();
    onLoad();
  }
  function initFilters() {
  }

  return {
    searchValue,
    searchLoading,
    dateRange,
    extra,
    initFilters,
    onFilterDebounced,
    onSearchEnter,
    clearAll
  };
}

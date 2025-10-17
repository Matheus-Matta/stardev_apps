// composables/table/useTablePagination.js
import { ref, computed } from 'vue';

export function useTablePagination(schema, totalRecords, onLoad) {
  const first = ref(0);
  const rowsPerPage = ref(schema.value.pageSize || 10);
  const pageSizeOptions = computed(() => schema.value.rowsPerPageOptions || [10, 20, 50, 100]);

  const totalPages = computed(() => Math.max(1, Math.ceil((totalRecords.value || 0) / (rowsPerPage.value || 10))));
  const currentPage = computed(() => (rowsPerPage.value ? Math.floor(first.value / rowsPerPage.value) + 1 : 1));

  const startItem = computed(() => (totalRecords.value ? first.value + 1 : 0));
  const endItem = computed(() => Math.min(first.value + rowsPerPage.value, totalRecords.value || 0));

  const pagesWindow = computed(() => {
    const size = 5;
    let start = Math.max(1, currentPage.value - Math.floor(size / 2));
    let end = Math.min(totalPages.value, start + size - 1);
    start = Math.max(1, end - size + 1);
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  });

  function goToPage(p) {
    const page = Math.min(Math.max(1, p), totalPages.value);
    first.value = (page - 1) * rowsPerPage.value;
    onLoad();
  }
  function goFirst() { goToPage(1); }
  function goPrev() { goToPage(currentPage.value - 1); }
  function goNext() { goToPage(currentPage.value + 1); }
  function goLast() { goToPage(totalPages.value); }

  function onPageSizeChange(newSize) {
    if (!Number.isFinite(newSize) || newSize <= 0) return;
    rowsPerPage.value = newSize;
    first.value = 0;
    onLoad();
  }

  function resetPagination() { first.value = 0; }

  return {
    first, rowsPerPage, pageSizeOptions,
    totalPages, currentPage, startItem, endItem, pagesWindow,
    goToPage, goFirst, goPrev, goNext, goLast,
    onPageSizeChange, resetPagination
  };
}

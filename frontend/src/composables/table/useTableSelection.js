// composables/useTableSelection.js
import { ref, computed } from 'vue';

export function useTableSelection(rows) {
  const selectedIds = ref(new Set());

  const pageIds = computed(() => 
    new Set(rows.value.map(r => r.id))
  );

  function isAllPageSelected() {
    return rows.value.length > 0 && 
           rows.value.every(r => selectedIds.value.has(r.id));
  }

  function toggleSelectAllPage() {
    const all = isAllPageSelected();
    if (all) {
      rows.value.forEach(r => selectedIds.value.delete(r.id));
    } else {
      rows.value.forEach(r => selectedIds.value.add(r.id));
    }
  }

  function toggleRowSelection(id) {
    if (selectedIds.value.has(id)) {
      selectedIds.value.delete(id);
    } else {
      selectedIds.value.add(id);
    }
  }

  const headerIndeterminate = computed(() => {
    if (!rows.value.length) return false;
    
    let count = 0;
    selectedIds.value.forEach(id => {
      if (pageIds.value.has(id)) count++;
    });
    
    return count > 0 && count < rows.value.length;
  });

  function clearSelection() {
    selectedIds.value = new Set();
  }

  return {
    selectedIds,
    isAllPageSelected,
    toggleSelectAllPage,
    toggleRowSelection,
    headerIndeterminate,
    clearSelection
  };
}
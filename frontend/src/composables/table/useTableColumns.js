// composables/table/useTableColumns.js
import { computed } from 'vue';

export function useTableColumns(schema) {
  const allColumns = computed(() => {
    const cols = (schema.value.columns || []).map(c => ({ ...c }));
    const order = schema.value.ListFields || cols.map(c => c.field || c.type);
    const allow = new Set(order);
    cols.forEach(c => {
      const key = c.field || c.type;
      if (!allow.has(key)) c.hidden = true;
    });
    return cols;
  });

  const visibleCols = computed(() => {
    const cols = allColumns.value;
    const order = schema.value.ListFields || cols.map(c => c.field || c.type);
    const byKey = new Map(cols.map(c => [c.field || c.type, c]));
    return order.map(k => byKey.get(k)).filter(Boolean);
  });

  return { allColumns, visibleCols };
}

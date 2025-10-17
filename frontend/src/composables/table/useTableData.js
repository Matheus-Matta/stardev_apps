// composables/table/useTableData.js
import { ref } from 'vue';
import { buildListParams } from '../../lib/forms/tableQuery';

export function useTableData(schema, store) {
  const rows = ref([]);
  const totalRecords = ref(0);
  const loading = ref(false);
  const error = ref(null);

  async function loadRows(params) {
    loading.value = true;
    error.value = null;

    try {
      const queryParams = buildListParams(schema.value, {
        rows: params.rows,
        first: params.first,
        sortField: params.sortField,
        sortOrder: params.sortOrder,
        filters: {}, 
        extra: params.extra || {}
      });

      const searchKey = (schema.value.server && schema.value.server.searchParam) || 'search';
      if (params.searchValue && params.searchValue.trim()) {
        queryParams[searchKey] = params.searchValue.trim();
      }
      const startKey = (schema.value.server && schema.value.server.startParam) || 'start_date';
      const endKey   = (schema.value.server && schema.value.server.endParam)   || 'end_date';
      if (Array.isArray(params.dateRange) && params.dateRange[0] && params.dateRange[1]) {
        queryParams[startKey] = startOfDayISO(params.dateRange[0]);
        queryParams[endKey]   = endOfDayISO(params.dateRange[1]);
      }
      const resp = await store.value.list(queryParams);
      rows.value = resp?.items || [];
      totalRecords.value = resp?.count ?? rows.value.length;
    } catch (e) {
      error.value = e?.message || 'Falha ao carregar';
    } finally {
      loading.value = false;
    }
  }

  return { rows, totalRecords, loading, error, loadRows };
}

function startOfDayISO(d) {
  if (!d) return null;
  const dt = new Date(d);
  dt.setHours(0, 0, 0, 0);
  return dt.toISOString();
}
function endOfDayISO(d) {
  if (!d) return null;
  const dt = new Date(d);
  dt.setHours(23, 59, 59, 999);
  return dt.toISOString();
}

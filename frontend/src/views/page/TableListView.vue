<script setup>
import { ref, reactive, computed, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import BaseView from "../../layout/BaseView.vue";

import { FilterMatchMode, FilterOperator } from "@primevue/core/api";
import { useStore } from "../../store/index";
import { getTableSchema } from "../../forms/schemas/tables/index";
import { buildListParams } from "../../lib/tableQuery";

// util: safe-get dotpath
function get(obj, path, def = undefined) {
    if (!path) return def;
    return String(path)
        .split(".")
        .reduce((acc, k) => (acc && acc[k] != null ? acc[k] : def), obj);
}

const route = useRoute();
const namePlural = computed(() => (route.params.model || "").toString());
const schema = computed(() => getTableSchema(namePlural.value));
const store = computed(() => useStore(schema.value.store));

// i18n para tradução
const { t } = useI18n();

// dados / estado
const rows = ref([]);
const totalRecords = ref(0);
const loading = ref(false);
const error = ref(null);

// paginação / sort
const first = ref(0);
const rowsPerPage = ref(schema.value.pageSize || 10);
const sortField = ref(schema.value?.defaultSort?.field || "");
const sortOrder = ref(schema.value?.defaultSort?.order || 1); // 1 asc, -1 desc
const pageSizeOptions = computed(() => schema.value.rowsPerPageOptions || [10, 20, 50, 100]);

// seleção
const selectedIds = ref(new Set());

// filtros (mantidos para futura linha de filtros por coluna)
const filters = ref({});
function initFilters() {
    const f = { global: { value: null, matchMode: FilterMatchMode.CONTAINS } };
    for (const col of schema.value.columns) {
        if (!col.filter) continue;
        const key = col.filterField || col.field;
        if (!key) continue;

        const matchMode = col.filter.matchMode || FilterMatchMode.CONTAINS;
        const operator = col.filter.operator || FilterOperator.AND;

        if (matchMode === FilterMatchMode.BETWEEN) {
            f[key] = { value: [0, 100], matchMode };
        } else if (matchMode === FilterMatchMode.IN) {
            f[key] = { value: [], matchMode };
        } else if (matchMode === FilterMatchMode.DATE_IS) {
            f[key] = { operator, constraints: [{ value: null, matchMode }] };
        } else {
            f[key] = { operator, constraints: [{ value: null, matchMode }] };
        }
    }
    filters.value = f;
}
initFilters();

// toolbar: search + date range
const SearchValue = ref("");
const SearchLoading = ref(false);
const dateRange = ref(null); // [Date, Date] | null

// extra params
const extra = reactive({
    [schema.value.server.startParam || "start_date"]: null,
    [schema.value.server.endParam || "end_date"]: null,
});

// visibilidade das colunas (respeita listDisplay)
const visibleCols = computed(() => {
    const cols = (schema.value.columns || []).filter((c) => {
        if (c.type === "selection") return false;
        if (c.hidden === true) return false;
        if (c.type === "actions" && (!Array.isArray(c.actions) || c.actions.length === 0)) return false;
        return true;
    });
    const order = schema.value.listDisplay || cols.map((c) => c.field || c.type);
    const byKey = new Map(cols.map((c) => [c.field || c.type, c]));
    return order.map((k) => byKey.get(k)).filter(Boolean);
});

// helpers — normalização de datas para query e formatação para célula
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
function formatDateCell(val) {
    if (!val) return "";
    const d = new Date(val);
    if (isNaN(d)) return String(val);
    return d.toLocaleDateString("pt-BR");
}

async function loadRows() {
    loading.value = true;
    error.value = null;
    try {
        const params = buildListParams(schema.value, {
            rows: rowsPerPage.value,
            first: first.value,
            sortField: sortField.value,
            sortOrder: sortOrder.value,
            filters: filters.value,
            extra,
        });

        // SEARCH → ?search=...
        const searchKey = schema.value.server?.searchParam || "search";
        if (SearchValue.value?.trim()) params[searchKey] = SearchValue.value.trim();
        else delete params[searchKey];

        // RANGE → ?start_date / ?end_date (normalizado início/fim do dia)
        const startKey = schema.value.server?.startParam || "start_date";
        const endKey = schema.value.server?.endParam || "end_date";
        if (Array.isArray(dateRange.value) && dateRange.value[0] && dateRange.value[1]) {
            params[startKey] = startOfDayISO(dateRange.value[0]);
            params[endKey] = endOfDayISO(dateRange.value[1]);
        } else {
            delete params[startKey];
            delete params[endKey];
        }

        const resp = await store.value.list(params);

        // Ajustando os dados conforme esperado { items, count }
        rows.value = resp?.items || [];
        totalRecords.value = resp?.count ?? rows.value.length;
    } catch (e) {
        error.value = e?.message || "Falha ao carregar";
    } finally {
        loading.value = false;
    }
}

// sort / página
function onPageChange(newFirst) {
    first.value = newFirst;
    loadRows();
}
function toggleSort(col) {
    const field = col.sortField || col.field;
    if (!field) return;
    if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 1 ? -1 : 1;
    } else {
        sortField.value = field;
        sortOrder.value = 1;
    }
    first.value = 0;
    loadRows();
}
function ariaSortFor(col) {
    const field = col.sortField || col.field;
    if (!field || field !== sortField.value) return "none";
    return sortOrder.value === 1 ? "ascending" : "descending";
}

// debounce p/ filtros/toolbar
let t;
function onFilterDebounced() {
    clearTimeout(t);
    t = setTimeout(() => {
        first.value = 0;
        loadRows();
    }, 350);
}
function onSearchEnter() {
    SearchLoading.value = true;
    first.value = 0;
    loadRows().finally(() => (SearchLoading.value = false));
}
function clearAll() {
    SearchValue.value = "";
    dateRange.value = null;
    initFilters();
    first.value = 0;
    loadRows();
}

// seleção
function isAllPageSelected() {
    return rows.value.length > 0 && rows.value.every((r) => selectedIds.value.has(r.id));
}
function toggleSelectAllPage() {
    const all = isAllPageSelected();
    if (all) rows.value.forEach((r) => selectedIds.value.delete(r.id));
    else rows.value.forEach((r) => selectedIds.value.add(r.id));
}
function toggleRowSelection(id) {
    if (selectedIds.value.has(id)) selectedIds.value.delete(id);
    else selectedIds.value.add(id);
}
const pageIds = computed(() => new Set(rows.value.map((r) => r.id)));
const headerIndeterminate = computed(() => {
    if (!rows.value.length) return false;
    let count = 0;
    selectedIds.value.forEach((id) => {
        if (pageIds.value.has(id)) count++;
    });
    return count > 0 && count < rows.value.length;
});

// paginação — estilo “foto”
const totalPages = computed(() =>
    Math.max(1, Math.ceil((totalRecords.value || 0) / (rowsPerPage.value || 10)))
);
const currentPage = computed(() =>
    rowsPerPage.value ? Math.floor(first.value / rowsPerPage.value) + 1 : 1
);
function goToPage(p) {
    const page = Math.min(Math.max(1, p), totalPages.value);
    onPageChange((page - 1) * rowsPerPage.value);
}
function goFirst() { goToPage(1); }
function goPrev() { goToPage(currentPage.value - 1); }
function goNext() { goToPage(currentPage.value + 1); }
function goLast() { goToPage(totalPages.value); }
const pagesWindow = computed(() => {
    const size = 5;
    let start = Math.max(1, currentPage.value - Math.floor(size / 2));
    let end = Math.min(totalPages.value, start + size - 1);
    start = Math.max(1, end - size + 1);
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});
const startItem = computed(() => (totalRecords.value ? first.value + 1 : 0));
const endItem = computed(() => Math.min(first.value + rowsPerPage.value, totalRecords.value || 0));

// mudança do page size (select nativo)
function onPageSizeChange(e) {
    const newSize = Number(e.target.value);
    if (!Number.isFinite(newSize) || newSize <= 0) return;
    rowsPerPage.value = newSize;
    first.value = 0;
    loadRows();
}

// recarregar ao trocar de recurso (rota)
watch(
    () => route.params.model,
    () => {
        initFilters();
        first.value = 0;
        sortField.value = schema.value?.defaultSort?.field || "";
        sortOrder.value = schema.value?.defaultSort?.order || 1;
        selectedIds.value = new Set();
        loadRows();
    }
);

onMounted(loadRows);
</script>

<template>
    <BaseView>
        <div class="mx-auto h-full flex flex-col">
            <!-- Header / Ações -->
            <div class="flex justify-between">
                <div class="flex my-4 mx-2 items-center gap-4">
                    <i :class="schema.icon + ' text-2xl text-zinc-700 dark:text-zinc-200'"></i>
                    <h1 class="text-zinc-700 dark:text-zinc-200 font-semibold">{{ schema.title }}</h1>
                </div>
                <div class="flex items-center gap-4">
                    <DatePicker v-model="dateRange" placeholder="Filtre a data aqui!" :manualInput="false" size="small"
                        class="h-7.5 m-0 p-0" selectionMode="range" showIcon iconDisplay="input" variant="filled"
                        inputId="in_label" @update:modelValue="onFilterDebounced" />
                    <Button label="Adicionar" severity="contrast" size="small" icon="pi pi-plus" raised
                        class="py-1 text-[12px]" :pt="{ icon: 'text-[12px]' }" />
                </div>
            </div>

            <!-- Toolbar: Search + Limpar/Colunas -->
            <div class="flex items-center gap-2 px-2 py-2">
                <IconField class="flex-1">
                    <InputIcon class="pi pi-search" />
                    <InputText v-model="SearchValue" placeholder="Procurar..." size="small" variant="filled"
                        class="w-full pl-10 pr-16 py-1 rounded-full bg-white dark:bg-zinc-800 border dark:border-zinc-700 text-sm dark:text-zinc-200
                   dark:placeholder-zinc-400 focus:outline-none focus:ring-2 dark:focus:ring-zinc-700 focus:ring-zinc-100 dark:focus:border-zinc-600 focus:border-zinc-300"
                        @keydown.enter="onSearchEnter" />
                    <InputIcon v-if="SearchLoading" class="pi pi-spin pi-spinner" />
                </IconField>

                <div class="flex items-center gap-2">
                    <Button label="Limpar" icon="pi pi-filter-slash" variant="text" size="small" raised
                        severity="secondary" class="py-1 text-[12px] rounded-2xl" :pt="{ icon: 'text-[12px]' }"
                        @click="clearAll" />
                    <Button label="Colunas" icon="pi pi-list" variant="text" size="small" raised severity="secondary"
                        class="py-1 text-[12px] rounded-2xl" :pt="{ icon: 'text-[12px]' }" />
                </div>
            </div>

            <!-- Chips de filtros (placeholder, mantém UX/UI) -->
            <div class="flex itens-center flex-wrap gap-2 px-2 py-2 border-t border-zinc-200 dark:border-zinc-800">
                <Button label="Nome Igual Matheus" icon="pi pi-times" iconPos="right" size="small" variant="text"
                    severity="secondary"
                    class="py-1 text-[10px] rounded-2xl border-dashed border-zinc-300 dark:border-zinc-700"
                    :pt="{ icon: 'text-[10px]' }" />
                <Button label="Add filtro" icon="pi pi-plus" size="small" variant="text" severity="secondary"
                    class="py-1 text-[10px] gap-1 rounded-2xl border-dashed border-zinc-300 dark:border-zinc-700"
                    :pt="{ icon: 'text-[10px]' }" />
            </div>

            <!-- Tabela -->
            <div class="min-h-0 flex-1 overflow-auto rounded-lg bg-white dark:bg-zinc-900">
                <div class="min-h-0 flex-1 overflow-auto bg-white dark:bg-zinc-900">
                    <table class="w-full table-fixed text-sm" role="table" :aria-label="`Tabela de ${schema.title}`">
                        <colgroup>
                            <col v-if="schema.selection" style="width: 2.25rem" />
                            <col v-for="(col, i) in visibleCols" :key="'cg-' + i"
                                :style="col.width ? `width:${col.width}` : ''" />
                        </colgroup>

                        <thead>
                            <tr class="bg-zinc-200/50 dark:bg-zinc-800 sticky top-0 z-10">
                                <!-- seleção -->
                                <th v-if="schema.selection" scope="col"
                                    class="w-10 px-2 py-2 border-b border-zinc-200 dark:border-zinc-800">
                                    <Checkbox class="mb-0.5" size="small" binary :modelValue="isAllPageSelected()"
                                        :indeterminate="headerIndeterminate" @update:modelValue="toggleSelectAllPage" />
                                </th>

                                <!-- cabeçalhos -->
                                <th v-for="(col, i) in visibleCols" :key="'h-' + i" scope="col"
                                    :aria-sort="ariaSortFor(col)"
                                    class="px-3 py-2 border-b border-zinc-200 dark:border-zinc-800 text-[12px] font-semibold text-start text-zinc-700 dark:text-zinc-200 select-none">
                                    <button v-if="col.sortable" type="button"
                                        class="inline-flex items-center gap-1 hover:text-zinc-900 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-zinc-300 dark:focus:ring-zinc-700 rounded"
                                        @click="toggleSort(col)">
                                        <span class="truncate">{{ col.header }}</span>
                                        <i :class="(col.sortField || col.field) === sortField ? (sortOrder === 1 ? 'pi pi-sort-amount-up' : 'pi pi-sort-amount-down') : 'pi pi-sort'"
                                            class="text-[10px] opacity-70" />
                                    </button>
                                    <span v-else class="truncate">{{ col.header }}</span>
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-if="loading">
                                <td :colspan="visibleCols.length + (schema.selection ? 1 : 0)"
                                    class="px-4 py-8 text-center text-zinc-500">
                                    Carregando...
                                </td>
                            </tr>

                            <tr v-else-if="rows.length === 0">
                                <td :colspan="visibleCols.length + (schema.selection ? 1 : 0)"
                                    class="px-4 py-10 text-center text-zinc-500">
                                    Nenhum registro encontrado.
                                </td>
                            </tr>

                            <tr v-else v-for="(row, rIndex) in rows" :key="row.id || rIndex"
                                class="odd:bg-zinc-50/40 dark:odd:bg-zinc-900/40 hover:bg-zinc-100/60 dark:hover:bg-zinc-800/60">
                                <td v-if="schema.selection" class="px-2.5 pb-2">
                                    <Checkbox binary size="small" :modelValue="selectedIds.has(row.id)"
                                        @update:modelValue="() => toggleRowSelection(row.id)" />
                                </td>

                                <template v-for="(col, i) in visibleCols" :key="'c-'+rIndex+'-'+i">
                                    <td v-if="!col.type || col.type === 'text'" class="px-3 py-1.5 truncate">
                                        {{ get(row, col.field, "....") }}
                                    </td>

                                    <td v-else-if="col.type === 'avatarText'" class="px-3 py-1.5">
                                        <div class="flex items-center gap-2">
                                            <img :src="col.avatar?.(row)" alt=""
                                                class="h-6 w-6 rounded-full object-cover" />
                                            <span class="truncate">{{ col.text?.(row) }}</span>
                                        </div>
                                    </td>

                                    <td v-else-if="col.type === 'image'">
                                        <img :src="get(row, col.field)" alt="" class="h-8 w-8 rounded object-cover" />
                                    </td>

                                    <td v-else-if="col.type === 'tag'" class="px-3 py-1.5">
                                        <Tag size="small" :value="get(row, col.field)"
                                            :severity="col.severityMap?.[get(row, col.field)] ?? null" :pt="{
                                                label: { class: 'text-[12px] font-semibold' },
                                                root: {
                                                    class: 'rounded-full py-0.5 pt-1 px-3'
                                                }
                                            }" />
                                    </td>

                                    <td v-else-if="col.type === 'date'" class="px-3 py-1.5">
                                        {{ col.format ? col.format(get(row, col.field)) : formatDateCell(get(row,
                                        col.field)) }}
                                    </td>

                                    <td v-else-if="col.type === 'currency'" class="px-3 py-1.5">
                                        {{ col.format ? col.format(get(row, col.field)) : get(row, col.field) }}
                                    </td>

                                    <td v-else-if="col.type === 'progress'" class="px-3 py-1.5">
                                        <ProgressBar :value="get(row, col.field) || 0" :showValue="false"
                                            style="height: 6px" />
                                    </td>

                                    <td v-else-if="col.type === 'actions'" class="px-3 py-1.5">
                                        <div class="flex justify-start gap-1">
                                            <Button v-for="(act, i2) in col.actions" :key="i2"
                                                :icon="act.icon || 'pi pi-cog'" :rounded="act.rounded ?? true"
                                                size="small" @click="() => act.onClick?.(row)" />
                                        </div>
                                    </td>
                                </template>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Footer / paginação + page size -->
            <div
                class="flex items-center justify-between gap-3 py-3 px-3 bg-white dark:bg-zinc-900 border-t border-zinc-200 dark:border-zinc-800">
                <div class="text-xs text-zinc-600 dark:text-zinc-400">
                    Mostrando <b>{{ startItem }}</b>–<b>{{ endItem }}</b> de <b>{{ totalRecords }}</b>
                </div>

                <nav class="flex items-center gap-1 text-sm">
                    <i class="pi pi-angle-double-left p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
                        :class="{ 'pointer-events-none opacity-40': currentPage === 1 }"
                        @click="currentPage !== 1 && goFirst()" aria-label="Primeira página" title="Primeira página" />
                    <i class="pi pi-angle-left p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
                        :class="{ 'pointer-events-none opacity-40': currentPage === 1 }"
                        @click="currentPage !== 1 && goPrev()" aria-label="Página anterior" title="Página anterior" />

                    <button v-for="p in pagesWindow" :key="'p-' + p" @click="goToPage(p)"
                        :aria-current="p === currentPage ? 'page' : undefined"
                        class="h-7 w-7 rounded-full grid place-items-center text-xs transition" :class="p === currentPage
                            ? 'bg-zinc-800 text-zinc-100 dark:bg-zinc-100 dark:text-zinc-900 font-semibold'
                            : 'text-zinc-300 hover:bg-zinc-800/60'">
                        {{ p }}
                    </button>

                    <i class="pi pi-angle-right p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
                        :class="{ 'pointer-events-none opacity-40': currentPage === totalPages }"
                        @click="currentPage !== totalPages && goNext()" aria-label="Próxima página"
                        title="Próxima página" />
                    <i class="pi pi-angle-double-right p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
                        :class="{ 'pointer-events-none opacity-40': currentPage === totalPages }"
                        @click="currentPage !== totalPages && goLast()" aria-label="Última página"
                        title="Última página" />
                </nav>

                <!-- Select nativo (Tailwind) para page size -->
                <div class="ml-2">
                    <div class="relative">
                        <select v-model.number="rowsPerPage" @change="onPageSizeChange" class="h-7 pl-2 pr-7 rounded-md bg-white text-zinc-700 border border-zinc-300
                     dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700
                     text-xs focus:outline-none focus:ring-2 focus:ring-zinc-300 dark:focus:ring-zinc-700"
                            aria-label="Itens por página" title="Itens por página">
                            <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">{{ opt }}</option>
                        </select>
                        <span
                            class="pointer-events-none absolute inset-y-0 right-1 grid place-items-center text-zinc-400 text-[10px]">▾</span>
                    </div>
                </div>
            </div>
        </div>
    </BaseView>
</template>

<style scoped>
thead th {
    position: sticky;
    top: 0;
}

th>button:focus {
    outline: 2px solid rgb(212 212 216);
    outline-offset: 1px;
    border-radius: .375rem;
}
</style>

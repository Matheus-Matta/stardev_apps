<script setup>
import { computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

import { useUserStore } from '../../store/auth/user';

import TableHeader from './TableHeader.vue';
import TableToolbar from './TableToolbar.vue';
import TableCell from './TableCell.vue';
import TablePagination from './TablePagination.vue';

import { useStore } from '../../store/index';
import { getTableSchema } from '../../schemas/tables/index';
import { useTableData } from '../../composables/table/useTableData';
import { useTablePagination } from '../../composables/table/useTablePagination';
import { useTableSorting } from '../../composables/table/useTableSorting';
import { useTableSelection } from '../../composables/table/useTableSelection';
import { useTableFilters } from '../../composables/table/useTableFilters';
import { useTableColumns } from '../../composables/table/useTableColumns';

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

const userStore = useUserStore();

const namePlural = computed(() => (route.params.model || '').toString());
const schema = computed(() => getTableSchema(namePlural.value));
const store = computed(() => useStore(schema.value.store));

const { rows, totalRecords, loading, error, loadRows } = useTableData(schema, store);

const {
    first,
    rowsPerPage,
    pageSizeOptions,
    totalPages,
    currentPage,
    startItem,
    endItem,
    pagesWindow,
    goFirst,
    goPrev,
    goNext,
    goLast,
    goToPage,
    onPageSizeChange,
    resetPagination
} = useTablePagination(schema, totalRecords, loadData);

const {
    sortField,
    sortOrder,
    toggleSort,
    ariaSortFor,
    resetSorting
} = useTableSorting(schema, resetPagination, loadData);

const {
    selectedIds,
    isAllPageSelected,
    toggleSelectAllPage,
    toggleRowSelection,
    headerIndeterminate,
    clearSelection
} = useTableSelection(rows);

const {
    filters,
    searchValue,
    searchLoading,
    dateRange,
    extra,
    initFilters,
    onFilterDebounced,
    onSearchEnter,
    clearAll
} = useTableFilters(schema, resetPagination, loadData);

const { visibleCols } = useTableColumns(schema);

async function loadData() {
    const hasPermission = userStore.hasPermission(`view_${schema.value.id}`);
    if(!hasPermission) router.push('/home');
    await loadRows({
        rows: rowsPerPage.value,
        first: first.value,
        sortField: sortField.value,
        sortOrder: sortOrder.value,
        extra,
        searchValue: searchValue.value,
        dateRange: dateRange.value
    });
}

function handleQuickCreated({ item, payload }) {
    loadData();
}

function handleQuickError(err) {
    console.error('Quick create falhou:', err);
}

watch(
    () => route.params.model,
    () => {
        initFilters();
        resetPagination();
        resetSorting();
        clearSelection();
        loadData();
    }
);

onMounted(loadData);
</script>

<template>
    <div class="mx-auto h-full flex flex-col">
        <TableHeader :showAddButton="userStore.hasPermission(`add_${schema.id}`)"  :schema="schema" :modelname="schema.id" :dateRange="dateRange" :onDateChange="onFilterDebounced"
            @quick-created="handleQuickCreated" @quick-error="handleQuickError" />

        <TableToolbar v-model:searchValue="searchValue" :searchLoading="searchLoading" :onSearchEnter="onSearchEnter"
            :onClearAll="clearAll" />

        <div class="flex items-center flex-wrap gap-2 px-2 py-2 border-t border-zinc-200 dark:border-zinc-800">
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
                            <th v-if="schema.selection" scope="col"
                                class="px-2 py-2 text-left align-middle border-b border-zinc-200 dark:border-zinc-800">
                                <div class="flex items-center justify-start">
                                    <Checkbox class="mb-0.5 ml-0.5" size="small" binary
                                        :modelValue="isAllPageSelected()" :indeterminate="headerIndeterminate"
                                        @update:modelValue="toggleSelectAllPage" />
                                </div>
                            </th>

                            <th v-for="(col, i) in visibleCols" :key="'h-' + i" scope="col"
                                :aria-sort="ariaSortFor(col)"
                                class="px-3 py-2 border-b border-zinc-200 dark:border-zinc-800 text-[12px] font-semibold text-start text-zinc-700 dark:text-zinc-200 select-none">
                                <button v-if="col.sortable" type="button"
                                    class="inline-flex items-center gap-1 hover:text-zinc-900 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-zinc-300 dark:focus:ring-zinc-700 rounded"
                                    @click="toggleSort(col)">
                                    <span class="truncate">{{ col.header }}</span>
                                    <i :class="(col.sortField || col.field) === sortField
                                        ? (sortOrder === 1 ? 'pi pi-sort-amount-up' : 'pi pi-sort-amount-down')
                                        : 'pi pi-sort'" class="text-[10px] opacity-70" />
                                </button>
                                <span v-else class="truncate">{{ col.header }}</span>
                            </th>
                        </tr>
                    </thead>

                    <tbody>
                        <!-- Loading -->
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
                            class="cursor-pointer group/row">
                            <td v-if="schema.selection" :class="[
                                'px-2.5 pb-0.5 text-left align-middle transition-colors',
                                rIndex % 2 === 0 ? 'dark:bg-zinc-900' : 'dark:bg-zinc-950/20 bg-zinc-100',
                                'group-hover/row:bg-zinc-200 dark:group-hover/row:bg-zinc-800/60'
                            ]">
                                <div class="flex items-center justify-start">
                                    <Checkbox binary size="small" :modelValue="selectedIds.has(row.id)"
                                        @update:modelValue="() => toggleRowSelection(row.id)" />
                                </div>
                            </td>

                            <TableCell @click="() => router.push(`/${schema.id}/${row.id}/update`)"
                                v-for="(col, i) in visibleCols" :key="'c-' + rIndex + '-' + i" :column="col" :row="row"
                                :class="[
                                    rIndex % 2 === 0
                                        ? 'dark:bg-zinc-900'
                                        : 'dark:bg-zinc-950/20 bg-zinc-100',
                                    'transition-colors group-hover/row:bg-zinc-200 dark:group-hover/row:bg-zinc-800/60'
                                ]" />
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Paginação -->
        <TablePagination :startItem="startItem" :endItem="endItem" :totalRecords="totalRecords"
            :currentPage="currentPage" :totalPages="totalPages" :pagesWindow="pagesWindow" :rowsPerPage="rowsPerPage"
            :pageSizeOptions="pageSizeOptions" :goFirst="goFirst" :goPrev="goPrev" :goNext="goNext" :goLast="goLast"
            :goToPage="goToPage" :onPageSizeChange="onPageSizeChange" />
    </div>
</template>

<style scoped>
thead th {
    position: sticky;
    top: 0;
}

th>button:focus {
    outline: 2px solid rgb(212 212 216);
    outline-offset: 1px;
    border-radius: 0.375rem;
}
</style>
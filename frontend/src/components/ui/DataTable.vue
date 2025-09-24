<!-- src/components/ui/DataTables.vue -->
<script setup>
import { ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from "vue";
import Icon from "./Icon.vue";
import Tables from "./tables.vue";
import { useStore } from "../../store/index";
import { useRouter } from "vue-router";
import DateRangePicker from "flowbite-datepicker/DateRangePicker";
import ptBR from "../../../node_modules/flowbite-datepicker/js/i18n/locales/pt-BR";

const props = defineProps({
  model_name: { type: String, required: true },
  columns: { type: Array, default: () => [] },
  columnsLimit: { type: Number, default: 4 },
  initialSearch:   { type: String, default: "" },
  initialOrdering: { type: String, default: "" },
  initialPage:     { type: Number, default: 1 },
  initialPageSize: { type: Number, default: 10 },
  pageSizes:       { type: Array,  default: () => [10, 20, 50, 100] },
  autoFetch: { type: Boolean, default: true },
});

const emit = defineEmits(["row-click","error","created","updated"]);

const api = useStore(props.model_name);
const router = useRouter();

const search   = ref(props.initialSearch);
const ordering = ref(props.initialOrdering);
const page     = ref(props.initialPage);
const pageSize = ref(props.initialPageSize);
const total    = ref(0);
const rows     = ref([]);
const loading  = ref(false);
const errorMsg = ref("");

const visibleColumns = computed(() =>
  (props.columns || []).slice(0, Math.max(1, props.columnsLimit))
);

const selectedIds = ref(new Set());
const allChecked = computed(() => {
  const ids = (rows.value || []).map((r) => r?.id).filter(Boolean);
  return ids.length > 0 && ids.every((id) => selectedIds.value.has(id));
});
function onToggleAll(checked) {
  const ids = (rows.value || []).map((r) => r?.id).filter(Boolean);
  if (checked) selectedIds.value = new Set([...selectedIds.value, ...ids]);
  else {
    ids.forEach((id) => selectedIds.value.delete(id));
    selectedIds.value = new Set(selectedIds.value);
  }
}
function onToggleOne({ id, checked }) {
  if (!id) return;
  checked ? selectedIds.value.add(id) : selectedIds.value.delete(id);
  selectedIds.value = new Set(selectedIds.value);
}
function isRowSelected(id) {
  return selectedIds.value.has(id);
}

function isSorted(col) {
  const cur = ordering.value || "";
  return cur === col.key || cur === "-" + col.key;
}
function sortIcon(col) {
  if (!col?.sortable) return "none";
  const cur = ordering.value || "";
  if (cur === col.key) return "asc";
  if (cur === "-" + col.key) return "desc";
  return "none";
}
function toggleSort(col) {
  if (!col?.sortable) return;
  const cur = ordering.value || "";
  const key = col.key;
  let next = key;
  if (cur === key) next = "-" + key;
  else if (cur === "-" + key) next = "";
  ordering.value = next;
  page.value = 1;
}

const totalPages = computed(() =>
  Math.max(1, Math.ceil((total.value || 0) / (pageSize.value || 10)))
);
function setPage(p) {
  page.value = Math.min(Math.max(1, p), totalPages.value);
}
function prevPage() {
  if (page.value > 1) setPage(page.value - 1);
}
function nextPage() {
  if (page.value < totalPages.value) setPage(page.value + 1);
}
function changePageSize(e) {
  const val = Number(e?.target?.value || 10);
  pageSize.value = val;
  page.value = 1;
}
const showingStart = computed(() =>
  total.value === 0 ? 0 : (page.value - 1) * pageSize.value + 1
);
const showingEnd = computed(() =>
  Math.min(page.value * pageSize.value, total.value)
);

const internalSearch = ref(search.value);
watch(search, v => (internalSearch.value = v));
function submitSearch(e) {
  e?.preventDefault?.();
  search.value = (internalSearch.value || "").trim();
  page.value = 1;
}

const dateStart = ref(""); // yyyy-MM-dd
const dateEnd   = ref(""); // yyyy-MM-dd

let startPicker = null;
let endPicker   = null;
let drp = null;

const toISO = (d) => {
  if (!(d instanceof Date) || isNaN(d)) return "";
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const da = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${da}`;
};

const hasDate = computed(() => !!dateStart.value || !!dateEnd.value);

function clearDates() {
  dateStart.value = "";
  dateEnd.value = "";
  const start = document.getElementById("datepicker-range-start");
  const end   = document.getElementById("datepicker-range-end");
  if (start) start.value = "";
  if (end)   end.value   = "";
  page.value = 1;
  fetchList();
}

onMounted(() => {

  const container = document.getElementById("date-range-picker");
  if (!container) return;
  drp = new DateRangePicker(container, {
    language: "pt-BR",
    format: "dd/mm/yyyy",
  });

  const start = document.getElementById("datepicker-range-start");
  const end   = document.getElementById("datepicker-range-end");

  start?.addEventListener("changeDate", (ev) => {
    const d = ev?.detail?.date;
    dateStart.value = d ? toISO(d) : "";
    page.value = 1;
    fetchList();
  });

  end?.addEventListener("changeDate", (ev) => {
    const d = ev?.detail?.date;
    dateEnd.value = d ? toISO(d) : "";
    page.value = 1;
    fetchList();
  });
});

onBeforeUnmount(() => {
  try { drp?.destroy?.(); } catch {}
  drp = null;
});

async function fetchList() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const params = buildQueryParams();
    const resp = await api.list(params);
    rows.value  = resp?.rows ?? resp?.items ?? resp?.data ?? [];
    total.value = Number(resp?.count ?? resp?.total ?? 0);
    selectedIds.value = new Set();
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || "Falha ao listar";
    errorMsg.value = msg;
    emit("error", msg);
  } finally {
    loading.value = false;
  }
}

watch([search, ordering, page, pageSize], () => {
  if (props.autoFetch) fetchList();
}, { immediate: true });

function goToCreate() { router.push(`/${props.model_name}/create`); }
function goToEdit(id) { router.push(`/${props.model_name}/update/${id}`); }

function buildQueryParams() {
  const params = {
    limit:  pageSize.value,
    offset: Math.max(0, (page.value - 1) * pageSize.value),
  };
  if ((search.value || "").trim()) params.search = search.value.trim();
  if ((ordering.value || "").trim()) params.order_by = ordering.value.trim();

  if (dateStart.value) params.start_date = dateStart.value; // YYYY-MM-DD
  if (dateEnd.value)   params.end_date   = dateEnd.value;   // YYYY-MM-DD

  return params;
}

defineExpose({
  refresh: fetchList,
  createRow: (payload) => api.create(payload).then(fetchList),
  updateRow: (id, payload) => api.update(id, payload).then(fetchList),
});
</script>

<template>
  <div class="relative overflow-x-auto custom-scroll sm:rounded-lg">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between py-4">
      <form class="w-full sm:w-auto flex flex-wrap items-center gap-2" @submit.prevent="submitSearch">
        <!-- Busca -->
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
            <Icon name="search" size="18px" class="text-gray-500 dark:text-gray-400" />
          </div>
          <input
            id="table-search"
            type="text"
            :value="internalSearch"
            @input="internalSearch = $event.target.value"
            class="block w-full sm:w-64 px-3 py-1.5 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg
                   bg-gray-50 focus:ring-blue-500 focus:border-blue-500
                   dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
            placeholder="Procurar..."
            aria-label="Pesquisar na tabela"
          />
        </div>

        <div id="date-range-picker" date-rangepicker class="flex items-center">
          <div class="relative">
            <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
              <Icon name="date_range" size="16px" class="text-gray-500 dark:text-gray-400" />
            </div>
            <input
              id="datepicker-range-start"
              name="start"
              type="text"
              placeholder="Data inicial"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
                    focus:ring-blue-500 focus:border-blue-500 block w-10 ps-8 p-1.5
                    dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
                    dark:focus:ring-blue-500 dark:focus:border-blue-500"
            />
          </div>
          <div class="relative">
            <input
              id="datepicker-range-end"
              name="end"
              type="hidden"
              placeholder="Data final"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
                    focus:ring-blue-500 focus:border-blue-500 block w-40 ps-8 p-1.5
                    dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
                    dark:focus:ring-blue-500 dark:focus:border-blue-500"
            />
          </div>
        </div>
        <button
          v-if="hasDate"
          type="button"
          @click="clearDates"
          class="inline-flex cursor-pointer hover:text-white items-center text-gray-900 bg-white border border-gray-300
                 hover:bg-red-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-200
                 font-medium dark:bg-gray-800 dark:text-white dark:border-gray-600 
                 rounded-lg text-[12px] gap-1 px-3 py-1.5"
        >
          <Icon name="close" size="14px" />
          <span>Limpar</span>
        </button>
      </form>

      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="goToCreate"
          class="inline-flex cursor-pointer items-center gap-2 text-gray-900 bg-white border border-gray-300
                 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-200
                 font-medium dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700
                 rounded-lg text-sm px-3 py-1.5"
        >
          <Icon name="add" size="16px" />
          <span>Adicionar</span>
        </button>
      </div>
    </div>

    <!-- Tabela -->
    <Tables
      :columns="visibleColumns"
      :rows="rows"
      :loading="loading"
      :ordering="ordering"
      :allChecked="allChecked"
      :isRowSelected="isRowSelected"
      :isSorted="isSorted"
      :sortIcon="sortIcon"
      @toggle-all="onToggleAll"
      @toggle-one="onToggleOne"
      @toggle-sort="toggleSort"
      @row-click="$emit('row-click', $event)"
    >
      <template #row-actions="{ row }">
        <button
          type="button"
          @click="goToEdit(row.id)"
          title="Editar"
          aria-label="Editar"
          class="inline-flex items-center gap-2 text-gray-900 bg-white border border-gray-300
                 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-200
                 font-medium dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700
                 rounded-lg text-sm p-1.5 cursor-pointer"
        >
          <Icon name="edit" size="14px" />
        </button>
      </template>
    </Tables>

    <!-- Paginação -->
    <nav class="flex items-center flex-col md:flex-row justify-between px-2 py-4 dark:border-gray-700" aria-label="Table navigation">
      <div class="flex items-center gap-3 mb-4 md:mb-0">
        <span class="text-sm font-normal text-gray-600 dark:text-gray-400">
          Mostrando
          <span class="font-semibold text-gray-900 dark:text-gray-100">{{ showingStart }}-{{ showingEnd }}</span>
          de
          <span class="font-semibold text-gray-900 dark:text-gray-100">{{ total }}</span>
        </span>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">Mostrar</span>
          <select
            :value="pageSize"
            @change="changePageSize"
            class="border border-gray-300 rounded-lg py-1.5 text-sm bg-white
                   focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                   dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100"
          >
            <option v-for="n in pageSizes" :key="n" :value="n">{{ n }}</option>
          </select>
          <span class="text-sm text-gray-600 dark:text-gray-400">por página</span>
        </div>
      </div>

      <ul class="inline-flex -space-x-px rtl:space-x-reverse text-sm h-9">
        <li>
          <button
            type="button"
            @click="prevPage"
            :disabled="page <= 1"
            class="flex items-center justify-center px-3 h-9 leading-tight text-gray-600 bg-white border mr-1
                   border-gray-300 rounded-l-lg hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700
                   dark:text-gray-300 cursor-pointer dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Anterior
          </button>
        </li>
        <li v-for="p in totalPages" :key="p">
          <button
            type="button"
            @click="setPage(p)"
            :aria-current="p === page ? 'page' : undefined"
            :class="[
              'flex items-center justify-center px-3 h-9 leading-tight border',
              p === page
                ? 'text-gray-700 cursor-default border-gray-300 bg-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100'
                : 'text-gray-600 cursor-pointer bg-white border-gray-300 hover:bg-gray-50 hover:text-gray-800 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-700'
            ]"
          >
            {{ p }}
          </button>
        </li>
        <li>
          <button
            type="button"
            @click="nextPage"
            :disabled="page >= totalPages"
            class="flex items-center cursor-pointer justify-center px-3 h-9 leading-tight text-gray-600 bg-white border ml-1
                   border-gray-300 rounded-e-lg hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700
                   dark:text-gray-300 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Próximo
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import TableCell from "../../tables/TableCell.vue";
import Menu from "primevue/menu";

const props = defineProps({
  label: String,
  modelValue: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  contextId: { type: [String, Number, null], default: null },
  rows: { type: Function, default: null },

  showEdit: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  pkField: { type: String, default: "id" },
  loading: { type: Boolean, default: false },

  // paginação
  pageSize: { type: Number, default: 5 },
});

const emit = defineEmits(["update:modelValue", "edit"]);
const toast = useToast?.();

const isServer = computed(() => typeof props.rows === "function");

// ----- STATE -----
const localItems = ref([...(props.modelValue || [])]); // client-mode data
watch(() => props.modelValue, (v) => (localItems.value = [...(v || [])]));

const serverItems = ref([]);      // server-mode page data
const totalRecords = ref(0);      // server-mode total
const isFetching   = ref(false);

// paginação
const currentPage = ref(1);
const pageSize = computed(() => Math.max(1, props.pageSize || 5));
const totalPages = computed(() => {
  const tot = isServer.value ? totalRecords.value : localItems.value.length;
  return Math.max(1, Math.ceil(tot / pageSize.value));
});

// client-mode paginação
const startIdx = computed(() => (currentPage.value - 1) * pageSize.value);
const endIdx   = computed(() => Math.min(startIdx.value + pageSize.value, (isServer.value ? totalRecords.value : localItems.value.length)));
const displayedItems = computed(() => {
  if (isServer.value) return serverItems.value; // já vem paginado
  return localItems.value.slice(startIdx.value, endIdx.value);
});

watch([() => totalRecords.value, () => localItems.value.length], () => {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value;
});

async function fetchServerPage(page = 1) {
  if (!isServer.value) return;
  isFetching.value = true;
  try {
    const limit = pageSize.value;
    const offset = (page - 1) * limit;
    const resp = await props.rows?.(props.contextId, { limit, offset, page });
    const arr  = Array.isArray(resp) ? resp : (resp?.items || resp?.rows || []);
    const tot  = typeof resp?.total === "number" ? resp.total : (Array.isArray(resp) ? resp.length : (arr?.length ?? 0));
    serverItems.value = arr || [];
    totalRecords.value = Math.max(0, tot);
    currentPage.value = page;
  } catch (e) {
    console.error("[FieldRelationTable] fetch error:", e);
    toast?.add?.({ severity: "error", summary: "Erro ao carregar", life: 2000 });
  } finally {
    isFetching.value = false;
  }
}

watch(() => props.contextId, () => {
  if (isServer.value) fetchServerPage(1);
});

onMounted(() => {
  if (isServer.value) fetchServerPage(1);
});

// trocar página
function goFirst() { if (currentPage.value !== 1) fetchServerPage(1); else currentPage.value = 1; }
function goPrev()  { if (currentPage.value > 1)  isServer.value ? fetchServerPage(currentPage.value - 1) : currentPage.value--; }
function goNext()  { if (currentPage.value < totalPages.value) isServer.value ? fetchServerPage(currentPage.value + 1) : currentPage.value++; }
function goLast()  { if (currentPage.value !== totalPages.value) isServer.value ? fetchServerPage(totalPages.value) : (currentPage.value = totalPages.value); }
function goToPage(p) {
  const page = Math.min(Math.max(1, p), totalPages.value);
  isServer.value ? fetchServerPage(page) : (currentPage.value = page);
}

// janela de páginas (até 7 botões)
const pagesWindow = computed(() => {
  const maxBtns = 7;
  const total = totalPages.value;
  const cur = currentPage.value;
  let start = Math.max(1, cur - Math.floor(maxBtns / 2));
  let end = Math.min(total, start + maxBtns - 1);
  if (end - start + 1 < maxBtns) start = Math.max(1, end - maxBtns + 1);
  const arr = [];
  for (let p = start; p <= end; p++) arr.push(p);
  return arr;
});

// menu de opções
const menuRefs = ref(new Map());
function setMenuRef(id, el) {
  if (!menuRefs.value) menuRefs.value = new Map();
  if (el) menuRefs.value.set(id, el);
  else menuRefs.value.delete(id);
}
function toggleMenu(event, row) {
  const id = row?.[props.pkField];
  const menu = menuRefs.value.get(id);
  menu?.toggle(event);
}
function removeItem(row) {
  const pk = props.pkField;
  const id = row?.[pk];

  if (isServer.value) {
    // em modo server, removemos apenas visualmente da página (ou você pode emitir um evento para o pai remover no backend)
    serverItems.value = serverItems.value.filter((it) => it?.[pk] !== id);
    // opcional: atualizar total local
    totalRecords.value = Math.max(0, totalRecords.value - 1);
  } else {
    const next = localItems.value.filter((it) => it?.[pk] !== id);
    localItems.value = next;
    emit("update:modelValue", next);
  }

  toast?.add?.({ severity: "success", summary: "Removido", life: 1200 });
}
function editItem(row) {
  emit("edit", row);
}
function buildMenuItems(row) {
  const actions = [];
  if (props.showEdit) actions.push({ label: "Editar", icon: "pi pi-pencil", command: () => editItem(row) });
  actions.push({ label: "Remover", icon: "pi pi-trash", command: () => removeItem(row) });
  return actions;
}

// colunas
const effectiveColumns = computed(() => Array.isArray(props.columns) ? props.columns.slice() : []);
const visibleColsCount = computed(() => (effectiveColumns.value?.length || 0) + 1);

// recarregar
function reload() {
  if (isServer.value) fetchServerPage(currentPage.value);
}
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <label v-if="label" class="block text-[12px] font-medium mb-1">{{ label }}</label>

      <div class="flex items-center gap-2">
        <Button
          v-if="rows"
          label="Recarregar"
          icon="pi pi-refresh"
          size="small"
          text
          :loading="isFetching"
          :disabled="disabled || isFetching"
          @click="reload"
        />
      </div>
    </div>

    <div class="overflow-auto rounded-md border border-zinc-200 dark:border-zinc-800">
      <table class="min-w-full text-[13px]">
        <thead>
          <tr class="bg-zinc-200/50 dark:bg-zinc-800 sticky top-0 z-10">
            <th
              v-for="col in effectiveColumns"
              :key="col.field || col.header || col.type"
              :style="col.width ? { width: col.width } : null"
              class="px-3 py-2 text-left font-semibold text-zinc-700 dark:text-zinc-200"
            >
              {{ col.header || col.label || '' }}
            </th>
            <th class="px-3 py-2 text-left font-semibold text-zinc-700 dark:text-zinc-200" style="width: 60px;">
              Opções
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- Loading -->
          <tr v-if="loading || isFetching">
            <td :colspan="visibleColsCount" class="px-4 py-8 text-center text-zinc-500">
              Carregando...
            </td>
          </tr>

          <!-- Vazio -->
          <tr v-else-if="displayedItems.length === 0">
            <td :colspan="visibleColsCount" class="px-4 py-4 text-center text-zinc-500">
              Nenhum registro encontrado.
            </td>
          </tr>

          <!-- Linhas (mesmo design da DataTable) -->
          <tr
            v-else
            v-for="(row, rIndex) in displayedItems"
            :key="row?.[pkField] ?? rIndex"
            class="cursor-pointer group/row"
          >
            <TableCell
              v-for="col in effectiveColumns"
              :key="(col.field || col.header || col.type) + '-' + (row?.[pkField] ?? rIndex)"
              :column="col"
              :row="row"
              :class="[
                (rIndex % 2 === 0)
                  ? 'dark:bg-zinc-900'
                  : 'dark:bg-zinc-950/20 bg-zinc-100',
                'transition-colors group-hover/row:bg-zinc-200 dark:group-hover/row:bg-zinc-800/60'
              ]"
            />
            <td
              class="px-1 py-1.5"
              :class="[
                (rIndex % 2 === 0)
                  ? 'dark:bg-zinc-900'
                  : 'dark:bg-zinc-950/20 bg-zinc-100',
                'transition-colors group-hover/row:bg-zinc-200 dark:group-hover/row:bg-zinc-800/60'
              ]"
            >
              <Button
                icon="pi pi-ellipsis-v"
                text
                rounded
                size="small"
                :disabled="disabled"
                @click="(e) => toggleMenu(e, row)"
              />
              <Menu :model="buildMenuItems(row)" popup :ref="(el) => setMenuRef(row?.[pkField], el)" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação -->
    <div class="flex items-center justify-between gap-3 py-3 px-3 bg-white dark:bg-zinc-900 border-t border-zinc-200 dark:border-zinc-800">
      <div class="text-xs text-zinc-600 dark:text-zinc-400">
        <template v-if="isServer">
          Mostrando <b>{{ (currentPage - 1) * pageSize + 1 }}</b>–<b>{{ Math.min(currentPage * pageSize, totalRecords) }}</b> de <b>{{ totalRecords }}</b>
        </template>
        <template v-else>
          Mostrando <b>{{ startIdx + 1 }}</b>–<b>{{ endIdx }}</b> de <b>{{ localItems.length }}</b>
        </template>
      </div>

      <nav class="flex items-center gap-1 text-sm">
        <i class="pi pi-angle-double-left p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
           :class="{ 'pointer-events-none opacity-40': currentPage === 1 }"
           @click="goFirst()" title="Primeira página" />
        <i class="pi pi-angle-left p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
           :class="{ 'pointer-events-none opacity-40': currentPage === 1 }"
           @click="goPrev()" title="Página anterior" />

        <button
          v-for="p in pagesWindow"
          :key="'p-' + p"
          @click="goToPage(p)"
          :aria-current="p === currentPage ? 'page' : undefined"
          class="h-7 w-7 rounded-full grid place-items-center text-xs transition"
          :class="p === currentPage
            ? 'bg-zinc-800 text-zinc-100 dark:bg-zinc-100 dark:text-zinc-900 font-semibold'
            : 'text-zinc-300 hover:bg-zinc-800/60'"
        >
          {{ p }}
        </button>

        <i class="pi pi-angle-right p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
           :class="{ 'pointer-events-none opacity-40': currentPage === totalPages }"
           @click="goNext()" title="Próxima página" />
        <i class="pi pi-angle-double-right p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
           :class="{ 'pointer-events-none opacity-40': currentPage === totalPages }"
           @click="goLast()" title="Última página" />
      </nav>
    </div>
  </div>
</template>

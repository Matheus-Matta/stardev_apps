<script setup>
const props = defineProps({
  startItem: Number,
  endItem: Number,
  totalRecords: Number,
  currentPage: Number,
  totalPages: Number,
  pagesWindow: Array,
  rowsPerPage: Number,
  pageSizeOptions: Array,
  goFirst: Function,
  goPrev: Function,
  goNext: Function,
  goLast: Function,
  goToPage: Function,
  onPageSizeChange: Function
});

function handlePageSizeChange(e) {
  const newSize = Number(e.target.value);
  props.onPageSizeChange(newSize);
}
</script>

<template>
  <div class="flex items-center justify-between gap-3 py-3 px-3 bg-white dark:bg-zinc-900 border-t border-zinc-200 dark:border-zinc-800">
    <!-- Contador de itens -->
    <div class="text-xs text-zinc-600 dark:text-zinc-400">
      Mostrando <b>{{ startItem }}</b>–<b>{{ endItem }}</b> de <b>{{ totalRecords }}</b>
    </div>

    <!-- Navegação de páginas -->
    <nav class="flex items-center gap-1 text-sm">
      <i
        class="pi pi-angle-double-left p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
        :class="{ 'pointer-events-none opacity-40': currentPage === 1 }"
        @click="currentPage !== 1 && goFirst()"
        aria-label="Primeira página"
        title="Primeira página"
      />
      
      <i
        class="pi pi-angle-left p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
        :class="{ 'pointer-events-none opacity-40': currentPage === 1 }"
        @click="currentPage !== 1 && goPrev()"
        aria-label="Página anterior"
        title="Página anterior"
      />

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

      <i
        class="pi pi-angle-right p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
        :class="{ 'pointer-events-none opacity-40': currentPage === totalPages }"
        @click="currentPage !== totalPages && goNext()"
        aria-label="Próxima página"
        title="Próxima página"
      />
      
      <i
        class="pi pi-angle-double-right p-1.5 rounded-full text-zinc-400 hover:bg-zinc-700/50 cursor-pointer"
        :class="{ 'pointer-events-none opacity-40': currentPage === totalPages }"
        @click="currentPage !== totalPages && goLast()"
        aria-label="Última página"
        title="Última página"
      />
    </nav>

    <!-- Seletor de tamanho de página -->
    <div class="ml-2">
      <div class="relative">
        <select
          :value="rowsPerPage"
          @change="handlePageSizeChange"
          class="h-7 pl-2 pr-7 rounded-md bg-white text-zinc-700 border border-zinc-300
                 dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700
                 text-xs focus:outline-none focus:ring-2 focus:ring-zinc-300 dark:focus:ring-zinc-700"
          aria-label="Itens por página"
          title="Itens por página"
        >
          <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">
            {{ opt }}
          </option>
        </select>
        <span class="pointer-events-none absolute inset-y-0 right-1 grid place-items-center text-zinc-400 text-[10px]">
          ▾
        </span>
      </div>
    </div>
  </div>
</template>
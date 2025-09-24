<script setup lang="ts">
import Icon from "../ui/Icon.vue";

type Column = {
  key: string;
  label: string;
  width?: string;
  sortable?: boolean;
  formatter?: (val: any, row: any) => any;
};

const props = defineProps<{
  columns: Column[];
  rows: any[];
  loading: boolean;
  ordering: string;

  allChecked: boolean;
  isRowSelected: (id: string | number) => boolean;
  isSorted: (col: Column) => boolean;
  sortIcon: (col: Column) => "asc" | "desc" | "none";
}>();

const emit = defineEmits<{
  (e: "toggle-all", checked: boolean): void;
  (e: "toggle-one", payload: { id: string | number; checked: boolean }): void;
  (e: "toggle-sort", col: Column): void;
  (e: "row-click", row: any): void;
}>();
</script>

<template>
  <div class="relative overflow-x-auto shadow-md sm:rounded-t-lg custom-scroll">
    <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
      <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
        <tr>
          <th scope="col" class="p-3 w-12">
            <label class="flex items-center gap-2">
              <input
                id="checkbox-all-search"
                type="checkbox"
                :checked="allChecked"
                @change="$emit('toggle-all', ($event.target as HTMLInputElement).checked)"
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded
                       focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600
                       dark:ring-offset-gray-800 dark:bg-gray-700 dark:border-gray-600"
                :aria-checked="allChecked ? 'true' : 'false'"
                aria-label="Selecionar todos"
              />
            </label>
          </th>

          <th
            v-for="c in columns"
            :key="c.key"
            scope="col"
            class="px-4 py-3 select-none"
            :class="c.width || ''"
            :aria-sort="ordering === c.key ? 'ascending' : (ordering === '-' + c.key ? 'descending' : 'none')"
          >
            <button
              v-if="c.sortable"
              type="button"
              @click="$emit('toggle-sort', c)"
              :title="'Ordenar por ' + c.label"
              :class="[
                'inline-flex items-center gap-1 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors',
                isSorted(c) ? 'text-blue-600 dark:text-blue-300'
                            : 'hover:text-blue-500 hover:dark:text-white'
              ]"
            >
              <span class="font-semibold">{{ c.label }}</span>
              <Icon v-if="sortIcon(c) === 'asc'"  name="keyboard_arrow_up"   size="16px" class="opacity-70" />
              <Icon v-else-if="sortIcon(c) === 'desc'" name="keyboard_arrow_down" size="16px" class="opacity-70" />
              <Icon v-else name="unfold_more" size="16px" class="opacity-50" />
            </button>
            <span v-else class="font-semibold">{{ c.label }}</span>
          </th>

          <th scope="col" class="pr-3 py-3 text-right pe-6">Ações</th>
        </tr>
      </thead>

      <tbody>
        <!-- Loading -->
        <tr v-if="loading">
          <td :colspan="columns.length + 2" class="px-6 py-10 text-center text-gray-500 dark:text-gray-400">
            Carregando…
          </td>
        </tr>

        <!-- Empty -->
        <tr v-else-if="rows.length === 0">
          <td :colspan="columns.length + 2" class="px-6 py-10 text-center">
            <div class="flex flex-col items-center gap-2">
              <Icon name="inbox" size="28px" class="text-gray-400 dark:text-gray-500" />
              <p class="text-sm text-gray-600 dark:text-gray-400">Nenhum registro encontrado.</p>
            </div>
          </td>
        </tr>

        <!-- Rows -->
        <tr
          v-else
          v-for="row in rows"
          :key="row.id"
          class="odd:bg-white even:bg-gray-50 dark:odd:bg-gray-900 dark:even:bg-gray-800
                 border-b border-gray-200 dark:border-gray-700
                 hover:bg-gray-100 dark:hover:bg-gray-700/60 transition-colors"
        >
          <td class="px-3 py-2 w-12">
            <label class="flex items-center gap-2">
              <input
                :id="'checkbox-' + row.id"
                type="checkbox"
                :checked="isRowSelected(row.id)"
                @change="$emit('toggle-one', { id: row.id, checked: ($event.target as HTMLInputElement).checked })"
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded
                       focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600
                       dark:ring-offset-gray-800 dark:bg-gray-700 dark:border-gray-600"
                :aria-label="`Selecionar linha ${row.id}`"
              />
            </label>
          </td>

          <td
            v-for="c in columns"
            :key="c.key"
            class="px-3 py-2 text-gray-900 dark:text-gray-100 cursor-pointer"
            @click="$emit('row-click', row)"
          >
            <span class="block truncate">
              {{ typeof c.formatter === "function" ? c.formatter(row[c.key], row) : row[c.key] }}
            </span>
          </td>

          <td class="px-3 py-2 pe-2 text-right">
            <!-- Slot para ações da linha -->
            <slot name="row-actions" :row="row" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

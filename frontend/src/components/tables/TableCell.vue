<script setup>
import { computed } from 'vue';

const props = defineProps({
  column: { type: Object, required: true },
  row: { type: Object, required: true }
});

// util para nested props: "a.b.c"
function get(obj, path, def = null) {
  if (!path) return def;
  return String(path)
    .split('.')
    .reduce((acc, k) => (acc && acc[k] != null ? acc[k] : def), obj);
}

// formatação padrão para datas quando não houver column.format
function formatDateCell(val) {
  if (!val) return '';
  const d = new Date(val);
  if (isNaN(d)) return String(val);
  return d.toLocaleDateString('pt-BR');
}

// valor bruto (antes de qualquer format)
const rawValue = computed(() => get(props.row, props.column.field));

// valor exibido (aplica column.format, se houver)
const displayValue = computed(() => {
  const v = rawValue.value;
  return typeof props.column.format === 'function'
    ? props.column.format(v, props.row)
    : v;
});

// resolve severidade da Tag preferindo mapear pelo valor bruto (ex.: boolean)
// e caindo para o valor formatado se necessário
function resolveSeverity(map, raw, disp) {
  if (!map) return null;

  // 1) chave direta pelo valor bruto
  if (raw in map) return map[raw];

  // 2) chave pelo bruto como string (ex.: "true"/"false")
  const rawStr = (raw !== null && raw !== undefined && typeof raw !== 'object')
    ? String(raw)
    : null;
  if (rawStr && rawStr in map) return map[rawStr];

  // 3) chave pelo valor exibido (formatado)
  if (disp in map) return map[disp];

  return null;
}

const tagSeverity = computed(() => resolveSeverity(props.column.severityMap, rawValue.value, displayValue.value));

// valor numérico para ProgressBar (aplica format caso exista, depois tenta converter)
const progressValue = computed(() => {
  const v = (typeof props.column.format === 'function') ? displayValue.value : rawValue.value;
  const num = Number(v);
  return Number.isFinite(num) ? num : 0;
});
</script>

<template>
  <!-- Texto padrão -->
  <td v-if="!column.type || column.type === 'text'" class="px-3 py-1.5 truncate">
    {{ displayValue }}
  </td>

  <!-- Avatar + Texto (usa column.text se existir; senão cai para displayValue) -->
  <td v-else-if="column.type === 'avatarText'" class="px-3 py-1.5">
    <div class="flex items-center gap-2">
      <img :src="column.avatar?.(row)" alt="" class="h-6 w-6 rounded-full object-cover" />
      <span class="truncate">
        {{ typeof column.text === 'function' ? column.text(row) : displayValue }}
      </span>
    </div>
  </td>

  <!-- Imagem (src pode ser transformado por column.format) -->
  <td v-else-if="column.type === 'image'">
    <img :src="displayValue || ''" alt="" class="h-8 w-8 rounded object-cover" />
  </td>

  <!-- Tag (label usa displayValue; severidade mapeada a partir do rawValue, com fallback) -->
  <td v-else-if="column.type === 'tag'" class="px-3 py-1.5">
    <Tag size="small" :value="displayValue" :severity="tagSeverity" :pt="{
      label: { class: 'text-[12px] font-medium' },
      root: { class: 'rounded-full p-0 px-2 pt-0.5' }
    }" />
  </td>

  <!-- Data (usa column.format se fornecido; senão formatação padrão) -->
  <td v-else-if="column.type === 'date'" class="px-3 py-1.5">
    {{ typeof column.format === 'function' ? displayValue : formatDateCell(rawValue) }}
  </td>

  <!-- Moeda (ou valor qualquer com format; se não houver format, mostra raw) -->
  <td v-else-if="column.type === 'currency'" class="px-3 py-1.5">
    {{ displayValue }}
  </td>

  <!-- Progresso (tenta converter displayValue/raw para número) -->
  <td v-else-if="column.type === 'progress'" class="px-3 py-1.5">
    <ProgressBar :value="progressValue" :showValue="false" style="height: 6px" />
  </td>

  <!-- Ações -->
  <td v-else-if="column.type === 'actions'" class="px-3 py-1.5">
    <div class="flex justify-start gap-1">
      <Button v-for="(act, idx) in column.actions" :key="idx" :icon="act.icon || 'pi pi-cog'"
        :rounded="act.rounded ?? true" size="small" @click="() => act.onClick?.(row)" />
    </div>
  </td>
</template>

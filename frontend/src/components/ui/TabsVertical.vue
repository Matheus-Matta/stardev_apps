<script setup>
/**
 * Abas verticais com menu à esquerda e conteúdo à direita.
 * Uso:
 *  <TabsVertical :items="[{key:'profile',label:'Meu Perfil',icon:'person'}]" v-model="tab">
 *    <template #panel-profile> ... </template>
 *  </TabsVertical>
 */
import Icon from "./Icon.vue";

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
    // item: { key: string, label: string, icon?: string, badge?: string }
  },
  modelValue: { type: String, default: "" }, // aba ativa
  class: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

function select(key) {
  if (key && key !== props.modelValue) emit("update:modelValue", key);
}
</script>

<template>
  <div
    :class="[
      'rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
      'grid grid-cols-1 lg:grid-cols-12',
      props.class,
    ]"
  >
    <!-- MENU ESQUERDA (unido) -->
    <aside
      class="lg:col-span-2 border-b lg:border-b-0 lg:border-r border-gray-200 dark:border-gray-700"
    >
      <ul class="p-2">
        <li v-for="it in items" :key="it.key" class="mb-2">
          <button
            type="button"
            class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium
                   hover:bg-gray-200 cursor-pointer dark:hover:bg-gray-700 transition-colors"
            :class="it.key === modelValue
              ? 'bg-gray-100 dark:bg-gray-700/60 text-gray-700 dark:text-gray-200'
              : 'text-gray-700 dark:text-gray-200'"
            @click="select(it.key)"
          >
            <Icon v-if="it.icon" :name="it.icon" class="text-[18px]" />
            <span class="truncate">{{ it.label }}</span>
            <span v-if="it.badge"
                  class="ml-auto text-[11px] px-1.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
              {{ it.badge }}
            </span>
          </button>
        </li>
      </ul>
    </aside>

    <!-- CONTEÚDO DIREITA -->
    <section class="lg:col-span-10 p-4 md:p-6">
      <!-- Renderiza o painel da aba ativa via named slot: panel-<key> -->
      <slot :name="`panel-${modelValue}`"></slot>
    </section>
  </div>
</template>

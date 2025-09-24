<script setup>
import { computed } from "vue"
import { FwbButton } from "flowbite-vue"
import Icon from "./Icon.vue"

const props = defineProps({
  editing: { type: Boolean, default: false },   // estado atual
  saving:  { type: Boolean, default: false },   // estado de loading
  form:    { type: String,  default: "" },      // id do form para o botão salvar (submit externo)
  size:    { type: String,  default: "sm" },    // passa para FwbButton
  showEdit:   { type: Boolean, default: true }, // permite esconder o botão Editar (ex.: sem permissão)
  showCancel: { type: Boolean, default: true }, // idem
  showSave:   { type: Boolean, default: true }, // idem
  // labels customizáveis
  editLabel:   { type: String, default: "Editar" },
  cancelLabel: { type: String, default: "Cancelar" },
  saveLabel:   { type: String, default: "Salvar" },
  // cores (Flowbite)
  editColor:   { type: String, default: "light" },
  cancelColor: { type: String, default: "light" },
  saveColor:   { type: String, default: "green" },
})

const emit = defineEmits(["edit", "cancel", "save"])

// acessibilidade
const ariaBusy = computed(() => (props.saving ? "true" : "false"))
</script>

<template>
  <div class="flex gap-2">
    <!-- Modo visualizar -->
    <FwbButton
      v-if="!editing && showEdit"
      :size="size"
      :color="editColor"
      class="flex items-center gap-2 cursor-pointer hover:dark:bg-gray-700 hover:bg-gray-200 rounded-xl"
      @click="$emit('edit')"
    >
      <Icon name="edit" size="14px" class="mr-1"/>
      <span>{{ editLabel }}</span>
    </FwbButton>

    <!-- Modo edição -->
    <template v-else>
      <FwbButton
        v-if="showCancel"
        :size="size"
        :color="cancelColor"
        :disabled="saving"
        @click="$emit('cancel')"
        :aria-busy="ariaBusy"
        class="flex items-center gap-2 cursor-pointer hover:dark:bg-gray-700 hover:bg-gray-200 rounded-xl"
        type="button"
      >
        <Icon name="close" size="14px" class="mr-1" />
        <span>{{ cancelLabel }}</span>
      </FwbButton>

      <FwbButton
        v-if="showSave"
        :size="size"
        :color="saveColor"
        :disabled="saving"
        :aria-busy="ariaBusy"
        class="flex items-center gap-2 cursor-pointer hover:bg-green-700 rounded-xl"
        type="submit"
        :form="form || null"
        @click="$emit('save')"
      >
        <Icon name="check" size="14px" class="mr-1" />
        <span>{{ saveLabel }}</span>
      </FwbButton>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  label: String,
  modelValue: [String, Number, Object],
  options: { type: Array, default: () => [] },
  loading: Boolean,
  placeholder: String,
  disabled: Boolean,
  emptyMessage: { type: String, default: 'Nenhum resultado' },
  editable: { type: Boolean, default: true },
  pt: Object,
  iconLeft: String,
  iconRight: String,
  addonLeft: String,
  addonRight: String,
  showAdd: { type: Boolean, default: false },
  addLabel: { type: String, default: 'Adicionar' },
  addIcon: { type: String, default: 'pi pi-plus' },
})

const emit = defineEmits(['update:modelValue','blur','focus','show','hide','add','search'])

const hasGroup = !!(props.iconLeft || props.iconRight || props.addonLeft || props.addonRight)
const labelName = props?.label?.toLowerCase?.().replace(/\s+/g, '_') || 'field'

function onSearch(e){ emit('search', e) }

const overlayOpen = ref(false)
function onShow(){ overlayOpen.value = true; emit('show') }
function onHide(){ overlayOpen.value = false; emit('hide') }

const hasSelection = computed(() => {
  const mv = props.modelValue
  const v = mv && typeof mv === 'object'
    ? ('value' in mv ? mv.value : ('id' in mv ? mv.id : null))
    : mv
  return v !== null && v !== undefined && String(v) !== ''
})

const isEditable = computed(() => props.editable && (!hasSelection.value || overlayOpen.value))
</script>

<template>
  <label v-if="label" class="block text-[12px] font-medium mb-1">{{ label }}</label>

  <template v-if="hasGroup">
    <InputGroup class="w-full">
      <InputGroupAddon v-if="iconLeft || addonLeft"
        class="dark:bg-zinc-800 bg-zinc-200 text-zinc-600 border-0 dark:text-zinc-400 rounded-l-lg">
        <i v-if="iconLeft" :class="iconLeft"></i>
        <span v-else>{{ addonLeft }}</span>
      </InputGroupAddon>

      <Select
        :modelValue="modelValue?.value"
        :name="labelName"
        :options="options"
        optionLabel="label"
        optionValue="value"
        size="small"
        :editable="isEditable"
        showClear
        :emptyMessage="loading ? 'Carregando...' : emptyMessage"
        :loading="!!loading"
        :placeholder="loading ? 'Loading...' : (placeholder || 'Selecione...')"
        class="w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950"
        :disabled="disabled"
        :pt="Object.assign({
          option: { class: 'py-1 text-[14px] font-medium' },
          emptyMessage: { class: 'text-[12px] text-center text-zinc-500 dark:text-zinc-400' },
          label: { onInput: onSearch, onKeyup: onSearch },
          dropdownIcon: { class: 'w-3 hover:text-zinc-900 dark:hover:text-zinc-100' },
          clearIcon: { class: 'w-3 hover:text-red-400' },
        }, pt)"
        @update:modelValue="$emit('update:modelValue', $event)"
        @show="onShow"
        @hide="onHide"
        @focus="$emit('focus')"
        @blur="$emit('blur')"
      >
        <template #footer v-if="showAdd">
          <div class="px-1 pb-1">
            <Button
              @click="$emit('add')"
              :label="addLabel"
              fluid
              severity="contrast"
              variant="text"
              size="small"
              :icon="addIcon"
              class="text-[12px] py-1 font-medium shadow-sm dark:shadow-zinc-950"
              :pt="{ icon: 'text-[8px]' }"
            />
          </div>
        </template>
      </Select>

      <InputGroupAddon v-if="iconRight || addonRight"
        class="dark:bg-zinc-800 bg-zinc-200 text-zinc-600 border-0 dark:text-zinc-400 rounded-r-lg">
        <i v-if="iconRight" :class="iconRight"></i>
        <span v-else>{{ addonRight }}</span>
      </InputGroupAddon>
    </InputGroup>
  </template>

  <template v-else>
    <Select
      :modelValue="modelValue?.value"
      :name="label"
      :options="options"
      optionLabel="label"
      optionValue="value"
      size="small"
      :editable="isEditable"
      showClear
      :emptyMessage="loading ? 'Carregando...' : emptyMessage"
      :loading="!!loading"
      :placeholder="loading ? 'Loading...' : (placeholder || 'Selecione...')"
      class="w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950"
      :disabled="disabled"
      :pt="Object.assign({
        option: { class: 'py-1 text-[14px] font-medium' },
        emptyMessage: { class: 'text-[12px] text-center text-zinc-500 dark:text-zinc-400' },
        label: { onInput: onSearch, onKeyup: onSearch },
        dropdownIcon: { class: 'w-3 hover:text-zinc-900 dark:hover:text-zinc-100' },
        clearIcon: { class: 'w-3 hover:text-red-400' },
      }, pt)"
      @update:modelValue="$emit('update:modelValue', $event)"
      @show="onShow"
      @hide="onHide"
      @focus="$emit('focus')"
      @blur="$emit('blur')"
    >
      <template #footer v-if="showAdd">
        <div class="px-1 pb-1">
          <Button
            @click="$emit('add')"
            :label="addLabel"
            fluid
            severity="contrast"
            variant="text"
            size="small"
            :icon="addIcon"
            class="text-[12px] py-1 font-medium shadow-sm dark:shadow-zinc-950"
            :pt="{ icon: 'text-[8px]', label: 'text-start' }"
          />
        </div>
      </template>
    </Select>
  </template>
</template>

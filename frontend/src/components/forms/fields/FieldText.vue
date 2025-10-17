<script setup>
import InputText from "primevue/inputtext";
import InputGroup from "primevue/inputgroup";
import InputGroupAddon from "primevue/inputgroupaddon";

const props = defineProps({
    label: String,
    modelValue: [String, Number],
    placeholder: String,
    disabled: Boolean,
    iconLeft: String,
    iconRight: String,
    addonLeft: String,
    addonRight: String,
    inputProps: Object,    
    keyfilter: [String, Object], 
});

const emit = defineEmits(["update:modelValue", "blur"]);

const hasGroup = !!(props.iconLeft || props.iconRight || props.addonLeft || props.addonRight);
const labelName = props?.label.toLowerCase().replace(/\s+/g, '_') || 'field';

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

            <InputText :modelValue="modelValue" :name="labelName" :placeholder="placeholder" size="small" :disabled="disabled"
                class="w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950"
                v-bind="inputProps" v-keyfilter="keyfilter" @update:modelValue="$emit('update:modelValue', $event)"
                @blur="$emit('blur')" />

            <InputGroupAddon v-if="iconRight || addonRight"
                class="dark:bg-zinc-800 bg-zinc-200 text-zinc-600 border-0 dark:text-zinc-400 rounded-r-lg">
                <i v-if="iconRight" :class="iconRight"></i>
                <span v-else>{{ addonRight }}</span>
            </InputGroupAddon>
        </InputGroup>
    </template>

    <template v-else>
        <InputText :modelValue="modelValue" :name="labelName" :placeholder="placeholder" size="small" :disabled="disabled"
            class="w-full focus:!ring-zinc-500 focus:!border-zinc-500 border-zinc-200 dark:border-zinc-800 disabled:bg-zinc-50 dark:disabled:bg-zinc-950"
            v-bind="inputProps" v-keyfilter="keyfilter" @update:modelValue="$emit('update:modelValue', $event)"
            @blur="$emit('blur')" />
    </template>
</template>

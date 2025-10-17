<!-- src/components/ConfirmAction.vue -->
<template>
  <ConfirmDialog
    group="confirm-action"
    :pt="{
      message: { class: 'text-sm' },
      icon: { class: 'text-lg w-5 h-5' }
    }"
  >
    <template #container="{ message, acceptCallback, rejectCallback }">
      <div
        class="relative w-[22vw] !p-4 sm:p-8 rounded-2xl
               bg-white text-zinc-800 dark:bg-zinc-900 dark:text-zinc-100
               shadow-xl ring-1 ring-zinc-200/60 dark:ring-zinc-800/60"
      >
        <!-- Badge/Icon circular -->
        <div
          class="absolute top-2.5 left-1/2 -translate-x-1/2
                 h-10 w-10 rounded-full flex items-center justify-center shadow-md
                 ring-4 ring-white dark:ring-zinc-900"
          :class="message.circleClass || 'bg-zinc-800 text-white'"
        >
          <i :class="[message.icon || 'pi pi-question', '!text-[16px]']"></i>
        </div>

        <div class="mt-10 text-center">
          <h3 class="font-semibold mb-0.5">{{ message.header }}</h3>
          <p class="text-[0.8rem] text-zinc-600 dark:text-zinc-300">
            {{ message.message }}
          </p>
        </div>

        <div class="mt-2 flex items-center justify-center gap-2">
          <Button
            :label="message.acceptLabel || 'Confirmar'"
            :severity="message.acceptSeverity || 'contrast'"
            size="small"
            class="py-1 text-[0.8rem]"
            :class="message.acceptSeverity === 'danger' ? 'dark:bg-red-600 text-white hover:dark:bg-red-700 dark:border-red-600 hover:dark:border-red-700' : ''"
            @click="acceptCallback"
          />
          <Button
            :label="message.rejectLabel || 'Cancelar'"
            :severity="message.rejectSeverity || 'secondary'"
            size="small"
            class="py-1 text-[0.8rem]"
            variant="outlined"
            @click="rejectCallback"
          />
        </div>
      </div>
    </template>
  </ConfirmDialog>
</template>

<script setup>
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'

const confirm = useConfirm()

/**
 * Abre o confirm e resolve com true/false.
 * @param {Object} opts
 * @param {'create'|'edit'|'delete'} [opts.mode='edit']
 * @param {String} [opts.title='Confirmação']
 * @param {String} [opts.description='Tem certeza?']
 * @param {String} [opts.acceptLabel]
 * @param {String} [opts.rejectLabel]
 * @returns {Promise<boolean>}
 */
function ask (opts = {}) {
  const {
    mode = 'edit',
    title = 'Confirmação',
    description = 'Tem certeza?',
    acceptLabel,
    rejectLabel
  } = opts

  const sevMap = { create: 'success', edit: 'contrast', delete: 'danger' }
  const iconMap = { create: 'pi pi-check', edit: 'pi pi-pencil', delete: 'pi pi-trash' }
  const circleMap = {
    create: 'bg-emerald-500 text-white',
    edit:   'bg-zinc-800 text-white',
    delete: 'bg-red-600 text-white'
  }

  const aLabel = acceptLabel ?? (mode === 'create' ? 'Criar' : mode === 'delete' ? 'Excluir' : 'Salvar')
  const rLabel = rejectLabel ?? 'Cancelar'

  return new Promise((resolve) => {
    confirm.require({
      group: 'confirm-action',
      header: title,
      message: description,
      // os campos abaixo ficam disponíveis como "message" no slot #container
      icon: iconMap[mode] ?? 'pi pi-question',
      circleClass: circleMap[mode] ?? 'bg-zinc-800 text-white',
      acceptLabel: aLabel,
      rejectLabel: rLabel,
      acceptSeverity: sevMap[mode] ?? 'contrast',
      rejectSeverity: 'secondary',
      // callbacks do PrimeVue (em caso de fallback ao template padrão)
      accept: () => resolve(true),
      reject: () => resolve(false),
    })
  })
}

defineExpose({ ask })
</script>

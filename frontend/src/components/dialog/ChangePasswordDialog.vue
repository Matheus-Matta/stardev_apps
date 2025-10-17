<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Alterar senha"
    :style="{ width: '420px' }"
  >
    <div class="space-y-5">
      <!-- Senha atual -->
      <div class="flex flex-col gap-2">
        <label for="cp_current" class="font-medium">Senha atual</label>
        <div class="relative">
          <InputText
            id="cp_current"
            v-model.trim="currentPassword"
            :type="showCurrent ? 'text' : 'password'"
            placeholder="Senha atual"
            unstyled
            class="w-full px-3 py-2 text-sm rounded-lg border bg-white text-zinc-900
                   border-zinc-300 placeholder-zinc-400
                   focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-zinc-600
                   dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700
                   dark:focus:ring-zinc-600 dark:focus:border-zinc-600"
            @keyup.enter="onSubmit"
            autocomplete="current-password"
          />
          <button
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 rounded-md text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200"
            @click="showCurrent = !showCurrent"
            :aria-label="showCurrent ? 'Ocultar senha' : 'Mostrar senha'"
          >
            <i :class="showCurrent ? 'pi pi-eye-slash' : 'pi pi-eye'"></i>
          </button>
        </div>
      </div>

      <!-- Nova senha -->
      <div class="flex flex-col gap-2">
        <label for="cp_new" class="font-medium">Nova senha</label>
        <div class="relative">
          <InputText
            id="cp_new"
            v-model.trim="newPassword"
            :type="showNew ? 'text' : 'password'"
            placeholder="Senha nova"
            unstyled
            class="w-full px-3 py-2 text-sm rounded-lg border bg-white text-zinc-900
                   border-zinc-300 placeholder-zinc-400
                   focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-zinc-600
                   dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700
                   dark:focus:ring-zinc-600 dark:focus:border-zinc-600"
            @keyup.enter="onSubmit"
            autocomplete="new-password"
          />
          <button
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 rounded-md text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200"
            @click="showNew = !showNew"
            :aria-label="showNew ? 'Ocultar senha' : 'Mostrar senha'"
          >
            <i :class="showNew ? 'pi pi-eye-slash' : 'pi pi-eye'"></i>
          </button>
        </div>

        <!-- Barra de força -->
        <div class="space-y-1">
          <div class="w-full h-2 rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden">
            <div
              class="h-full transition-all"
              :class="'bg-' + barClass"
              :style="{ width: strengthPercent + '%' }"
            ></div>
        </div>
            <div class="text-xs text-center font-medium" >
            <span :class="'text-' + barClass">{{ strengthLabel }}</span>
            </div>
        </div>

        <!-- Checklist de regras -->
        <ul class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1 text-xs">
          <li v-for="(r, i) in rules" :key="i" class="flex items-center gap-2"
              :class="r.pass ? 'text-emerald-600 dark:text-emerald-400' : 'text-zinc-500 dark:text-zinc-400'">
            <i :class="r.pass ? 'pi pi-check-circle' : 'pi pi-circle'"></i>
            <span>{{ r.label }}</span>
          </li>
        </ul>
      </div>

      <!-- Confirmar nova senha -->
      <div class="flex flex-col gap-2">
        <label for="cp_confirm" class="font-medium">Confirmar nova senha</label>
        <div class="relative">
          <InputText
            id="cp_confirm"
            v-model.trim="confirmPassword"
            :type="showConfirm ? 'text' : 'password'"
            placeholder="Confirmar nova senha"
            unstyled
            class="w-full px-3 py-2 text-sm rounded-lg border bg-white text-zinc-900
                   border-zinc-300 placeholder-zinc-400
                   focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-zinc-600
                   dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700
                   dark:focus:ring-zinc-600 dark:focus:border-zinc-600"
            @keyup.enter="onSubmit"
            autocomplete="new-password"
          />
          <button
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 rounded-md text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200"
            @click="showConfirm = !showConfirm"
            :aria-label="showConfirm ? 'Ocultar senha' : 'Mostrar senha'"
          >
            <i :class="showConfirm ? 'pi pi-eye-slash' : 'pi pi-eye'"></i>
          </button>
        </div>

        <p v-if="confirmPassword && !matchConfirm" class="text-xs text-red-500">
          A confirmação não confere com a nova senha.
        </p>
      </div>

      <!-- Ações -->
      <div class="flex justify-end gap-2 pt-1">
        <Button label="Cancelar" size="small" severity="secondary" @click="close" :disabled="loading" />
        <Button label="Salvar" size="small" severity="contrast" :loading="loading" :disabled="!allValid || loading" @click="onSubmit" />
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useAuthStore } from '../../store/auth/auth'

const visible = ref(false)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)

const showCurrent = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

function open () {
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  showCurrent.value = showNew.value = showConfirm.value = false
  visible.value = true
}
function close () {
  visible.value = false
}

const hasMinLen     = computed(() => (newPassword.value || '').length >= 8)
const hasUpper      = computed(() => /[A-Z]/.test(newPassword.value || ''))
const hasLower      = computed(() => /[a-z]/.test(newPassword.value || ''))
const hasNumOrSym   = computed(() => /[0-9]|[^A-Za-z0-9]/.test(newPassword.value || ''))
const noSpaces      = computed(() => !/\s/.test(newPassword.value || ''))
const notSameAsOld  = computed(() =>
  !!currentPassword.value && !!newPassword.value ? currentPassword.value !== newPassword.value : true
)
const matchConfirm  = computed(() =>
  !newPassword.value || confirmPassword.value === newPassword.value
)

const rules = computed(() => ([
  { label: 'Mín. 8 caracteres', pass: hasMinLen.value },
  { label: '1 letra maiúscula', pass: hasUpper.value },
  { label: '1 letra minúscula', pass: hasLower.value },
  { label: '1 número ou símbolo', pass: hasNumOrSym.value },
  { label: 'Sem espaços', pass: noSpaces.value },
  { label: 'Diferente da senha atual', pass: notSameAsOld.value },
  { label: 'Confirmação igual', pass: matchConfirm.value },
]))

const passedCount = computed(() => rules.value.filter(r => r.pass).length)
const strengthPercent = computed(() => Math.round((passedCount.value / rules.value.length) * 100))
const strengthLabel = computed(() => {
   if (!newPassword.value) return ''
  if (strengthPercent.value >= 90) return 'Muito forte'
  if (strengthPercent.value >= 70) return 'Forte'
  if (strengthPercent.value >= 50) return 'Média'
  if (strengthPercent.value >= 25) return 'Fraca'
  return 'Muito fraca'
})

const barClass = computed(() => {
  if (!newPassword.value) return 'transparent'
  if (strengthPercent.value >= 90) return 'emerald-500'
  if (strengthPercent.value >= 70) return 'lime-500'
  if (strengthPercent.value >= 50) return 'yellow-500'
  if (strengthPercent.value >= 25) return 'orange-500'
  return 'red-500'
})

const allValid = computed(() =>
  !!currentPassword.value &&
  !!newPassword.value &&
  !!confirmPassword.value &&
  rules.value.every(r => r.pass)
)

async function onSubmit () {
  if (!allValid.value) return
  loading.value = true
  try {
    const auth = useAuthStore()
    await auth.changePassword({
      currentPassword: currentPassword.value,
      newPassword: newPassword.value
    })
    close()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

defineExpose({ open, close })
</script>

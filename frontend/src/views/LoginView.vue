<template>
  <div class="min-h-[100dvh] flex items-center justify-center px-6 py-16">
    <Card class="w-full max-w-[400px] shadow-sm">
      <template #title>
        <div class="text-center text-2xl font-semibold">
          {{ t('common.welcomeBack') }}
        </div>
      </template>

      <template #content>
        <div class="flex flex-col gap-6">
          <SchemaForm
            :schema="loginSchema"
            :initial="initialValues"
            :submitLabel="loading ? 'Entrando…' : 'Entrar'"
            :loading="loading"
            @submit="onSubmit"
          >
          </SchemaForm>

          <div v-if="error" class="text-red-500 text-sm">
            {{ error }}
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'

import Card from 'primevue/card'
import SchemaForm from '../components/forms/LoginForm.vue'
import { useAuthStore } from '../store/auth/auth'

const { t } = useI18n()

// --- Validadores com i18n
const required = () => (v) =>
  (v !== null && v !== undefined && String(v).trim() !== '') || t('forms.errors.required')

const isEmail = () => (v) =>
  (!v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v))) || t('forms.errors.email')

const minLen = (n) => (v) =>
  (!v || String(v).length >= n) || t('forms.errors.minLength', { n })

// --- Schema do formulário usando chaves de tradução
const loginSchema = [
  {
    key: 'email',
    type: 'text',
    label: t('forms.email.label'),
    placeholder: t('forms.email.placeholder'),
    rules: [required(), isEmail()]
  },
  {
    key: 'password',
    type: 'password',
    label: t('forms.password.label'),
    placeholder: t('forms.password.placeholder'),
    rules: [required(), minLen(3)]
  },
]

const initialValues = { email: '', password: '', remember: false }

// --- Auth flow
const router = useRouter()
const auth = useAuthStore()
const { loading } = storeToRefs(auth)
const error = computed(() => auth.error)

const onSubmit = async (values) => {
  if (loading.value) return
  const ok = await auth.login(values.email, values.password)
  if (ok) {
    router.push({ path: '/' })
  }
}
</script>
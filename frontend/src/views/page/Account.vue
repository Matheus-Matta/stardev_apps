<script setup>
import { reactive, ref, onMounted } from 'vue'
import BaseView from '../../layout/BaseView.vue'
import SchemaRenderer from '../../components/forms/SchemaRenderer.vue'
import { accountSchema } from '../../forms/schemas/update/account'
import { useStore } from '../../store/index'

const accountApi = useStore('account')

const model = reactive({
  slug: '',
  legal_name: '',
  display_name: '',
  email_principal: '',
  phone_principal: '',
  site_url: '',
  logo_url: ''
})

const id = ref(null)
const loading = ref(false)
const error = ref(null)
const saved = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const acc = await accountApi.get({ force: true })
    if (acc) {
      id.value = acc.id
      Object.assign(model, {
        slug: acc.slug || '',
        legal_name: acc.legal_name || '',
        display_name: acc.display_name || '',
        email_principal: acc.email_principal || '',
        phone_principal: acc.phone_principal || '',
        site_url: acc.site_url || '',
        logo_url: acc.logo_url || ''
      })
    }
  } catch (e) {
    error.value = e?.message || 'Falha ao carregar'
  } finally {
    loading.value = false
  }
})

function onSuccess() {
  saved.value = true
  setTimeout(() => (saved.value = false), 1500)
}
function onError(e) {
  error.value = e?.message || 'Falha ao salvar'
}
</script>

<template>
  <BaseView>
    <div class="mx-auto">
      <div class="flex my-4 mx-2 items-center gap-2">
        <i :class="accountSchema.icon + ' text-2xl text-zinc-700 dark:text-zinc-200'"></i>
        <h1 class="text-zinc-700 dark:text-zinc-200 font-semibold">{{ accountSchema.title }}</h1>
      </div>
      <Card class="shadow-lg bg-transparent" :pt="{ body: { class: 'p-0' } }">
        <template #content>
          <SchemaRenderer
            :schema="accountSchema"
            v-model="model"
            method="update"
            :ids="{ account: id }"
            :loading="loading"
            :submit-label="accountSchema.submitLabel"
            @success="onSuccess"
            @error="onError"
          />
        </template>
      </Card>
    </div>
  </BaseView>
</template>

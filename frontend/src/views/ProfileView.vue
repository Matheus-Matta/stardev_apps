<script setup>
import { reactive, ref, onMounted } from 'vue'
import BaseView from '../layout/BaseView.vue'
import Card from 'primevue/card'
import SchemaRenderer from '../components/forms/SchemaRenderer.vue'
import { settingsSchema } from '../forms/schemas/update/user'
import { useStore } from '../store'

const userApi = useStore('user')
const model = reactive({
  id: null,
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  display_name: '',
  phone: '',
  bio: '',
})

const userId = ref(null)
const loading = ref(false)
const saved = ref(false)
const error = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    const me = await userApi.get({ force: true })
    userId.value = me.id
    Object.assign(model, me)
  } catch (e) {
    error.value = e?.message || 'Falha ao carregar usuário'
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
        <i :class="settingsSchema.icon + ' text-2xl text-zinc-700 dark:text-zinc-200'"></i>
        <h1 class="text-zinc-700 dark:text-zinc-200 font-semibold">{{ settingsSchema.title }}</h1>
      </div>

      <Card class="shadow-lg bg-transparent" :pt="{ body: { class: 'p-0' } }">
        <template #content>
          <SchemaRenderer
            :schema="settingsSchema"
            v-model="model"
            method="update"
            :ids="{ user: userId }"
            :loading="loading"
            :submit-label="settingsSchema.submitLabel"
            @success="onSuccess"
            @error="onError"
          />
        </template>
      </Card>
    </div>
  </BaseView>
</template>

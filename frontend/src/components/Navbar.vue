<!-- src/components/Navbar.vue -->
<template>
  <nav class="fixed top-0 z-50 w-full h-14 bg-zinc-900 border-b border-zinc-800 flex items-center">
    <div class="w-full px-3 lg:px-4 container mx-auto">
      <div class="grid grid-cols-[auto_1fr_auto] items-center gap-3">
        <!-- Esquerda: Brand -->
        <RouterLink :to="brand.to" class="flex items-center gap-2 min-w-[120px] justify-self-start">
          <img
            v-if="brand.logo"
            :src="brand.logo"
            :alt="brand.alt || brand.title"
            class="h-6 w-auto rounded-sm"
            :key="brand.logo"
          />
          <span v-else class="text-zinc-50 font-semibold text-lg">{{ brand.title }}</span>
        </RouterLink>
        <div class="relative flex items-center gap-2 min-w-[130px] justify-self-end">
          <div class="justify-self-center w-full flex justify-center">
              <div class="relative w-full max-w-3xl">
                      <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 pointer-events-none"></i>
                      <InputText
                        unstyled
                        ref="searchRef"
                        v-model="search"
                        :placeholder="placeholder"
                        class="w-full pl-10 pr-16 py-1 rounded-full bg-zinc-800 border border-zinc-700 text-sm text-zinc-200
                                   placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-zinc-600"
                        aria-label="Buscar"
                      />
              </div>
          </div>
          <Button
            text rounded class="!h-9 !w-9 hover:!bg-zinc-800"
            @click="toggleNotifs"
            aria-label="Notificações"
                v-tooltip.bottom="{
                value: 'notificações',
                pt: { text: { class: '!bg-zinc-800' } },
            }"
          >
            <i class="pi pi-bell text-zinc-200"></i>
            <Badge v-if="notifCount>0" :value="notifCount" severity="contrast" class="ml-2" />
          </Button>

          <Popover ref="notifPopover" unstyled class="rounded-xl bg-zinc-900 border border-zinc-800 shadow-lg">
            <div class="p-3">
              <div class="text-zinc-100 font-medium mb-2">Notificações</div>
              <ul>
                <li v-for="(n,i) in notifications" :key="i" class="text-sm text-zinc-300">• {{ n }}</li>
                <li v-if="notifications.length===0" class="text-sm text-zinc-400">Sem notificações.</li>
              </ul>
            </div>
          </Popover>

          <!-- Theme toggle -->
          <Button
            text rounded class="!h-9 !w-9 hover:!bg-zinc-800"
            @click="toggleTheme"
                v-tooltip.bottom="{
                value: isDark ? 'Modo claro' : 'Modo escuro',
                pt: { text: { class: '!bg-zinc-800' } },
            }"
          >
            <i :class="isDark ? 'pi pi-sun' : 'pi pi-moon'" class="text-zinc-200" />
          </Button>

          <!-- Alterar senha -->
          <Button
            text rounded class="!h-9 !w-9 hover:!bg-zinc-800"
            @click="pwdDialog?.open()"
                v-tooltip.bottom="{
                value: 'Alterar senha',
                pt: { text: { class: '!bg-zinc-800' } },
            }"
          >
            <i class="pi pi-lock text-zinc-200" />
          </Button>

          <!-- Sair -->
          <Button
            text rounded class="!h-9 !w-9 hover:!bg-zinc-800"
            @click="handleLogout"
                v-tooltip.bottom="{
                value: 'Sair',
                pt: { text: { class: '!bg-zinc-800' } },
            }"
          >
            <i class="pi pi-sign-out text-zinc-200" />
          </Button>
        </div>
      </div>
    </div>
    <ChangePasswordDialog ref="pwdDialog" />
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ChangePasswordDialog from './dialog/ChangePasswordDialog.vue'

import { useStore } from '../store/index'
import { useTheme } from '../lib/theme'
const { isDark, toggleTheme, initTheme } = useTheme()

const props = defineProps({ placeholder: { type: String, default: 'Pesquisar' } })
const router = useRouter()

const accountApi = useStore('account')
const userApi    = useStore('user')

const account = ref(null)
const user    = ref(null)
const pwdDialog = ref(null)
const searchRef = ref(null)
const search = ref('')

const notifications = ref([])
const notifPopover = ref(null)
const notifCount = computed(() => notifications.value.length)
function toggleNotifs(e) { notifPopover.value?.toggle(e) }

const logoSrc = computed(() => {
  const src = account.value?.logo || ''
  if (!src) return ''
  const stamp = account.value?.updatedAt || 0
  const sep = src.includes('?') ? '&' : '?'
  return `${src}${sep}v=${stamp}`
})

const brand = computed(() => ({
  to: '/',
  logo: logoSrc.value,
  title: account.value?.display_name || 'Minha Marca',
  alt:   account.value?.display_name || 'Minha Marca'
}))

async function handleLogout() {
  const { useAuthStore } = await import('../store/auth')
  const auth = useAuthStore()
  await auth.logout()
  router.push('/login')
}

onMounted(async () => {
  initTheme()
  try {
    const [acc, usr] = await Promise.all([
      accountApi.get?.({ force: true }),
      userApi.get?.({ force: true }),
    ])
    account.value = acc || account.value
    user.value = usr || user.value
  } catch (e) {
    console.error('Navbar fetch error:', e)
  }
})
</script>


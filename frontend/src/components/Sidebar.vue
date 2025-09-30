<!-- src/components/AppSidebar.vue -->
<script setup>
import { ref, computed, watch } from 'vue'   // 👈 adiciona watch
import PanelMenu from 'primevue/panelmenu'
import { useUserStore } from '../store/user'
import { useRoute } from 'vue-router'

const route = useRoute()
const userStore = useUserStore()

// 👇 precisa existir para o v-model:expandedKeys
const expandedKeys = ref({})                // 👈 adiciona

function routeMatches(item) {
  if (!item?.route) return false
  return route.path === item.route || route.path.startsWith(item.route + '/')
}

function routeMatchesDeep(item) {
  if (routeMatches(item)) return true
  return Array.isArray(item?.items) && item.items.some(routeMatchesDeep)
}

const rawItems = ref([
  { key: 'home', label: 'Home', icon: 'pi pi-home', route: '/' },
  {
    key: 'comercial',
    label: 'Comercial',
    icon: 'pi pi-users',
    items: [
      { key: 'comercial-account', label: 'Conta', icon: 'pi pi-id-card', route: '/account', permission: 'view_account' },
      { key: 'comercial-businesses', label: 'Empresas', icon: 'pi pi-briefcase', route: '/businesses/list', permission: 'view_business' }
    ]
  },
  {
    key: 'settings',
    label: 'Configurações',
    icon: 'pi pi-cog',
    items: [
      { key: 'settings-profile', label: 'Minha Conta', icon: 'pi pi-user', route: '/profile' },
    ]
  },
])

function filterByPermission(items) {
  const out = []
  for (const item of items || []) {
    const permOK = !item.permission || userStore.hasPermission(item.permission)
    if (!permOK) continue
    const clone = { ...item }
    if (clone.items?.length) {
      clone.items = filterByPermission(clone.items)
      if (!clone.items.length) continue
    }
    out.push(clone)
  }
  return out
}

const menuItems = computed(() => filterByPermission(rawItems.value))

function buildExpandedKeys(items) {
  const keys = {}
  const walk = (nodes = []) => nodes.forEach(n => {
    if (n.items?.length) {
      if (routeMatchesDeep(n) && n.key) keys[n.key] = true
      walk(n.items)
    }
  })
  walk(items)
  return keys
}

watch(
  () => [route.path, menuItems.value],
  () => { expandedKeys.value = buildExpandedKeys(menuItems.value) },
  { immediate: true, deep: true }
)
</script>

<template>
  <aside class="rounded-2xl p-3 shadow-md bg-white border-zinc-100/50 dark:bg-zinc-900/80 dark:border-zinc-800"
    :class="['h-[calc(100vh-var(--header-h)-var(--footer-h))]', 'overflow-hidden flex flex-col']">
    <div class="flex-1 overflow-y-auto">
      <PanelMenu
        v-model:expandedKeys="expandedKeys"
        :model="menuItems"
        multiple
        class="w-full"
        :pt="{
          root: { class: 'gap-0' },
          panel: { class: 'border-0 m-0 p-0 bg-transparent' },
          header: { class: 'text-[14px] font-semibold dark:bg-zinc-900 rounded-md shadow-sm dark:shadow-zinc-950/50 shadow-zinc-200' },
          headerLink: { class: 'py-1 flex items-center' },
          itemContent: { class: 'text-[14px] font-semibold my-1 dark:bg-zinc-900 rounded-md shadow-sm dark:shadow-zinc-950/50 shadow-zinc-200' },
          icon: { class: 'text-[14px]' }
        }"
      >
        <template #item="{ item }">
          <!-- Filho com rota (destaca quando ativo) -->
          <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
            <a
              v-ripple
              :href="href"
              @click="navigate"
              :class="[
                'flex items-center cursor-pointer text-[14px] rounded-md px-2 py-1 my-1 transition-colors',
                routeMatches(item)
                  ? 'bg-zinc-100/70 dark:bg-zinc-800/70 text-zinc-900 dark:text-zinc-100 font-semibold ring-1 ring-zinc-200/60 dark:ring-zinc-700/60'
                  : 'text-zinc-600 dark:text-zinc-200 hover:bg-zinc-100/50 hover:dark:bg-zinc-800'
              ]"
            >
              <span :class="[item.icon, 'text-[14px]']" />
              <span class="ml-2">{{ item.label }}</span>
            </a>
          </router-link>

          <a
            v-else
            v-ripple
            class="flex items-center cursor-pointer text-[14px] rounded-md my-1 px-2 py-1 transition-colors
                   text-zinc-600 dark:text-zinc-200 hover:bg-zinc-100/50 hover:dark:bg-zinc-800"
            :href="item.url"
            :target="item.target"
          >
            <span :class="[item.icon, 'text-[14px]']" />
            <span class="ml-2">{{ item.label }}</span>
            <span
              v-if="item.items"
              :class="[
                'pi pi-angle-up ml-auto text-[14px] transition-transform',
                expandedKeys[item.key] ? 'rotate-180' : ''
              ]"
            />
          </a>
        </template>
      </PanelMenu>
    </div>
  </aside>
</template>

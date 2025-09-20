<script setup>
import SidebarItem from "./nav/SidebarItem.vue";
import SidebarSeparator from "./nav/SidebarSeparator.vue";
import SidebarGroup from "./nav/SidebarGroup.vue";

const props = defineProps({
  open:    { type: Boolean, default: false },
  user:    { type: Object,  default: () => ({}) },
  account: { type: [String, Object, null], default: null },
});
const emit = defineEmits(["close"]);
</script>

<template>
  <!-- overlay (mobile) -->
  <div
    v-if="open"
    class="fixed inset-0 z-40 bg-black/30 sm:hidden"
    @click="$emit('close')"
  />

  <!-- drawer + sidebar -->
  <aside
    id="sidebar-multi-level-sidebar"
    class="fixed top-0 left-0 z-40 w-64 h-screen pt-16 transition-transform
           bg-white border-r border-gray-200 dark:bg-gray-800 dark:border-gray-700
           -translate-x-full sm:translate-x-0"
    :class="{ 'translate-x-0': open }"
    aria-label="Sidebar"
  >
    <div class="h-full px-3 pt-4 pb-4 overflow-y-auto bg-white dark:bg-gray-800">
      <ul class="space-y-2 font-medium">
        <!-- Dashboard -->
        <li>
          <SidebarItem
            to="/"
            label="Dashboard"
            exact
            @click="$emit('close')"
          >
            <template #icon>
              <svg class="w-5 h-5" viewBox="0 0 22 21" fill="currentColor">
                <path d="M16.975 11H10V4.025a1 1 0 0 0-1.066-.998 8.5 8.5 0 1 0 9.039 9.039.999.999 0 0 0-1-1.066h.002Z"/>
                <path d="M12.5 0c-.157 0-.311.01-.565.027A1 1 0 0 0 11 1.02V10h8.975a1 1 0 0 0 1-.935c.013-.188.028-.374.028-.565A8.51 8.51 0 0 0 12.5 0Z"/>
              </svg>
            </template>
          </SidebarItem>
        </li>

        <!-- Kanban -->
        <li>
          <SidebarItem
            to="/kanban"
            label="Kanban"
            badge-text="Pro"
            badge-tone="gray"
            @click="$emit('close')"
          >
            <template #icon>
              <svg class="w-5 h-5" viewBox="0 0 18 18" fill="currentColor">
                <path d="M6.143 0H1.857A1.857 1.857 0 0 0 0 1.857v4.286C0 7.169.831 8 1.857 8h4.286A1.857 1.857 0 0 0 8 6.143V1.857A1.857 1.857 0 0 0 6.143 0Zm10 0h-4.286A1.857 1.857 0 0 0 10 1.857v4.286C10 7.169 10.831 8 11.857 8h4.286A1.857 1.857 0 0 0 18 6.143V1.857A1.857 1.857 0 0 0 16.143 0Zm-10 10H1.857A1.857 1.857 0 0 0 0 11.857v4.286C0 17.169.831 18 1.857 18h4.286A1.857 1.857 0 0 0 8 16.143v-4.286A1.857 1.857 0 0 0 6.143 10Zm10 0h-4.286A1.857 1.857 0 0 0 10 11.857v4.286c0 1.026.831 1.857 1.857 1.857h4.286A1.857 1.857 0 0 0 18 16.143v-4.286A1.857 1.857 0 0 0 16.143 10Z"/>
              </svg>
            </template>
          </SidebarItem>
        </li>

        <!-- Inbox -->
        <li>
          <SidebarItem
            to="/inbox"
            label="Inbox"
            :badge-text="3"
            badge-tone="blue"
            @click="$emit('close')"
          >
            <template #icon>
              <svg class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="m17.418 3.623-.018-.008a6.713 6.713 0 0 0-2.4-.569V2h1a1 1 0 1 0 0-2h-2a1 1 0 0 0-1 1v2H9.89A6.977 6.977 0 0 1 12 8v5h-2V8A5 5 0 1 0 0 8v6a1 1 0 0 0 1 1h8v4a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-4h6a1 1 0 0 0 1-1V8a5 5 0 0 0-2.582-4.377ZM6 12H4a1 1 0 0 1 0-2h2a1 1 0 0 1 0 2Z"/>
              </svg>
            </template>
          </SidebarItem>
        </li>

        <!-- Users -->
        <li>
          <SidebarItem
            to="/users"
            label="Users"
            @click="$emit('close')"
          >
            <template #icon>
              <svg class="w-5 h-5" viewBox="0 0 20 18" fill="currentColor">
                <path d="M14 2a3.963 3.963 0 0 0-1.4.267 6.439 6.439 0 0 1-1.331 6.638A4 4 0 1 0 14 2Zm1 9h-1.264A6.957 6.957 0 0 1 15 15v2a2.97 2.97 0 0 1-.184 1H19a1 1 0 0 0 1-1v-1a5.006 5.006 0 0 0-5-5ZM6.5 9a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9ZM8 10H5a5.006 5.006 0 0 0-5 5v2a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-2a5.006 5.006 0 0 0-5-5Z"/>
              </svg>
            </template>
          </SidebarItem>
        </li>

        <!-- Separador -->
        <SidebarSeparator />

        <!-- Submenu: E-commerce -->
        <li>
          <SidebarGroup
            label="E-commerce"
            :items="[
              { label: 'Products', to: '/ecom/products' },
              { label: 'Billing', to: '/ecom/billing' },
              { label: 'Invoice', to: '/ecom/invoice' },
            ]"
            @item:click="$emit('close')"
          >
            <template #icon>
              <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" viewBox="0 0 18 18" fill="currentColor">
                <path d="M6.143 0H1.857A1.857 1.857 0 0 0 0 1.857v4.286C0 7.169.831 8 1.857 8h4.286A1.857 1.857 0 0 0 8 6.143V1.857A1.857 1.857 0 0 0 6.143 0Zm10 0h-4.286A1.857 1.857 0 0 0 10 1.857v4.286C10 7.169 10.831 8 11.857 8h4.286A1.857 1.857 0 0 0 18 6.143V1.857A1.857 1.857 0 0 0 16.143 0Zm-10 10H1.857A1.857 1.857 0 0 0 0 11.857v4.286C0 17.169.831 18 1.857 18h4.286A1.857 1.857 0 0 0 8 16.143v-4.286A1.857 1.857 0 0 0 6.143 10Zm10 0h-4.286A1.857 1.857 0 0 0 10 11.857v4.286c0 1.026.831 1.857 1.857 1.857h4.286A1.857 1.857 0 0 0 18 16.143v-4.286A1.857 1.857 0 0 0 16.143 10Z"/>
              </svg>
            </template>
          </SidebarGroup>
        </li>

        <!-- Outro Submenu -->
        <li>
          <SidebarGroup
            label="Relatórios"
            :items="[
              { label: 'Vendas', to: '/reports/sales' },
              { label: 'Financeiro', to: '/reports/finance', badgeText: 'novo', badgeTone: 'red' },
            ]"
            @item:click="$emit('close')"
          >
            <template #icon>
              <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 3h2v18H3zM7 13h2v8H7zM11 9h2v12h-2zM15 5h2v16h-2zM19 2h2v19h-2z"/>
              </svg>
            </template>
          </SidebarGroup>
        </li>
      </ul>
    </div>
  </aside>
</template>

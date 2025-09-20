<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import { useRoute } from "vue-router";
import Navbar from "../components/Navbar.vue";
import Sidebar from "../components/Sidebar.vue";

import { useAuthStore } from "../store/auth";
import { useUserStore } from "../store/user";
import { useAccountStore } from "../store/account";

const isSidebarOpen = ref(false);

const route = useRoute();
const auth = useAuthStore();
const userStore = useUserStore();
const accountStore = useAccountStore();

userStore.hydrate();
accountStore.hydrate();

function createSpamBlocker({ minIntervalMs = 5000, maxBurst = 3, burstWindowMs = 20000 } = {}) {
  let lastRun = 0, burst = 0, winStart = 0;
  return {
    allowed() {
      const now = Date.now();
      if (now - lastRun < minIntervalMs) return false;
      if (now - winStart > burstWindowMs) { winStart = now; burst = 0; }
      if (burst >= maxBurst) return false;
      lastRun = now; burst += 1; return true;
    }
  };
}
const blocker = createSpamBlocker();

async function refresh({ force = false } = {}) {
  if (!blocker.allowed()) return;
  const userId = auth.user?.id;
  const accountId = auth.account?.id;
  const tasks = [];
  if (auth.isAuthenticated && userId)   tasks.push(userStore.ensure(userId,   { force }).catch(() => {}));
  if (auth.isAuthenticated && accountId) tasks.push(accountStore.ensure(accountId, { force }).catch(() => {}));
  if (tasks.length) await Promise.allSettled(tasks);
}

function onFocus() { refresh({ force: false }); }
function onOnline() { refresh({ force: true }); }
function onVisibleChange() {
  if (document.visibilityState === "visible") refresh({ force: false });
}

onMounted(() => {
  refresh({ force: false });
  window.addEventListener("focus", onFocus);
  window.addEventListener("online", onOnline);
  document.addEventListener("visibilitychange", onVisibleChange);
});

watch(() => route.fullPath, () => refresh({ force: false }));

onBeforeUnmount(() => {
  window.removeEventListener("focus", onFocus);
  window.removeEventListener("online", onOnline);
  document.removeEventListener("visibilitychange", onVisibleChange);
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <Navbar
      @toggle-sidebar="isSidebarOpen = !isSidebarOpen"
    />
    <Sidebar
      @close="isSidebarOpen = false"
    />
    <main class="px-4 py-3 sm:ml-64">
      <div class="mt-16"></div>
      <div><slot /></div>
    </main>
  </div>
</template>

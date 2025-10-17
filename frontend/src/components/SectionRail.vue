<!-- src/components/SectionRail.vue -->
<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';

const props = defineProps({
  title: { type: String, default: 'Organization' },
  // items: [{ id: 'sec-0', title: 'Overview', children: [...] }]
  items: { type: Array, required: true },
});

const emit = defineEmits(['navigate', 'update:activeId']);

const listRef = ref(null);
const itemEls = new Map();         // id -> element
const markerTop = ref(0);
const activeId = ref(null);

// flaten com nível p/ indentação
const flatItems = computed(() => {
  const out = [];
  const walk = (arr, lvl = 0) => {
    arr?.forEach((it) => {
      out.push({ ...it, _level: lvl });
      if (it.children?.length) walk(it.children, lvl + 1);
    });
  };
  walk(props.items, 0);
  return out;
});

function registerItem(el, id) {
  if (!el) itemEls.delete(id);
  else itemEls.set(id, el);
}

function positionMarker(id) {
  nextTick(() => {
    const el = itemEls.get(id);
    const list = listRef.value;
    if (!el || !list) return;
    const er = el.getBoundingClientRect();
    const lr = list.getBoundingClientRect();
    // bolinha 8px => centraliza
    markerTop.value = er.top - lr.top + er.height / 2 - 4;
  });
}

function setActive(id) {
  activeId.value = id;
  emit('update:activeId', id);
  positionMarker(id);
}

function scrollTo(id) {
  const target = document.getElementById(id);
  if (!target) return;
  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  setActive(id);            // ativa imediatamente no clique
  emit('navigate', id);
}

// Scroll spy
let io = null;
function setupObserver() {
  if (io) { io.disconnect(); io = null; }

  io = new IntersectionObserver(
    (entries) => {
      const vis = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => (b.intersectionRatio || 0) - (a.intersectionRatio || 0));
      if (vis.length) setActive(vis[0].target.id);
    },
    {
      root: null,
      rootMargin: '-35% 0px -55% 0px',
      threshold: [0.25, 0.5, 0.75],
    }
  );

  // observar IDs presentes no DOM
  flatItems.value.forEach(({ id }) => {
    const el = document.getElementById(id);
    if (el) io.observe(el);
  });
}

onMounted(async () => {
  await nextTick();
  setupObserver();
  const first = flatItems.value[0]?.id;
  if (first) setActive(first);
  const handler = () => positionMarker(activeId.value);
  window.addEventListener('resize', handler, { passive: true });
  onBeforeUnmount(() => window.removeEventListener('resize', handler));
});

onBeforeUnmount(() => { if (io) io.disconnect(); });

watch(
  () => props.items,
  async () => {
    await nextTick();
    setupObserver();
  },
  { deep: true }
);
</script>

<template>
  <aside class="w-[200px] hidden lg:block">
    <div class="sticky top-16">
      <div
        class="relative"
      >
        <div ref="listRef" class="relative pl-4 pr-2">
          <!-- Linha vertical -->
          <span class="pointer-events-none absolute left-2 top-2 bottom-2 w-px bg-zinc-300 dark:bg-zinc-700"></span>

          <!-- Bolinha ativa -->
          <span
            class="pointer-events-none absolute left-[7px] h-2 w-2 rounded-full transition-all duration-200
                   bg-zinc-900 dark:bg-zinc-100"
            :style="{ top: markerTop + 'px' }"
          ></span>

          <ul class="flex flex-col">
            <li
              v-for="it in flatItems"
              :key="it.id"
              :ref="el => registerItem(el, it.id)"
            >
              <Button
                variant="text"
                size="small"
                class="group py-1 my-0.5 flex font-medium w-full items-center gap-2 rounded-lg text-sm transition-colors
                       focus:outline-none focus-visible:ring-2 focus-visible:ring-zinc-300 dark:focus-visible:ring-zinc-700"
                :class="activeId === it.id
                  ? 'bg-zinc-200/50 dark:bg-zinc-800/70 text-zinc-900 dark:text-zinc-100'
                  : 'text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100/70 dark:hover:bg-zinc-800/40'"
                :style="{ paddingLeft: `${12 + it._level * 16}px` }"
                :aria-current="activeId === it.id ? 'true' : 'false'"
                @click="scrollTo(it.id)"
                @keydown.enter.prevent="scrollTo(it.id)"
                @keydown.space.prevent="scrollTo(it.id)"
                :pt="{ root: { class: 'justify-start' }, label: { class: 'truncate' } }"
              >
                <span class="truncate">{{ it.title }}</span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </aside>
</template>

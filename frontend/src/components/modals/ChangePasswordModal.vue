<template>
  <teleport to="body">
    <div v-if="open">
      <!-- Overlay -->
      <div class="fixed inset-0 z-[100] bg-black/40" @click="onBackgroundClick" />
      <!-- Modal -->
      <div
        class="fixed inset-0 z-[110] grid place-items-center px-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="cp-title"
        @keydown.escape.prevent.stop="emitClose"
      >
        <div
          ref="modalRef"
          class="w-full max-w-md rounded-md bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700"
          tabindex="-1"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 id="cp-title" class="text-lg font-semibold text-gray-900 dark:text-white">
              Alterar senha
            </h2>
            <button class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700" @click="emitClose" aria-label="Fechar">
              <Icon name="close" />
            </button>
          </div>

          <!-- Body -->
          <form @submit.prevent="handleSubmit" class="px-5 py-4 space-y-4">
            <!-- Senha atual -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Senha atual</label>
              <div class="relative">
                <input
                  :type="showCurrent ? 'text' : 'password'"
                  v-model.trim="form.current"
                  required
                  autocomplete="current-password"
                  class="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700
                         px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                />
                <button type="button" class="absolute inset-y-0 right-2 flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-300"
                        @click="showCurrent = !showCurrent" :aria-label="showCurrent ? 'Ocultar senha' : 'Mostrar senha'">
                  <Icon :name="showCurrent ? 'visibility_off' : 'visibility'" />
                </button>
              </div>
            </div>

            <!-- Nova senha -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nova senha</label>
              <div class="relative">
                <input
                  :type="showNew ? 'text' : 'password'"
                  v-model="form.newPwd"
                  required
                  autocomplete="new-password"
                  class="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700
                         px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                  @input="touched = true"
                />
                <button type="button" class="absolute inset-y-0 right-2 flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-300"
                        @click="showNew = !showNew" :aria-label="showNew ? 'Ocultar senha' : 'Mostrar senha'">
                  <Icon :name="showNew ? 'visibility_off' : 'visibility'" />
                </button>
              </div>

              <!-- força -->
              <div class="mt-2">
                <div class="h-1.5 w-full bg-gray-200 dark:bg-gray-700 rounded">
                  <div class="h-1.5 rounded transition-all" :class="barClass" :style="{ width: strengthWidth }"></div>
                </div>
                <p class="mt-1 text-xs" :class="labelClass">{{ strengthLabel }}</p>
              </div>

              <!-- requisitos -->
              <ul class="mt-2 space-y-1 text-xs">
                <li class="flex items-center" v-for="r in rulesChecks" :key="r.key">
                  <Icon :name="r.ok ? 'check_circle' : 'cancel'" :class="r.ok ? 'text-green-600 mr-1' : 'text-gray-400 mr-1'" />
                  <span :class="r.ok ? 'text-green-700 dark:text-green-400' : 'text-gray-600 dark:text-gray-300'">{{ r.label }}</span>
                </li>
              </ul>

              <p v-if="sameAsCurrent" class="mt-2 text-xs text-red-600">A nova senha não pode ser igual à senha atual.</p>
              <p v-if="containsUserInfo" class="mt-1 text-xs text-red-600">Evite usar seu nome de usuário ou e-mail na senha.</p>
            </div>

            <!-- Confirmar senha -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Repetir nova senha</label>
              <div class="relative">
                <input
                  :type="showConfirm ? 'text' : 'password'"
                  v-model="form.confirm"
                  required
                  autocomplete="new-password"
                  class="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700
                         px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                />
                <button type="button" class="absolute inset-y-0 right-2 flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-300"
                        @click="showConfirm = !showConfirm" :aria-label="showConfirm ? 'Ocultar senha' : 'Mostrar senha'">
                  <Icon :name="showConfirm ? 'visibility_off' : 'visibility'" />
                </button>
              </div>
              <p v-if="form.confirm && !matchConfirm" class="mt-2 text-xs text-red-600">As senhas não coincidem.</p>
            </div>

            <!-- erro da API -->
            <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

            <!-- Footer -->
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" @click="emitClose"
                class="px-4 py-2 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200">
                Cancelar
              </button>
              <button
                type="submit"
                :disabled="!canSubmit || loading"
                class="px-4 py-2 text-sm rounded-md text-white
                       disabled:opacity-60 disabled:cursor-not-allowed
                       bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-400"
              >
                <span v-if="!loading">Salvar</span>
                <span v-else class="inline-flex items-center gap-1">
                  <Icon name="hourglass_top" class="animate-pulse" /> Salvando…
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, watch, computed, onMounted, nextTick } from "vue";
import Icon from "../ui/Icon.vue";
import { useAuthStore } from "../../store/auth";

const props = defineProps({
  open: { type: Boolean, default: false },
  user: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["close", "submitted"]);

const auth = useAuthStore();
const loading = ref(false);
const errorMsg = ref("");

// foco inicial no abrir
const modalRef = ref(null);
onMounted(() => {
  watch(() => props.open, async (v) => {
    if (v) {
      await nextTick();
      errorMsg.value = "";
      modalRef.value?.focus?.();
    }
  });
});

// estado local
const form = ref({ current: "", newPwd: "", confirm: "" });
const showCurrent = ref(false);
const showNew = ref(false);
const showConfirm = ref(false);
const touched = ref(false);

// validações
const minLen = 12;
const hasLower = (s) => /[a-z]/.test(s);
const hasUpper = (s) => /[A-Z]/.test(s);
const hasDigit = (s) => /\d/.test(s);
const hasSymbol = (s) => /[^A-Za-z0-9]/.test(s);
const notCommon = (s) => {
  const blacklist = ["password","123456","123456789","qwerty","abc123","111111","123123","senha","iloveyou","admin","welcome","dragon","letmein","football"];
  return !blacklist.includes(s.toLowerCase());
};
const noSequences = (s) => {
  const lowers = "abcdefghijklmnopqrstuvwxyz";
  const uppers = lowers.toUpperCase();
  const digits = "0123456789";
  const seqs = [lowers, uppers, digits, "qwertyuiop", "asdfghjkl", "zxcvbnm"];
  for (const seq of seqs) {
    for (let i = 0; i < seq.length - 2; i++) {
      const pat = seq.slice(i, i + 3);
      if (s.toLowerCase().includes(pat)) return false;
    }
  }
  if (/(.)\1{2,}/.test(s)) return false;
  if (/(\w{2,})\1{1,}/i.test(s)) return false;
  return true;
};
const notEqualCurrent = computed(() => !form.value.newPwd || form.value.newPwd !== form.value.current);

const userString = computed(() => {
  const name = (props.user?.username || props.user?.name || "").toString().toLowerCase();
  const email = (props.user?.email || "").toString().toLowerCase();
  const local = email.split("@")[0] || "";
  return [name, local].filter(Boolean).join(" ");
});
const containsUserInfo = computed(() => {
  const pwd = (form.value.newPwd || "").toLowerCase();
  const tokens = userString.value.split(/[.\s_\-]+/).filter(t => t && t.length >= 3);
  return tokens.some(t => pwd.includes(t));
});

const rulesChecks = computed(() => {
  const s = form.value.newPwd || "";
  return [
    { key: "len",      ok: s.length >= minLen, label: `Mínimo ${minLen} caracteres` },
    { key: "lower",    ok: hasLower(s),        label: "Letra minúscula" },
    { key: "upper",    ok: hasUpper(s),        label: "Letra maiúscula" },
    { key: "digit",    ok: hasDigit(s),        label: "Número" },
    { key: "symbol",   ok: hasSymbol(s),       label: "Caractere especial" },
    { key: "common",   ok: notCommon(s),       label: "Não é senha comum" },
    { key: "seq",      ok: noSequences(s),     label: "Sem sequências/repetições" },
    { key: "neqcurr",  ok: notEqualCurrent.value, label: "Diferente da senha atual" },
  ];
});
const allRulesOk = computed(() => rulesChecks.value.every(r => r.ok) && !containsUserInfo.value);

const matchConfirm = computed(() => !form.value.confirm || form.value.newPwd === form.value.confirm);
const sameAsCurrent = computed(() => !!form.value.newPwd && form.value.newPwd === form.value.current);

// força
const score = computed(() => {
  const s = form.value.newPwd || "";
  let sc = 0;
  if (s.length >= minLen) sc++;
  if (hasLower(s) && hasUpper(s)) sc++;
  if (hasDigit(s)) sc++;
  if (hasSymbol(s)) sc++;
  if (!noSequences(s) || !notCommon(s) || containsUserInfo.value) sc = Math.min(sc, 2);
  return Math.max(0, Math.min(4, sc));
});
const strengthLabel = computed(() => ["Muito fraca", "Fraca", "Média", "Boa", "Excelente"][score.value]);
const strengthWidth = computed(() => `${(score.value / 4) * 100}%`);
const barClass = computed(() => [
  score.value <= 1 && "bg-red-500",
  score.value === 2 && "bg-yellow-500",
  score.value === 3 && "bg-green-500",
  score.value >= 4 && "bg-emerald-600",
].filter(Boolean).join(" "));
const labelClass = computed(() => [
  "text-xs",
  score.value <= 1 ? "text-red-600" : score.value === 2 ? "text-yellow-600" : "text-green-700 dark:text-green-400"
].join(" "));

const canSubmit = computed(() =>
  form.value.current && form.value.newPwd && form.value.confirm &&
  matchConfirm.value && allRulesOk.value
);

// envio (store + API)
async function handleSubmit() {
  if (!canSubmit.value || loading.value) return;
  errorMsg.value = "";
  loading.value = true;
  try {
    const response = await auth.changePassword({
      currentPassword: form.value.current,
      newPassword: form.value.newPwd,
    });
    // sucesso
    const payload = { currentPassword: form.value.current, newPassword: form.value.newPwd, response };
    reset();
    emit("submitted", payload);
    emitClose();
  } catch (err) {
    const msg =
      err?.response?.data?.message ||
      err?.response?.data?.error ||
      err?.message ||
      "Não foi possível alterar a senha. Tente novamente.";
    errorMsg.value = msg;
  } finally {
    loading.value = false;
  }
}

function emitClose() {
  reset();
  emit("close");
}
function reset() {
  form.value.current = "";
  form.value.newPwd = "";
  form.value.confirm = "";
  showCurrent.value = showNew.value = showConfirm.value = false;
  touched.value = false;
  errorMsg.value = "";
}
function onBackgroundClick() {
  emitClose();
}
</script>

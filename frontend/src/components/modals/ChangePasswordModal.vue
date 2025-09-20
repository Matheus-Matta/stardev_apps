<template>
  <teleport to="body">
    <div v-if="open">
      <!-- overlay com blur leve -->
      <div class="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm" @click="onBackgroundClick" />

      <div
        class="fixed inset-0 z-[110] grid place-items-center px-4"
        role="dialog" aria-modal="true" aria-labelledby="cp-title"
        @keydown.escape.prevent.stop="emitClose"
      >
        <!-- CARD -->
        <div
          ref="modalRef"
          class="w-full max-w-xl rounded-[22px] bg-white/95 dark:bg-slate-800/95 border border-slate-200 dark:border-slate-700 shadow-2xl ring-1 ring-black/5"
          tabindex="-1"
        >
          <!-- HEADER -->
          <div class="flex items-start justify-between gap-4 px-6 pt-6">
            <div class="flex items-start gap-3">
              <div class="h-9 w-9 rounded-full bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-500 grid place-items-center">
                <Icon name="info" class="text-[20px]" />
              </div>
              <div>
                <h2 id="cp-title" class="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  Alterar senha
                </h2>
                <p class="mt-1 text-[13px] leading-5 text-slate-600 dark:text-slate-300">
                  Defina uma senha forte e exclusiva. Evite palavras comuns e dados pessoais.
                </p>
              </div>
            </div>

            <button
              class="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
              @click="emitClose" aria-label="Fechar"
            >
              <Icon name="close" class="text-[20px] cursor-pointer hover:text-red-400" />
            </button>
          </div>

          <!-- BODY -->
          <form @submit.prevent="handleSubmit" class="px-6 pb-6 pt-4 space-y-5">
            <!-- Senha atual -->
            <div>
              <label class="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-2">Senha atual</label>

              <div
                class="group relative flex items-center rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 pl-4 pr-10
                       focus-within:ring-2 focus-within:ring-blue-500 focus-within:shadow-[0_0_0_4px_rgba(124,58,237,.15)] transition-shadow"
              >
                <Icon name="lock" class="mr-2 text-slate-400 dark:text-slate-300"/>
                <input
                  :type="showCurrent ? 'text' : 'password'"
                  v-model.trim="form.current"
                  @input="touchedCurrent = true"
                  required autocomplete="current-password"
                  class="peer w-full border-0 focus:ring-0 bg-transparent text-[14px] text-slate-900 dark:text-slate-100 placeholder-slate-400"
                  placeholder="Digite sua senha atual"
                />
                  <Icon 
                    :name="showCurrent  ? 'visibility_off' : 'visibility'" 
                    class="absolute right-3 text-slate-400 hover:text-slate-600 dark:text-slate-300 dark:hover:text-slate-100"
                    @click="showCurrent  = !showCurrent " :aria-label="showCurrent  ? 'Ocultar senha' : 'Mostrar senha'"
                   />
              </div>
            </div>

            <!-- Nova senha -->
            <div>
              <label class="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-2">Nova senha</label>

              <div
                class="relative flex items-center rounded-[28px] border
                       border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 pl-4 pr-10
                       focus-within:border-violet-400 focus-within:ring-2 focus-within:ring-blue-500
                       focus-within:shadow-[0_0_0_4px_rgba(124,58,237,.18)] transition"
              >
                <Icon name="lock" class="mr-2 text-slate-400 dark:text-slate-300"/>
                <input
                  :type="showNew ? 'text' : 'password'"
                  v-model="form.newPwd"
                  @input="touchedNew = true"
                  required autocomplete="new-password"
                  class="w-full border-0 focus:ring-0 bg-transparent outline-none text-[14px] text-slate-900 dark:text-slate-100 placeholder-slate-400"
                  placeholder="Crie uma nova senha forte"
                />
                  <Icon 
                    :name="showNew ? 'visibility_off' : 'visibility'" 
                    class="absolute right-3 text-slate-400 hover:text-slate-600 dark:text-slate-300 dark:hover:text-slate-100"
                    @click="showNew = !showNew" :aria-label="showNew ? 'Ocultar senha' : 'Mostrar senha'"
                   />
              </div>

              <div v-if="showValidationNew" class="mt-2">
                <div class="h-2 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-300"
                    :class="barColorClass"
                    :style="{ width: strengthWidth }"
                  ></div>
                </div>
                <p class="mt-2 text-xs" :class="labelClass">{{ strengthLabel }}</p>
              </div>

              <!-- Requisitos – só após digitar -->
              <ul v-if="showValidationNew" class="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                <li v-for="r in rulesChecks" :key="r.key" class="flex items-center">
                  <Icon :name="r.ok ? 'check_circle' : 'radio_button_unchecked'"
                        :class="r.ok ? 'text-emerald-600 mr-1' : 'text-slate-400 mr-1'" />
                  <span :class="r.ok ? 'text-emerald-700 dark:text-emerald-400' : 'text-slate-600 dark:text-slate-300'">
                    {{ r.label }}
                  </span>
                </li>
              </ul>

              <!-- Mensagens condicionais após digitar -->
              <p v-if="showValidationNew && sameAsCurrent" class="mt-2 text-xs text-red-600">
                A nova senha não pode ser igual à senha atual.
              </p>
              <p v-if="showValidationNew && containsUserInfo" class="mt-1 text-xs text-red-600">
                Evite usar seu nome de usuário ou e-mail na senha.
              </p>
            </div>

            <!-- Confirmar senha -->
            <div>
              <label class="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-2">Confirmar nova senha</label>

              <div
                class="group relative flex items-center rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 pl-4 pr-10
                       focus-within:ring-2 focus-within:ring-blue-500 focus-within:shadow-[0_0_0_4px_rgba(124,58,237,.15)] transition-shadow"
              >
                <Icon name="verified_user" class="mr-2 text-slate-400 dark:text-slate-300" />
                <input
                  :type="showConfirm ? 'text' : 'password'"
                  v-model="form.confirm"
                  @input="touchedConfirm = true"
                  required autocomplete="new-password"
                  class="w-full border-0 focus:ring-0 bg-transparent outline-none text-[14px] text-slate-900 dark:text-slate-100 placeholder-slate-400"
                  placeholder="Repita a nova senha"
                />
                  <Icon 
                    :name="showConfirm ? 'visibility_off' : 'visibility'" 
                    class="absolute right-3 text-slate-400 hover:text-slate-600 dark:text-slate-300 dark:hover:text-slate-100"
                    @click="showConfirm = !showConfirm" :aria-label="showConfirm ? 'Ocultar senha' : 'Mostrar senha'"
                   />
              </div>

              <p v-if="touchedConfirm && form.confirm && !matchConfirm" class="mt-2 text-xs text-red-600">
                As senhas não coincidem.
              </p>
            </div>

            <!-- erro da API (só após submit falhar) -->
            <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

            <!-- FOOTER -->
            <div class="flex justify-end gap-3 pt-2">
              <button
                type="button" @click="emitClose"
                class="cursor-pointer px-5 py-1.5 rounded-full border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-100
                       bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                Cancelar
              </button>
              <button
                type="submit" :disabled="!canSubmit || loading"
                class="cursor-pointer px-5 py-1.5 rounded-full text-white disabled:opacity-60 disabled:cursor-not-allowed bg-blue-600 hover:bg-primary-700"
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

// foco inicial ao abrir
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

// flags de interação (corrige “erro antes de digitar”)
const touchedCurrent = ref(false);
const touchedNew = ref(false);
const touchedConfirm = ref(false);

// validações
const minLen = 8;
const hasLower = (s) => /[a-z]/.test(s);
const hasUpper = (s) => /[A-Z]/.test(s);
const hasDigit  = (s) => /\d/.test(s);
const hasSymbol = (s) => /[^A-Za-z0-9]/.test(s);
const notCommon = (s) => {
  const blacklist = ["password", "senha", "admin"];
  return !blacklist.includes((s || "").toLowerCase());
};
const noSequences = (s) => {
  s = (s || "").toString();
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
  if (/(.)\1{2,}/.test(s)) return false;        // aaa
  if (/(\w{2,})\1{1,}/i.test(s)) return false;  // abab
  return true;
};

const notEqualCurrent = computed(() => !form.value.newPwd || form.value.newPwd !== form.value.current);

const progress = computed(() => {
  const s = form.value.newPwd || "";
  if (!s) return 0;
  let p = 0;
  p += Math.min(s.length / minLen, 1) * 1.5;
  if (hasLower(s)) p += 0.5;
  if (hasUpper(s)) p += 0.5;
  if (hasDigit(s)) p += 0.5;
  if (hasSymbol(s)) p += 1.0;
  if (!notCommon(s))  p = Math.min(p, 1.5);
  if (!noSequences(s)) p = Math.min(p, 2);
  return Math.max(0, Math.min(4, p));
});

const strengthWidth = computed(() => `${(progress.value / 4) * 100}%`);
const barColorClass = computed(() => {
  if (!form.value.newPwd) return 'bg-slate-300 dark:bg-slate-600';
  if (score.value <= 1)  return 'bg-red-500';
  if (score.value === 2) return 'bg-yellow-500';
  if (score.value === 3) return 'bg-green-500';
  return 'bg-emerald-600';
});

const userString = computed(() => {
  const name = (props.user?.username || props.user?.name || "").toString().toLowerCase();
  const email = (props.user?.email || "").toString().toLowerCase();
  const local = email.split("@")[0] || "";
  return [name, local].filter(Boolean).join(" ");
});
const containsUserInfo = computed(() => {
  const pwd = (form.value.newPwd || "").toLowerCase();
  const tokens = userString.value.split(/[.\s_\-]+/).filter(t => t && t.length >= 3);
  return !!pwd && tokens.some(t => pwd.includes(t));
});

const rulesChecks = computed(() => {
  const s = form.value.newPwd || "";
  return [
    { key: "len",     ok: s.length >= minLen, label: `Mínimo ${minLen} caracteres` },
    { key: "lower",   ok: hasLower(s),        label: "Letra minúscula" },
    { key: "upper",   ok: hasUpper(s),        label: "Letra maiúscula" },
    { key: "digit",   ok: hasDigit(s),        label: "Número" },
    { key: "symbol",  ok: hasSymbol(s),       label: "Caractere especial" },
    { key: "common",  ok: notCommon(s),       label: "Não é senha comum" },
    { key: "seq",     ok: noSequences(s),     label: "Sem sequências/repetições" },
    { key: "neqcurr", ok: notEqualCurrent.value, label: "Diferente da senha atual" },
  ];
});
const allRulesOk = computed(() =>
  !!form.value.newPwd && rulesChecks.value.every(r => r.ok) && !containsUserInfo.value
);

const matchConfirm = computed(() =>
  !form.value.confirm || form.value.newPwd === form.value.confirm
);
const sameAsCurrent = computed(() =>
  !!form.value.newPwd && form.value.newPwd === form.value.current
);

// força (0-4)
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
const strengthLabel = computed(() => {
  if (!showValidationNew) return "";
  return ["Muito fraca", "Fraca", "Média", "Boa", "Excelente"][score.value];
});
const labelClass = computed(() => {
  if (!showValidationNew) return "text-xs text-slate-500";
  return [
    "text-xs",
    score.value <= 1 ? "text-red-600" : score.value === 2 ? "text-yellow-600" : "text-emerald-700 dark:text-emerald-400"
  ].join(" ");
});

// só mostra validações/força depois que o usuário digitar
const showValidationNew = computed(() => touchedNew.value && !!form.value.newPwd);

const canSubmit = computed(() =>
  !!form.value.current &&
  !!form.value.newPwd &&
  !!form.value.confirm &&
  matchConfirm.value &&
  allRulesOk.value
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
    const payload = { currentPassword: form.value.current, newPassword: form.value.newPwd, response };
    reset();
    emit("submitted", payload);
    emitClose();
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.response?.data?.error || err?.message || "Não foi possível alterar a senha. Tente novamente.";
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
  touchedCurrent.value = touchedNew.value = touchedConfirm.value = false;
  errorMsg.value = "";
}
function onBackgroundClick() { emitClose(); }
</script>


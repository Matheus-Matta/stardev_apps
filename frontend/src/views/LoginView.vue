<script setup lang="ts">
import { ref, computed } from "vue";
import { useAuthStore } from "../store/auth";
import Input from "../components/ui/Input.vue";
import Button from "../components/ui/Button.vue";
import { useRoute } from "vue-router";
import { FwbP } from 'flowbite-vue'

const route = useRoute();
const auth = useAuthStore();

const email = ref("");
const password = ref("");

const errors = ref<{ email?: string; password?: string; general?: string }>({});

function isEmail(v: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
}

function validateEmail() {
  if (!email.value.trim()) return "Email é obrigatório.";
  if (!isEmail(email.value.trim())) return "Informe um email válido.";
  return "";
}
function validatePassword() {
  if (!password.value) return "Senha é obrigatória.";
  if (password.value.length < 3) return "A senha deve ter pelo menos 3 caracteres.";
  return "";
}

function validateAll() {
  errors.value = {
    email: validateEmail() || undefined,
    password: validatePassword() || undefined,
    general: undefined,
  };
  return !errors.value.email && !errors.value.password;
}

const emailMessage = computed(() => errors.value.email || "");
const emailType = computed(() => (errors.value.email ? "error" : "info"));
const passwordMessage = computed(() => errors.value.password || "");
const passwordType = computed(() => (errors.value.password ? "error" : "info"));
const isFormValid = computed(() => {
  return !validateEmail() && !validatePassword();
});

async function submit() {
  errors.value.general = undefined;

  if (!validateAll()) {
    return;
  }

  try {
    const ok = await auth.login(email.value.trim(), password.value);
    if (ok) {
      const nextParam = route.query?.next;
      const next =
        typeof nextParam === "string" && nextParam.startsWith("/")
          ? nextParam
          : "/";
      window.location.href = next;
    } else {
      errors.value.general = auth.error || "Não foi possível acessar. Tente novamente.";
    }
  } catch (e: any) {
    errors.value.general =
      e?.message || "Ocorreu um erro inesperado. Tente novamente.";
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
    <div class="w-full max-w-lg">
      <!-- Título -->
      
      <!-- Card -->
      <h1 class="text-3xl font-semibold text-center text-gray-900 dark:text-white mb-8">
        Login
      </h1>
      <h2 class="text-xl font-semibold text-center text-gray-800 dark:text-gray-300 mb-8">
        Seja bem-vindo!
      </h2>
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
        <form @submit.prevent="submit" class="space-y-5">
          <!-- Email -->
          <Input
            v-model="email"
            type="email"
            label="Email"
            leftIcon="mail"
            placeholder="example@companyname.com"
            :message="emailMessage"
            :messageType="emailType"
            autofocus
            @enter="submit"
          />

          <!-- Password -->
          <Input
            v-model="password"
            type="password"
            label="Password"
            leftIcon="lock"
            placeholder="••••••••"
            :message="passwordMessage"
            :messageType="passwordType"
            @enter="submit"
          />

          <!-- Error geral (backend/exception) -->
          <p
            v-if="errors.general || auth.error"
            class="text-sm text-red-600 dark:text-red-500"
          >
            {{ errors.general || auth.error }}
          </p>

          <!-- Botão -->
          <Button
            :isLoading="auth.loading"
            :disabled="auth.loading || !isFormValid"
            type="submit"
            label="Login"
            color="blue"
            variant="solid"
            extraClass="w-full"
            size="lg"
            block
          />
        </form>
        <fwb-p class="mt-6 text-sm text-gray-600 dark:text-gray-400 text-center">
           Esqueceu sua senha? fale com o administrador.
        </fwb-p>
      </div>
    </div>
  </div>
</template>

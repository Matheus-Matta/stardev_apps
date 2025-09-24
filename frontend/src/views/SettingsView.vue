<!-- src/views/SettingsView.vue (ou AccountView.vue) -->
<script setup>
import { computed, ref } from "vue";
import BaseView from "../layout/BaseView.vue";
import TabsVertical from "../components/ui/TabsVertical.vue";
import TabProfile from "../components/tabs/TabProfile.vue";
import TabAccount from "../components/tabs/TabAccount.vue";
import TabBusiness from "../components/tabs/TabBusiness.vue";
import { useAuthStore } from "../store/auth";
import { useUserStore } from "../store/user";

const auth = useAuthStore();
const userStore = useUserStore();

const user = computed(() => auth.user || {});
const accountId = computed(() => user.value?.Account || ""); // <- id da account

const tab = ref("profile");

const tabs = computed(() => {
  const list = [{ key: "profile", label: "Meu Perfil", icon: "person" }];
  if (userStore.hasPermissions(["view_account"])) {
    list.push({ key: "account", label: "Minha Conta", icon: "settings" });
  }
  if (userStore.hasPermissions(["view_business"])) {
    list.push({ key: "business", label: "Minhas Empresas", icon: "business" });
  } 
  return list;
});
</script>

<template>
  <BaseView>
    <TabsVertical :items="tabs" v-model="tab" class="mt-2">

      <template #panel-profile>
        <TabProfile :user="user" />
      </template>

      <template #panel-account>
        <TabAccount v-if="accountId" :account-id="accountId" />
      </template>

      <template #panel-business>
        <TabBusiness />
      </template>

    </TabsVertical>
  </BaseView>
</template>

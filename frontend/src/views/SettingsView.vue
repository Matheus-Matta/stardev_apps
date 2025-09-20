<script setup>
import { computed, ref } from "vue";
import BaseView from "../layout/BaseView.vue";
import TabsVertical from "../components/ui/TabsVertical.vue";
import TabProfile from "../components/tabs/TabProfile.vue";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const user = computed(() => auth.user || {});

const tab = ref("profile");
const tabs = [{ key: "profile", label: "Meu Perfil", icon: "person" }];
</script>

<template>
  <BaseView>
    <TabsVertical :items="tabs" v-model="tab" class="mt-2">
      <!-- só injeta o componente no slot da aba -->
      <template #panel-profile>
        <TabProfile :user="user" />
      </template>
    </TabsVertical>
  </BaseView>
</template>

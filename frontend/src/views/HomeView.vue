<!-- src/views/HomeView.vue -->
<script setup>
import Card from 'primevue/card'
import Button from 'primevue/button'
import BaseView from '../layout/BaseView.vue'
</script>

<template>
  <BaseView>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
      <!-- Card 1 -->
      <Card class="shadow-md ">
        <template #title>Relatórios</template>
        <template #content>
          <p class="text-sm text-zinc-600 dark:text-zinc-300">
            Acompanhe métricas e estatísticas de desempenho da sua conta em tempo real.
          </p>
        </template>
        <template #footer>
          <Button label="Ver Relatórios" icon="pi pi-chart-bar" text />
        </template>
      </Card>

      <!-- Card 2 -->
      <Card class="shadow-md">
        <template #title>Mensagens</template>
        <template #content>
          <p class="text-sm text-zinc-600 dark:text-zinc-300">
            Acesse as últimas mensagens recebidas e organize suas conversas com a equipe.
          </p>
        </template>
        <template #footer>
          <Button label="Abrir Inbox" icon="pi pi-inbox" text />
        </template>
      </Card>

      <!-- Card 3 -->
      <Card class="shadow-md">
        <template #title>Configurações</template>
        <template #content>
          <p class="text-sm text-zinc-600 dark:text-zinc-300">
            Personalize preferências da conta, ajuste permissões e configure integrações.
          </p>
        </template>
        <template #footer>
          <Button label="Ir para Configurações" icon="pi pi-cog" text />
        </template>
      </Card>

      <!-- Card 4 -->
      <Card class="shadow-md md:col-span-2">
        <template #title>Atividades Recentes</template>
        <template #content>
          <ul class="space-y-2 text-sm text-zinc-700 dark:text-zinc-200">
            <li>• João atualizou a conta "Empresa X".</li>
            <li>• Maria adicionou um novo usuário.</li>
            <li>• Relatório de vendas foi gerado.</li>
          </ul>
        </template>
        <template #footer>
          <Button label="Ver Tudo" icon="pi pi-list" text />
        </template>
      </Card>
    </div>
  </BaseView>
</template>

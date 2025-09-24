<script setup>
import DataTables from "../ui/DataTable.vue";
import Icon from "../ui/Icon.vue";
</script>
<template>
  <div class="space-y-4">
    <div>
      <h2 class="text-base font-semibold text-gray-900 dark:text-white">Unidades de Negócio</h2>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
        Liste, filtre e gerencie suas unidades.
      </p>
    </div>

    <DataTables
      model_name="business"
      :columns="[
        { key:'code',          label:'Código',    sortable:true, width:'w-32' },
        { key:'name',          label:'Nome',      sortable:true },
        { key:'cnpj',          label:'CNPJ',      sortable:true, width:'w-44' },
        { key:'business_type', label:'Tipo',      sortable:true, width:'w-40' },
        { key:'created_at',    label:'Criado em', sortable:true, width:'w-40' },
      ]"
      :columnsLimit="4"          
      :initialPageSize="10"        
      :pageSizes="[10,20,50,100]" 
      @row-click="row => console.log('row', row)"
      @created="payload => console.log('created', payload)"
      @updated="payload => console.log('updated', payload)"
      @error="msg => console.error(msg)"
    />
    <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
      <span><Icon name="info" class="opacity-70" /> Alterações podem exigir atualização da sessão.</span>
    </div>
  </div>
</template>

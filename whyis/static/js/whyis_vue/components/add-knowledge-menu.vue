<template>
<div>
  <div class="dropdown">
    <button class="btn btn-outline-primary dropdown-toggle" type="button" id="addKnowledgeMenu" data-bs-toggle="dropdown" aria-expanded="false" @click="whichAdd = ''">
      <i class="bi bi-list"></i>
    </button>
    <ul class="dropdown-menu" aria-labelledby="addKnowledgeMenu">
      <li><button class="dropdown-item" type="button" @click="whichAdd = 'addLink'">Add Link</button></li>
      <li><button class="dropdown-item" type="button" @click="whichAdd = 'addType'">Add Type</button></li>
      <li><button class="dropdown-item" type="button" @click="whichAdd = 'addAttribute'">Add Attribute</button></li>
    </ul>
  </div>
  <add-link v-if="whichAdd == 'addLink'" v-bind:uri="uri" hideButton="true"></add-link>
  <add-type v-if="whichAdd == 'addType'" v-bind:uri="uri" hideButton="true"></add-type>
  <add-attribute v-if="whichAdd == 'addAttribute'" v-bind:uri="uri" hideButton="true"></add-attribute>
</div>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";

export default Vue.component('add-knowledge-menu', {
    props: ['uri'],
    data: function() {
      return {
        whichAdd: "",
      };
    },
});

</script>

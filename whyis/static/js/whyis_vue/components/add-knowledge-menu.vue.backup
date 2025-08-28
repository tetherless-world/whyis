<template>
<div>
  <md-menu md-size="medium" md-align-trigger>
    <md-button md-menu-trigger v-on:click="whichAdd = ''"><md-icon>menu</md-icon></md-button>

    <md-menu-content>
      <md-menu-item v-on:click="whichAdd = 'addLink'">Add Link</md-menu-item>
      <md-menu-item v-on:click="whichAdd = 'addType'">Add Type</md-menu-item>
      <md-menu-item v-on:click="whichAdd = 'addAttribute'">Add Attribute</md-menu-item>
    </md-menu-content>
  </md-menu>
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

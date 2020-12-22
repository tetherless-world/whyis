<template>
<md-menu md-size="medium" md-align-trigger>
  <md-button md-menu-trigger><md-icon>menu</md-icon></md-button>

  <md-menu-content>
    <md-menu-item><add-link uri="uri"></add-link></md-menu-item>
    <md-menu-item><add-type uri="uri"></add-type></md-menu-item>
    <md-menu-item><add-attribute uri="uri"></add-attribute></md-menu-item>
  </md-menu-content>
</md-menu>
</template>
<style scoped lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";

export default Vue.component('add-knowledge-menu', {
    props: ['uri']
});

</script>

<template>
  <div>
      <p>{{ message }}</p>
      <md-button @click="$emit('apiPost')">Post File</md-button>
      <md-button @click="$emit('apiGet')">Get File</md-button>
  </div>
</template>

<script>
import Vue from 'vue';
import { MdButton } from 'vue-material/dist/components';
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

export default Vue.component('TableControl', {
  data() {
    return {
      message: 'Tabulator File I/O',
    };
  },
  props: {
    method: { type: Function },
  },
});

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style >

</style>

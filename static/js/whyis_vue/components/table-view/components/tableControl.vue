<template>
  <div>
      <md-button @click="$emit('apiPost')">Post File</md-button>
      <md-button @click="$emit('apiGet')">Get File</md-button>
      <md-button @click="$emit('createCol')" disabled>Add Column</md-button>
      <md-button @click="$emit('createRow')" disabled>Add Row</md-button>
  </div>
</template>

<script>
import Vue from 'vue';
import { MdButton } from 'vue-material/dist/components';
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

export default Vue.component('tableControl', {
  props: {
    method: { type: Function },
  },
});

</script>

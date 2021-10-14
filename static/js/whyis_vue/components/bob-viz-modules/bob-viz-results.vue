<template>
<div>
  <!-- <h1>hello</h1> -->
  <yasr :results="results"/>
</div>
</template>
<script>
import Vue from 'vue';

import { mapGetters } from 'vuex';
export default Vue.component('bob-viz-results', {
  computed: {
    ...mapGetters('bobViz', ['results'])
  }
})
</script>

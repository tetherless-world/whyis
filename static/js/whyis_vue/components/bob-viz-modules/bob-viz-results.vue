<template>
<div>
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

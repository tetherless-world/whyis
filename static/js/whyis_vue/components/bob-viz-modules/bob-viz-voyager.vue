
<template>
  <div class="bob-viz-voyager">
    <data-voyager
      v-if="vegaData"
      :data="vegaData"
    />
    <p v-else>
      Select data to open voyager
    </p>
  </div>
</template>

<script>
import Vue from "vue";

import { mapGetters } from "vuex";
export default Vue.component("bob-viz-voyager", {
  computed: {
    ...mapGetters("bobViz", ["vegaData"]),
  }
});
</script>

<style>
.bob-viz-voyager #voyager-embed {
  margin-top: 0;
}
</style>

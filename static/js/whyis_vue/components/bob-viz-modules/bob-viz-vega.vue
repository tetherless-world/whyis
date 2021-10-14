<template>
  <div class="bob-viz-vega">
    <v-jsoneditor
      v-model="baseSpec"
      :options="specJsonEditorOpts"
      style="height: 50%"
    />
    <vega-lite :spec="fullSpec" />
  </div>
</template>

<script>
import Vue from "vue";
import VJsoneditor from "v-jsoneditor";
import {
  getDefaultChart,
} from "utilities/vega-chart";

const { baseSpec: defaultBaseSpec } = getDefaultChart();

import { mapGetters } from "vuex";
export default Vue.component("bob-viz-vega", {
  data: () => ({
    baseSpec: defaultBaseSpec,
    specJsonEditorOpts: {
      mode: "code",
      mainMenuBar: false
    }
  }),
  components: {
    VJsoneditor
  },
  computed: {
    ...mapGetters("bobViz", ["vegaResults"]),
    fullSpec() {
      return {
        ...this.baseSpec,
        data: {
          values: this.vegaResults
        }
      };
    }
  }
});
</script>

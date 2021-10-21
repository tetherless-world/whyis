<template>
  <div class="modular-viz-tool">
    <split-pane
      :default-percent="defaultPercent"
      split="vertical"
    >
      <template slot="paneL">
        <slot name="select"/>
      </template>
      <template slot="paneR">
        <slot name="explore"/>
      </template>
    </split-pane>
  </div>
</template>
<script>
import Vue from 'vue';
import splitPane from 'vue-splitpane';

export default Vue.component('modular-viz-tool', {
  props: {
    defaultPercent: {
      type: Number,
      default: () => 50
    }
  },
  components: {splitPane}
})
</script>

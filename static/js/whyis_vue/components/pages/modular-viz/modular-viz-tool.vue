<template>
  <div class="modular-viz-tool">
    <split-pane
      :default-percent='50'
      split="vertical"
    >
      <template slot="paneL">
        <div>
          Sparql Query Generator
          <slot name="sparql"/>
        </div>
      </template>
      <template slot="paneR">
        <div>
          Sparql Result Interpreter
          <slot name="results"/>
        </div>
      </template>
    </split-pane>
  </div>
</template>
<script>
import Vue from 'vue';
import splitPane from 'vue-splitpane';

export default Vue.component('modular-viz-tool', {
  components: {splitPane}
})
</script>

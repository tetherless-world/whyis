<template>
  <div ref="vegaContainer" class="vega-container"></div>
</template>

<script>
/**
 * Vega visualization component
 * Renders Vega specifications using vega-embed
 * Migrated from Angular directive "vega"
 */
export default {
  name: 'VegaVisualization',
  props: {
    /**
     * Vega specification object
     */
    spec: {
      type: Object,
      required: true
    },
    /**
     * Optional callback to execute after rendering
     */
    then: {
      type: Function,
      default: null
    },
    /**
     * Vega-embed options
     */
    opt: {
      type: Object,
      default: () => ({
        renderer: 'svg'
      })
    }
  },
  data() {
    return {
      view: null,
      error: null
    };
  },
  watch: {
    spec: {
      handler: 'renderVega',
      deep: true
    }
  },
  mounted() {
    this.renderVega();
  },
  beforeDestroy() {
    if (this.view) {
      this.view.finalize();
    }
  },
  methods: {
    /**
     * Render the Vega specification
     */
    async renderVega() {
      if (!this.spec || !this.$refs.vegaContainer) {
        return;
      }

      try {
        // Dynamically import vega-embed (assuming it's available)
        const vegaEmbed = (typeof window !== 'undefined' && window.vegaEmbed) || null;
        
        if (!vegaEmbed) {
          throw new Error('vega-embed is not available. Make sure it is included in the page.');
        }

        // Merge default options with provided options
        const options = {
          renderer: this.opt.renderer || 'svg',
          ...this.opt
        };

        // Embed the visualization
        const result = await vegaEmbed(this.$refs.vegaContainer, this.spec, options);
        
        this.view = result.view;
        this.error = null;

        // Call the optional callback
        if (this.then && typeof this.then === 'function') {
          this.then(result);
        }

        this.$emit('rendered', result);
      } catch (err) {
        console.error('Error rendering Vega visualization:', err);
        this.error = err;
        this.$emit('error', err);
      }
    }
  }
};
</script>

<style scoped>
.vega-container {
  width: 100%;
  height: 100%;
}
</style>

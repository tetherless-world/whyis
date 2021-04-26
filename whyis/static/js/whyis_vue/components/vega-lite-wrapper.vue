<template>
  <div>
    <div v-if="specValidation.valid" v-bind:id="id"></div>
    <p v-else-if="specValidation.valid === false">Invalid Vega-Lite specification.</p>
  </div>
</template>

<script>
import Vue from 'vue'
import vegaLiteSchema from 'vega-lite/build/vega-lite-schema.json'

import debounce from 'utilities/debounce'

import { validate as jsonValidate } from 'jsonschema'


export default Vue.component('vega-lite', {
  data () {
    return {
      id: 'vega-lite',
      specValidation: {}
    }
  },
  props: {
    spec: {
      type: Object,
      default: () => null
    }
  },
  created ()  {
    this.onSpecChange = debounce(this.processSpec, 300)
    this.onSpecChange()
  },
  methods: {
    async plotSpec () {
      // console.debug('plotting spec', this.spec)
      let embedResult = await window.vegaEmbed(`#${this.id}`, this.spec)
      this.$emit('new-vega-view', embedResult.view)
    },
    validateSpec () {
      const validation = jsonValidate(this.spec, vegaLiteSchema)
      if (!validation.valid) {
        console.warn('Invalid spec', validation)
      } else {
        console.debug('spec checks out', validation)
      }
      this.specValidation = validation
    },
    processSpec () {
      this.validateSpec()
      if (this.specValidation.valid) {
        this.plotSpec()
      }
    }
  },
  watch: {
    spec () {
      this.onSpecChange()
    }
  }
})

export { vegaLiteSchema }

</script>

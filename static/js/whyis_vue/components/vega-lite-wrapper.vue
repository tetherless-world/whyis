<template>
  <div>
    <div v-if="specValidation.valid" v-bind:id="id"></div>
    <p v-else>Invalid Vega-Lite specification.</p>
  </div>
</template>

<script>
import Vue from 'vue'
import vegaLiteSchema from 'vega-lite/build/vega-lite-schema.json'

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
  methods: {
    plotSpec () {
      console.debug('plotting new spec', this.spec)
      window.vegaEmbed(`#${this.id}`, this.spec)
    },
    validateSpec () {
      const validation = jsonValidate(this.spec, vegaLiteSchema)
      window.vlood = validation
      if (!validation.valid) {
        console.warn('Invalid spec', validation)
      } else {
        console.log('spec checks out', validation)
      }
      this.specValidation = validation
    }
  },
  watch: {
    spec () {
      this.validateSpec()
      if (this.specValidation.valid) {
        this.plotSpec()
      }
    }
  }
})

export { vegaLiteSchema }

</script>

<template>
  <div>
    <div v-if="specValidation.valid" v-bind:id="id"></div>
    <p v-else>Invalid Vega-Lite specification.</p>
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
  methods: {
    plotSpec () {
      console.debug('plotting spec', this.spec)
      window.vegaEmbed(`#${this.id}`, this.spec)
    },
    validateSpec () {
      const validation = jsonValidate(this.spec, vegaLiteSchema)
      if (!validation.valid) {
        console.warn('Invalid spec', validation)
      } else {
        console.debug('spec checks out', validation)
      }
      this.specValidation = validation
    }
  },
  watch: {
    spec: debounce(function () {
      this.validateSpec()
      if (this.specValidation.valid) {
        this.plotSpec()
      }
    }, 300)
  }
})

export { vegaLiteSchema }

</script>

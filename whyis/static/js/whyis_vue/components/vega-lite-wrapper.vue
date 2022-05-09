<template>
  <div>
    <div v-if="specValidation.valid" v-bind:id="id"></div>
    <p v-else-if="specValidation.valid === false">Invalid Vega-Lite specification.</p>
  </div>
</template>

<script>
import Vue from 'vue'
import vegaLiteSchema from 'vega-lite/build/vega-lite-schema.json'
import embed from 'vega-embed'

import debounce from 'utilities/debounce'

import { validate as jsonValidate } from 'jsonschema'


export default {
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
    },
    dataname: {
      type: String,
      default: () => null
    },
    data: {
      type: Array,
      default: () => null
    },
  },
  created ()  {
    this.onSpecChange = debounce(this.processSpec, 300)
    this.onSpecChange()
  },
  methods: {
    async plotSpec () {
      // Cancel plotting if the component's element no longer exists in dom
      if (!document.body.contains(this.$el)) {
        return
      }
      const result = await embed(`#${this.id}`, this.spec, {})
      if (this.data) {
        const name = this.dataname || ((this.spec || {}).data || {}).name || 'source'
        result.view.insert(name, this.data).resize().run()
      }
      this.$emit('new-vega-view', result.view)
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
}

export { vegaLiteSchema }

</script>

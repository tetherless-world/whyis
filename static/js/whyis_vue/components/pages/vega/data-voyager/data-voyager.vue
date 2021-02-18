<template>
  <div>
    <div id="voyager-embed"></div>
  </div>
</template>

<script>
  import Vue from 'vue'
  import { Voyager, CreateVoyager } from 'datavoyager'
  import 'datavoyager/build/style.css'

  const exampleData = {
    "values": [
      {"fieldA": "A", "fieldB": 28}, {"fieldA": "B", "fieldB": 55}, {"fieldA": "C", "fieldB": 43},
      {"fieldA": "D", "fieldB": 91}, {"fieldA": "E", "fieldB": 81}, {"fieldA": "F", "fieldB": 53},
    ]
  }

  const voyagerConf = {
    showDataSourceSelector: false,
    hideHeader: true,
    hideFooter: true,
  }

  export default {
    props: {
      data: {
        type: Object,
        default: () => null,
      }
    },
    mounted() {
      console.log('data', this.data)
      const container = document.getElementById("voyager-embed")
      this.voyagerInstance = CreateVoyager(container, voyagerConf, undefined)
      const data = this.data
      // const data = exampleData
      this.voyagerInstance.updateData(data)
    }
  };
</script>

<template>
  <div id="voyager-embed"></div>
</template>

<script>
  import Vue from 'vue'
  import { CreateVoyager } from 'datavoyager'
  // import 'datavoyager/dist/static/js/main.21331228'
  import 'datavoyager/dist/static/css/main.a907da23.css'

  export default {
    props: {
      data: {
        type: Object,
        default: () => null,
      }
    },
    mounted() {
      console.log('data', this.data)
      const container = document.getElementById("voyager-embed");
      const config = undefined;
      const data = this.data;
      // const data = {
      //   "values": [
      //     {"fieldA": "A", "fieldB": 28}, {"fieldA": "B", "fieldB": 55}, {"fieldA": "C", "fieldB": 43},
      //     {"fieldA": "D", "fieldB": 91}, {"fieldA": "E", "fieldB": 81}, {"fieldA": "F", "fieldB": 53},
      //     {"fieldA": "G", "fieldB": 19}, {"fieldA": "H", "fieldB": 87}, {"fieldA": "I", "fieldB": 52}
      //   ]
      // };
      const voyagerInstance = CreateVoyager(container, config, data)
    }
  };
</script>

<style scoped>
  #voyager-embed {
    position: fixed;
    background: #fafafa;
    top:0;
    left: 0;
    height: 100vh;
    width: 100vw;
    z-index: 10;

  }
</style>

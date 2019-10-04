<template>
  <div id='app'>
      <p>{{ message }}<p>
      <div id='table-test'></div>
      <button @click="$emit('apiPost')">Post File</button>
      <button @click="$emit('apiGet')">Get File</button>
  </div>
</template>

<script>

export default {
  name: 'MainPage',
  data() {
    return {
      message: 'Tabulator File I/O',
    };
  },
  props: {
    method: { type: Function },
  },
};

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>

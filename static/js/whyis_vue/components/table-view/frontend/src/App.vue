<template>
  <div id="app">
    <MainPage
      @apiPost="testApiPost"
      @apiGet="testApiGet"
    />
  </div>
</template>

<script>
/* eslint-disable */
import MainPage from './components/HelloWorld.vue';

export default {
  components: { MainPage },
  name: 'App',
  methods: {
    testApiPost() {
      this.$parent.testApiPost();
    },
    testApiGet() {
      this.$parent.testApiGet();
    }
  },
};
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

<template>
<div class="accordion">
  <md-toolbar>
    <div class="accordion-toolbar-row" @click="toggleOpen">
      <h3 class="md-title">{{title}}</h3>
      <div class="accordion-icons">
        <md-icon v-show="!open">
          expand_more
        </md-icon>
        <md-icon v-show="open">
          expand_less
        </md-icon>
      </div>
    </div>
  </md-toolbar>
  <div class="accordion-content" v-if="open">
    <slot></slot>
  </div>
</div>
</template>
<script>
import Vue from "vue";

export default Vue.component('accordion', {
  props: {
    startOpen: {
      type: Boolean,
      default: () => false
    },
    title: {
      type: String,
    }
  },
  data() {
    return {
      open: this.startOpen
    }
  },
  methods: {
    toggleOpen() {
      this.open = !this.open
    }
  }

})
</script>

<style scoped>
.accordion-content {
  max-height: 40vh;
  overflow: auto
}
.accordion-toolbar-row {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.accordion .md-toolbar:hover {
  cursor: pointer;
}
</style>


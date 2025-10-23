<template>
<div class="accordion">
  <div class="accordion-header bg-light border" @click="toggleOpen">
    <div class="accordion-toolbar-row p-3">
      <h3 class="h5 mb-0">{{ title }}</h3>
      <div class="accordion-icons">
        <i class="bi bi-chevron-down" v-show="!open"></i>
        <i class="bi bi-chevron-up" v-show="open"></i>
      </div>
    </div>
  </div>
  <div class="accordion-content border border-top-0" v-if="open">
    <div class="p-3">
      <slot></slot>
    </div>
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
  overflow: auto;
}
.accordion-toolbar-row {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.accordion-header:hover {
  cursor: pointer;
  background-color: #f8f9fa !important;
}
</style>


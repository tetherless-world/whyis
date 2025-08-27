<template>
<div class="accordion">
  <div class="bg-primary text-white p-3 rounded-top">
    <div class="accordion-toolbar-row" @click="toggleOpen">
      <h3 class="h5 mb-0">{{title}}</h3>
      <div class="accordion-icons">
        <i class="material-icons" v-show="!open">
          expand_more
        </i>
        <i class="material-icons" v-show="open">
          expand_less
        </i>
      </div>
    </div>
  </div>
  <div class="accordion-content border border-top-0 rounded-bottom p-3" v-if="open">
    <slot></slot>
  </div>
</div>
</template>
<script>

export default {
  name: 'accordion',
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

}
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
.bg-primary:hover {
  cursor: pointer;
}
</style>


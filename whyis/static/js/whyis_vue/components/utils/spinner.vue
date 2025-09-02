<template>
  <div class="spinner" v-show="loading">
    <div v-if="text" style="font-size:1.5rem; font-weight:200; flex:0 0 auto; margin-bottom: 2rem">{{ text }} <br /></div>
    <div style="flex: 0 0 auto;">
      <span class="sync" v-bind:style="[spinnerStyle, spinnerDelay1]"></span>
      <span class="sync" v-bind:style="[spinnerStyle, spinnerDelay2]"></span>
      <span class="sync" v-bind:style="[spinnerStyle, spinnerDelay3]"></span>
    </div> 
  </div>
</template>
<script>
/**
 * Animated loading spinner component with customizable appearance.
 * Displays three bouncing dots with configurable colors, sizes, and text.
 * 
 * @component Spinner
 * @example
 * <Spinner :loading="isLoading" color="#ff0000" size="20px" text="Loading data..." />
 */
import Vue from 'vue'
export default Vue.component('Spinner', {
  props: {
    /**
     * Controls spinner visibility
     * @type {Boolean}
     * @default true
     */
    loading: {
      type: Boolean,
      default: true
    },
    /**
     * Color of the spinning dots
     * @type {String}
     * @default "#08233c"
     */
    color: {
      type: String,
      default: "#08233c"
    },
    /**
     * Size of each spinning dot
     * @type {String}
     * @default "15px"
     */
    size: {
      type: String,
      default: "15px"
    },
    /**
     * Margin between spinning dots
     * @type {String}
     * @default "2px"
     */
    margin: {
      type: String,
      default: "2px"
    },
    /**
     * Border radius of the dots (100% for circles)
     * @type {String}
     * @default "100%"
     */
    radius: {
      type: String,
      default: "100%"
    },
    /**
     * Optional text to display above the spinner
     * @type {String}
     * @default null
     */
    text: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      spinnerStyle: {
        backgroundColor: this.color,
      	height: this.size,
        width: this.size,
        borderRadius: this.radius,
        margin: this.margin,
        display: 'inline-block',
        animationName: 'spinerAnimation',
        animationDuration: '1.25s',
        animationIterationCount: 'infinite',
        animationTimingFunction: 'ease-in-out',
        animationFillMode: 'both'
      },
      spinnerDelay1: {
        animationDelay: '0.07s'
      },
      spinnerDelay2: {
        animationDelay: '0.14s'
      },
      spinnerDelay3: {
        animationDelay: '0.21s'
      }
    };
  }
});

</script>
<style>
.spinner {
  width: 100%;
  height: 80%;
  display: flex;
  align-items: center;
  justify-content: center;
  align-content: center;
  flex-direction: column;
}
@keyframes spinerAnimation {
    33% {
      transform: translateY(10px);
    }
    66% {
      transform: translateY(-10px);
    }
    100% {
     transform: translateY(0);
    }
}
</style>
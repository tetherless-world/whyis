<template>
  <div class="range-slider">
    <div class="md-layout"
        :class="`md-alignment-center-center`"
        style="min-width: max-content">
        <md-button class="md-layout-item" v-on:click="setMin(rangeMin)">Minimize</md-button>
        <input class="md-layout-item" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMin">
        <input class="md-layout-item" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMax">
        <md-button class="md-layout-item" v-on:click="setMax(rangeMax)">Maximize</md-button>
    </div>  
    <input type="range" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMin">
    <input type="range" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMax">
  </div>
</template>
<script>
import Vue from 'vue'
export default Vue.component('range-slider', {
  props: {
    rangeMin: {
      type: String,
      default: "0"
    },
    rangeMax: {
      type: String,
      default: "100"
    },
    externalMin: {
      type: String,
      default: null,
    },
    externalMax: {
      type: String,
      default: null,
    }
  },
  data: function() {
    return {
      minInput: this.rangeMin,
      maxInput: this.rangeMax,
    }
  },
  computed: {
    sliderMin: {
      get: function() {
        return this.minInput;
      },
      set: function(val) {
        var numVal = Number(val);
        if (numVal > Number(this.maxInput)) {
          this.maxInput = val;
        }
        val = numVal.toExponential(2);
        this.minInput = String(val);
        this.$emit('minInput', this.minInput)
      }
    },
    sliderMax: {
      get: function() {
        return this.maxInput;
      },
      set: function(val) {
        var numVal = Number(val);
        if (numVal < Number(this.minInput)) {
          this.minInput = val;
        }
        val = numVal.toExponential(2);
        this.maxInput = String(val);
        this.$emit('maxInput', this.maxInput)
      }
    }
  },
  methods: {
    setMin (value) {
      if (value) {
        this.minInput = value;
      }
      else{
        this.minInput = this.rangeMin
      }
      this.$emit('minInput', this.minInput)
    },
    setMax (value) {
      if (value) {
        this.maxInput = value;
      }
      else{
        this.maxInput = this.rangeMax
      }
      this.$emit('maxInput', this.maxInput)
    }
  },
  mounted: function () {
    this.setMin(this.externalMin);
    this.setMax(this.externalMax);
  },
  watch: {
    externalMin (newVal, oldVal) {
      this.setMin(newVal)
    },
    externalMax (newVal, oldVal){
      this.setMax(newVal)
    },
  }
});

</script>
<style>

.range-slider {
  width: 200px;
  margin: auto;
  text-align: center;
  position: relative;
  height: 6em;
}

.range-slider input[type=range] {
  position: absolute;
  left: 0;
  bottom: 0;
}

input[type=number] {
  border: 1px solid #ddd;
  text-align: center;
  font-size: 1.6em;
  -moz-appearance: textfield;
}

input[type=number]::-webkit-outer-spin-button,
input[type=number]::-webkit-inner-spin-button {
  -webkit-appearance: none;
}

input[type=number]:invalid,
input[type=number]:out-of-range {
  border: 2px solid #ff6347;
}

input[type=range] {
  -webkit-appearance: none;
  width: 100%;
}

input[type=range]:focus {
  outline: none;
}

input[type=range]:focus::-webkit-slider-runnable-track {
  background: #2497e3;
}

input[type=range]:focus::-ms-fill-lower {
  background: #2497e3;
}

input[type=range]:focus::-ms-fill-upper {
  background: #2497e3;
} 

input[type=range]::-webkit-slider-runnable-track {
  width: 100%;
  height: 5px;
  cursor: pointer;
  /* animate: 0.2s; */
  background: #2497e3;
  border-radius: 1px;
  box-shadow: none;
  border: 0;
}

input[type=range]::-webkit-slider-thumb {
  z-index: 2;
  position: relative;
  box-shadow: 0px 0px 0px #000;
  border: 1px solid #2497e3;
  height: 18px;
  width: 18px;
  border-radius: 25px;
  background: #a1d0ff;
  cursor: pointer;
  -webkit-appearance: none;
  margin-top: -7px;
}
</style>
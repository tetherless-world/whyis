<template>
  <div class="range-slider">
    <div class="md-layout"
        :class="`md-alignment-center-center`" 
        style="min-width: max-content; min-height: fit-content"> 
        <md-button class="md-layout-item md-medium-size-20 md-small-size-20 md-xsmall-size-40" v-on:click="setMin(rangeMin)">Minimum</md-button>
        <input class="md-layout-item md-medium-size-20 md-small-size-20 md-xsmall-size-40" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMin">
        <input class="md-layout-item md-medium-size-20 md-small-size-20 md-xsmall-size-40" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMax">
        <md-button class="md-layout-item md-medium-size-20 md-small-size-20 md-xsmall-size-40" v-on:click="setMax(rangeMax)">Maximum</md-button>
    </div>  
    <input class="range-slider" type="range" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMin">
    <input class="range-slider" type="range" v-bind:min=rangeMin v-bind:max=rangeMax step="1" v-model="sliderMax">
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
        if (this.minInput == this.rangeMin){
          this.$emit('minInput', null)
        }
        else{ this.$emit('minInput', this.minInput) }
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
        if (this.maxInput == this.rangeMax){
          this.$emit('maxInput', null)
        }
        else{ this.$emit('maxInput', this.maxInput) }
      }
    }
  },
  methods: {
    setMin (value) {
      if ((!value) || (value == this.rangeMin)){
        this.minInput = this.rangeMin
        this.$emit('minInput', null)
      }
      else {
        this.minInput = value;
        this.$emit('minInput', this.minInput)
      }
    },
    setMax (value) {
      if ((!value) || (value == this.rangeMax)){
        this.maxInput = this.rangeMax
        this.$emit('maxInput', null)
      }
      else {
        this.maxInput = value;
        this.$emit('maxInput', this.maxInput)
      }
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
<style scoped lang="scss">

.range-slider {
  margin: auto;
  text-align: center;
  position: relative;
  height: 6em;
}

.range-slider input[type=range] {
  position: absolute;
  left: 0;
  bottom: 0;
  background: transparent;
  padding-top: 2em;
  pointer-events: none;
}

input[type=range] {
  -webkit-appearance: none;
  -moz-appearance: none;
  width: 70%;
  margin-left: 15%;
  
  &:nth-child(3){
    &::-webkit-slider-runnable-track{
      background-color: transparent;
    }
    &::-moz-range-track {
      background-color: transparent;
    }
  }
}

input[type=range]::-webkit-slider-runnable-track {
  width: 100%;
  height: 5px;
  cursor: pointer;
  background: #2497e3;
  border-radius: 1px;
  border: 0;
}
input[type=range]::-webkit-slider-thumb {
  position: relative;
  border: 1px solid #2497e3;
  height: 18px;
  width: 18px;
  border-radius: 25px;
  background: #a1d0ff;
  cursor: pointer;
  -webkit-appearance: none;
  margin-top: -7px;
  pointer-events: auto;
}

input[type=range]::-moz-range-track {
  width: 100%;
  height: 5px;
  cursor: pointer;
  background: #2497e3;
  border-radius: 1px;
  box-shadow: none;
  border: none;
}
input[type=range]::-moz-range-thumb {
  position: relative;
  border: 1px solid #2497e3;
  height: 18px;
  width: 18px;
  border-radius: 25px;
  background: #a1d0ff;
  cursor: pointer;

  -moz-appearance: none;
  pointer-events: auto;
}

</style>
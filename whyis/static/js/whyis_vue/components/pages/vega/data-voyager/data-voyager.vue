<template>
  <div>
    <div :id="containerId"></div>
  </div>
</template>

<script>
import { CreateVoyager } from "datavoyager";
import "datavoyager/build/style.css";

const voyagerConf = {
  showDataSourceSelector: false,
  hideHeader: true,
  hideFooter: true
};

export default {
  data() {
    return {
      containerId: "voyager-embed"
    };
  },
  props: {
    data: {
      type: Object,
      default: () => null
    },
    spec: {
      type: Object,
      default: () => null
    }
  },
  methods: {
    updateSpec() {
      this.$emit("update:spec", this.voyagerInstance.getSpec());
    },
    createVoyager() {
      const container = document.getElementById(this.containerId);
      this.voyagerInstance = CreateVoyager(container, voyagerConf, undefined);
      this.voyagerInstance.onStateChange(() => this.updateSpec());
      this.voyagerInstance.updateData(this.data);
    }
  },
  watch: {
    data() {
      this.createVoyager();
    }
  },
  mounted() {
    this.createVoyager();
  }
};
</script>

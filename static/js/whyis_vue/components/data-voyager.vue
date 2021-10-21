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
      containerId: "voyager-embed",
      voyagerInstance: null
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
      // this.voyagerInstance.updateData(this.data)
    },
    updateData(data) {
      if (this.voyagerInstance && data) {
        this.voyagerInstance.updateData(data)
      }
    }
  },
  watch: {
    data(data) {
      this.updateData(data)
    }
  },
  mounted() {
    this.createVoyager()
    this.updateData(this.data)
  }
};
</script>

<style>
#voyager-embed {
  background: #fafafa;
  height: 100%;
  width: calc(100% - 2.6rem);
  margin: 30px 1.3rem;
}
</style>

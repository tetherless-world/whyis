<template>
    <md-dialog-confirm class="utility-filter"
      :md-active.sync="active"
      md-title="Filter Option"
      md-content="Let you filter results. <br> This means sending <strong>anonymous</strong> location data, even when no apps are running."
      md-confirm-text="Submit"
      md-cancel-text="Cancel"
      @md-cancel="onCancel"
      @md-confirm="onConfirm" />
</template>

<script>
  import { eventCourier as ec } from '../store';
  export default {
    name: 'FilterBox',
    data () {
      return {
        active: false
      }
    },
    computed: {
      onClose() {
        return ec.$emit('close-filter-box', this.active)
      }
    },
    methods: {
      onConfirm() {
        this.value = 'Agreed'
      },
      onCancel() {
        return ec.$emit('close-filter-box', this.active)
      }
    },
    created() {
      ec.$on('open-filter-box', (data) => {
        return this.active = data
      });
    }
  }
</script>
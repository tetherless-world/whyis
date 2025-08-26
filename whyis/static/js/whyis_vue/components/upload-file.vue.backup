<template>

<md-dialog :md-active.sync="active"  :md-click-outside-to-close="true" @md-clicked-outside="resetDialogBox()">
  <md-dialog-title>Upload File for {{label}}</md-dialog-title>
    <form style="margin:2em;" id="upload_form" enctype="multipart/form-data" novalidate method="post" action="">
      <p>
          <md-radio name="upload_type" v-model="upload_type" checked value="http://purl.org/net/provenance/ns#File">Single File</md-radio>
          <md-radio name="upload_type" v-model="upload_type" value="http://purl.org/dc/dcmitype/Collection">Collection</md-radio>
          <md-radio name="upload_type" v-model="upload_type" value="http://www.w3.org/ns/dcat#Dataset">Dataset</md-radio>
      </p>
      <md-field>
        <label>File</label>
        <md-file name="file" multiple placeholder="Add files here." />
      </md-field>
  </form>
  <md-dialog-actions>
    <md-button @click="resetDialogBox()" class="md-primary" >Close</md-button>
    <md-button form="upload_form" type="submit" class="md-primary">Upload</md-button>
  </md-dialog-actions>
</md-dialog>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";
import axios from 'axios'


export default Vue.component('upload-file', {
    props: ['active', 'label'],
    data: function() {
        return {
          upload_type: "http://purl.org/net/provenance/ns#File"
        };
    },
    methods: {
        // Create dialog boxes
        showDialogBox () {
        this.$emit('update:active', true);
        },
        resetDialogBox(){
            //this.active = false;
            this.$emit('update:active', false);
        },
        onCancel() {
            return this.resetDialogBox();
        },
        onSubmit() {
            this.save()
            .then(() => window.location.reload());
            return this.resetDialogBox();
        }
    },
});

</script>

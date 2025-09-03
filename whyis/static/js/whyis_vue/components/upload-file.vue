<template>
  <!-- Bootstrap Modal -->
  <div class="modal fade" tabindex="-1" :class="{'show': active}" :style="{display: active ? 'block' : 'none'}" v-if="active">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Upload File for {{ label }}</h5>
          <button type="button" class="btn-close" @click="resetDialogBox" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form style="margin:2em;" id="upload_form" enctype="multipart/form-data" novalidate method="post" action="">
            <div class="mb-3">
              <div class="form-check">
                <input class="form-check-input" type="radio" name="upload_type" id="singleFile" 
                       v-model="upload_type" value="http://purl.org/net/provenance/ns#File" checked>
                <label class="form-check-label" for="singleFile">
                  Single File
                </label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" name="upload_type" id="collection" 
                       v-model="upload_type" value="http://purl.org/dc/dcmitype/Collection">
                <label class="form-check-label" for="collection">
                  Collection
                </label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" name="upload_type" id="dataset" 
                       v-model="upload_type" value="http://www.w3.org/ns/dcat#Dataset">
                <label class="form-check-label" for="dataset">
                  Dataset
                </label>
              </div>
            </div>
            
            <div class="mb-3">
              <label for="fileInput" class="form-label">File</label>
              <input class="form-control" type="file" id="fileInput" name="file" multiple>
              <div class="form-text">Add files here.</div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="resetDialogBox()">Close</button>
          <button type="submit" form="upload_form" class="btn btn-primary">Upload</button>
        </div>
      </div>
    </div>
  </div>
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

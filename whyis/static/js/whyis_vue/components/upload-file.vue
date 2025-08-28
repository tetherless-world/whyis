<template>
  <!-- Bootstrap Modal for Vue 3 -->
  <div class="modal fade" :class="{ show: active }" tabindex="-1" v-show="active" @click.self="resetDialogBox()">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Upload File for {{label}}</h5>
          <button type="button" class="btn-close" @click="resetDialogBox()" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form id="upload_form" enctype="multipart/form-data" novalidate method="post" action="">
            <div class="mb-3">
              <label for="upload_type" class="form-label">Upload Type</label><br/>
              <div class="form-check">
                <input class="form-check-input" type="radio" name="upload_type" v-model="upload_type" checked value="http://purl.org/net/provenance/ns#File" id="file-radio">
                <label class="form-check-label" for="file-radio">Single File</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" name="upload_type" v-model="upload_type" value="http://purl.org/dc/dcmitype/Collection" id="collection-radio">
                <label class="form-check-label" for="collection-radio">Collection</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" name="upload_type" v-model="upload_type" value="http://www.w3.org/ns/dcat#Dataset" id="dataset-radio">
                <label class="form-check-label" for="dataset-radio">Dataset</label>
              </div>
            </div>
            <div class="mb-3">
              <label for="file-input" class="form-label">Files</label>
              <input type="file" class="form-control" name="file" multiple id="file-input" placeholder="Add files here.">
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="resetDialogBox()">Close</button>
          <button type="submit" class="btn btn-primary" form="upload_form">Upload</button>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
import axios from 'axios'


export default {
  name: 'upload-file',
    props: ['active', 'label'],
    emits: ['update:active'],
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
}

</script>

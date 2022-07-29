<template>
  <md-dialog :md-active.sync="active"  :md-click-outside-to-close="true">
    <div style="margin:2em">
      <md-dialog-title>Upload Knowledge</md-dialog-title>
      <md-field>
        <label>RDF File</label>
        <md-file v-model="file.name" @md-change="handleFileUpload($event)" placeholder="Upload Knowledge in RDF" />
      </md-field>
      <md-field>
        <label>Format</label>
        <md-select :required="true" v-model="format" name="format" id="format">
          <md-option v-for="f in formats" :value="f">{{f.name}}</md-option>
        </md-select>
      </md-field>
      <md-dialog-options class="md-layout md-gutter md-alignment-center-right">
        <md-button @click.prevent="onCancel" class="md-raised md-layout-item">
          Cancel
        </md-button>
        <md-button v-on:click="onSubmit()" class="md-raised md-layout-item">
          Add
        </md-button>
      </md-dialog-options>
    </div>
  </md-dialog>
</template>
<style scoped lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";
import axios from 'axios'

var formats =  [
    { mimetype: "application/rdf+xml", name: "RDF/XML", extensions: ["rdf"]},
    { mimetype: "application/ld+json", name: 'JSON-LD', extensions: ["json",'jsonld']},
    { mimetype: "text/turtle", name : "Turtle", extensions: ['ttl']},
    { mimetype: "application/trig", name : "TRiG", extensions: ['trig']},
    { mimetype: "application/n-quads", name : "n-Quads", extensions: ['nq','nquads']},
    { mimetype: "application/n-triples", name : "N-Triples", extensions: ['nt','ntriples']},
];

var format_map = {

};

export default Vue.component('upload-knowledge', {
    props: ['active'],
    data: function() {
        return {
            formats: formats,
            file: {name: ''},
            format: null,
            fileobj: "",
            status: false,
            awaitingResolve: false,
            awaitingEntity: false,
        };
    },
    methods: {
        // Create dialog boxes
        showDialogBox () {
            this.active=true;
        },
        resetDialogBox(){
            this.active = false;
            this.$emit('update:active', false);
        },
        onCancel() {
            return this.resetDialogBox();
        },
        onSubmit() {
            this.save()
            .then(() => window.location.reload());
            return this.resetDialogBox();
        },
        handleFileUpload(event) {
            console.log(event);
            this.fileobj = event[0];
            let selectedFormats = this.formats.filter(f =>
                f.extensions.filter(e => this.fileobj.name.endsWith(e)));
            if (selectedFormats.length > 0) {
                this.format = selectedFormats[0];
            } else {
                this.format = null;
            }
        },
        async save() {
            console.log(this.format);
            try {
                const request = {
                  method: 'post',
                  url: `${ROOT_URL}pub`,
                  data: this.fileobj,
                  headers: { 'Content-Type': this.format.mimetype}
                }
                return axios(request)
            } catch(err){
                return alert(err)
            }
        },

    },
});

</script>

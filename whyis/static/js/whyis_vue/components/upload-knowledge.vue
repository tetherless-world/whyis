<template>
  <!-- Bootstrap Modal -->
  <div class="modal fade" tabindex="-1" :class="{'show': active}" :style="{display: active ? 'block' : 'none'}" v-if="active">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Upload Knowledge</h5>
          <button type="button" class="btn-close" @click="onCancel" aria-label="Close"></button>
        </div>
        <div class="modal-body" style="margin:2em">
          <div class="mb-3">
            <label for="rdfFile" class="form-label">RDF File</label>
            <input class="form-control" type="file" id="rdfFile" @change="handleFileUpload($event)" accept=".rdf,.json,.jsonld,.ttl,.trig,.nq,.nquads,.nt,.ntriples">
            <div class="form-text">Upload Knowledge in RDF format</div>
          </div>
          
          <div class="mb-3">
            <label for="format" class="form-label">Format</label>
            <select class="form-select" id="format" v-model="format" required>
              <option value="">Select format...</option>
              <option v-for="f in formats" :key="f.name" :value="f.name">{{ f.name }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click.prevent="onCancel">
            Cancel
          </button>
          <button type="button" class="btn btn-primary" @click="onSubmit()">
            Add
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
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

formats.forEach(function(f) { format_map[f.name] = f; })

export default Vue.component('upload-knowledge', {
    props: ['active'],
    data: function() {
        return {
            formats: formats,
            file: {name: ''},
            format_map: format_map,
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
            this.fileobj = event.target.files[0];
            this.file.name = event.target.files[0] ? event.target.files[0].name : '';
        },
        async save() {
            let format = this.format;
            if (format == null) {
                let selectedFormats = this.formats.filter(f =>
                    f.extensions.filter(e => this.fileobj.name.endsWith(e)));
                if (selectedFormats.length > 0) {
                    console.log("setting format", selectedFormats[0]);
                    format = selectedFormats[0];
                }
            } else {
                format = this.format_map[this.format];
            }
            console.log(this.format);
            try {
                const request = {
                  method: 'post',
                  url: `${ROOT_URL}pub`,
                  data: this.fileobj,
                  headers: { 'Content-Type': format.mimetype}
                }
                console.log(request);
                return axios(request)
            } catch(err){
                return alert(err)
            }
        },

    },
});

</script>

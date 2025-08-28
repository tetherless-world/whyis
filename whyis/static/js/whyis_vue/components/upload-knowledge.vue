<template>
  <!-- Bootstrap Modal for Vue 3 -->
  <div class="modal fade" :class="{ show: active }" tabindex="-1" v-show="active" @click.self="resetDialogBox()">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Upload Knowledge</h5>
          <button type="button" class="btn-close" @click="resetDialogBox()" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="rdf-file" class="form-label">RDF File</label>
            <input type="file" class="form-control" @change="handleFileUpload($event)" placeholder="Upload Knowledge in RDF" id="rdf-file">
            <div class="form-text">{{ file.name }}</div>
          </div>
          <div class="mb-3">
            <label for="format-select" class="form-label">Format</label>
            <select class="form-select" v-model="format" name="format" id="format-select" required>
              <option value="" disabled>Select format</option>
              <option v-for="f in formats" :key="f.name" :value="f.name">{{f.name}}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="onCancel">Cancel</button>
          <button type="button" class="btn btn-primary" @click="onSubmit()">Add</button>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
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

formats.forEach(function(f) { format_map[f.name] = f; });

export default {
    name: 'upload-knowledge',
    props: ['active'],
    emits: ['update:active'],
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
            this.$emit('update:active', true);
        },
        resetDialogBox(){
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
            this.file.name = this.fileobj ? this.fileobj.name : '';
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
}

</script>

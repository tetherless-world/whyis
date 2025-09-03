<template>
  <!-- Bootstrap Modal -->
  <div class="modal fade" id="addKnowledgeModal" tabindex="-1" ref="addKnowledgeModal" aria-labelledby="addKnowledgeModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="addKnowledgeModalLabel">Add Knowledge</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <!-- Knowledge Addition Options -->
          <div class="row g-3">
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-body text-center">
                  <i class="bi bi-file-earmark-arrow-up fs-1 text-primary mb-3"></i>
                  <h6 class="card-title">Upload RDF Knowledge</h6>
                  <p class="card-text">Upload knowledge in RDF format (Turtle, JSON-LD, etc.)</p>
                  <button type="button" class="btn btn-primary" @click="showUploadRDF">
                    Choose Option
                  </button>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-body text-center">
                  <i class="bi bi-plus-circle fs-1 text-success mb-3"></i>
                  <h6 class="card-title">Add Attribute</h6>
                  <p class="card-text">Add data properties and values to this entity</p>
                  <button type="button" class="btn btn-success" @click="showAddAttribute">
                    Choose Option
                  </button>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-body text-center">
                  <i class="bi bi-tag fs-1 text-info mb-3"></i>
                  <h6 class="card-title">Add Type</h6>
                  <p class="card-text">Specify additional types or classes for this entity</p>
                  <button type="button" class="btn btn-info" @click="showAddType">
                    Choose Option
                  </button>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-body text-center">
                  <i class="bi bi-arrow-right-circle fs-1 text-warning mb-3"></i>
                  <h6 class="card-title">Add Relationship</h6>
                  <p class="card-text">Link this entity to other entities in the knowledge base</p>
                  <button type="button" class="btn btn-warning" @click="showAddRelationship">
                    Choose Option
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- RDF Upload Section (initially hidden) -->
          <div v-if="showRDFUpload" class="mt-4 border-top pt-4">
            <h6>Upload RDF Knowledge</h6>
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
            
            <div class="d-flex gap-2">
              <button type="button" class="btn btn-secondary" @click="hideAllForms">
                Back
              </button>
              <button type="button" class="btn btn-primary" @click="onSubmitRDF">
                Upload RDF
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer" v-if="!showRDFUpload">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Cancel
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
            showRDFUpload: false,
            modalInstance: null,
        };
    },
    methods: {
        showUploadRDF() {
            this.showRDFUpload = true;
        },
        showAddAttribute() {
            this.hideModal();
            // For now, show a simple alert indicating this feature
            alert('Add Attribute functionality would go here. This requires a specific entity URI context.');
        },
        showAddType() {
            this.hideModal();
            // For now, show a simple alert indicating this feature
            alert('Add Type functionality would go here. This requires a specific entity URI context.');
        },
        showAddRelationship() {
            this.hideModal();
            // For now, show a simple alert indicating this feature
            alert('Add Relationship functionality would go here. This requires a specific entity URI context.');
        },
        hideAllForms() {
            this.showRDFUpload = false;
        },
        showModal() {
            if (this.$refs.addKnowledgeModal) {
                this.modalInstance = new bootstrap.Modal(this.$refs.addKnowledgeModal);
                this.modalInstance.show();
            }
        },
        hideModal() {
            if (this.modalInstance) {
                this.modalInstance.hide();
            }
        },
        onSubmitRDF() {
            this.save()
            .then(() => {
                this.hideModal();
                window.location.reload();
            })
            .catch(err => {
                console.error('Upload failed:', err);
            });
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
    watch: {
        active: function(newVal) {
            if (newVal) {
                this.$nextTick(() => {
                    this.showModal();
                });
            }
        }
    },
    mounted() {
        // Set up modal event listeners
        if (this.$refs.addKnowledgeModal) {
            this.$refs.addKnowledgeModal.addEventListener('hidden.bs.modal', () => {
                this.$emit('update:active', false);
                this.showRDFUpload = false;
            });
        }
    }
});

</script>

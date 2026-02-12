<template>
  <div class="new-nanopub-form">
    <div class="form-group">
      <label>Graph</label>
      <select v-model="currentGraph" class="form-control">
        <option v-for="graph in graphs" :key="graph" :value="graph">
          {{ graph }}
        </option>
      </select>
    </div>

    <div class="form-group">
      <label>Format</label>
      <select v-model="selectedFormat" class="form-control">
        <option v-for="format in formatOptions" :key="format.extension" :value="format">
          {{ format.label }} ({{ format.extension }})
        </option>
      </select>
    </div>

    <div class="form-group">
      <label>Content</label>
      <textarea
        v-model="graphContent"
        class="form-control"
        rows="10"
        :placeholder="`Enter ${currentGraph} content in ${selectedFormat.label} format`"
      ></textarea>
    </div>

    <div class="form-group">
      <label>Upload File</label>
      <input
        type="file"
        @change="handleFileUpload"
        class="form-control-file"
        accept=".ttl,.rdf,.jsonld,.json,.nt,.nq,.trig"
      />
    </div>

    <div class="form-actions">
      <button @click="handleSave" class="btn btn-primary" :disabled="!canSave">
        {{ verb || 'Save' }}
      </button>
      <button v-if="editing" @click="handleCancel" class="btn btn-secondary">
        Cancel
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
  </div>
</template>

<script>
import { getFormatByExtension, getFormatFromFilename } from '../utilities/formats';

export default {
  name: 'NewNanopub',
  props: {
    nanopub: {
      type: Object,
      required: true
    },
    verb: {
      type: String,
      default: 'Save'
    },
    editing: {
      type: [Boolean, String],
      default: false
    }
  },
  data() {
    return {
      currentGraph: 'assertion',
      graphs: ['assertion', 'provenance', 'pubinfo'],
      selectedFormat: null,
      formatOptions: [],
      graphContent: '',
      error: null
    };
  },
  computed: {
    canSave() {
      return !!(this.graphContent && this.graphContent.trim().length > 0);
    },
    isEditing() {
      return this.editing === true || this.editing === 'true';
    }
  },
  created() {
    this.initializeFormats();
    this.loadNanopubContent();
  },
  watch: {
    currentGraph(newGraph) {
      this.loadGraphContent(newGraph);
    },
    nanopub: {
      handler() {
        this.loadNanopubContent();
      },
      deep: true
    }
  },
  methods: {
    initializeFormats() {
      // Get common RDF formats
      const formats = [
        getFormatByExtension('ttl'),
        getFormatByExtension('rdf'),
        getFormatByExtension('jsonld'),
        getFormatByExtension('nt'),
        getFormatByExtension('nq'),
        getFormatByExtension('trig')
      ].filter(Boolean);

      this.formatOptions = formats;
      this.selectedFormat = formats[0] || { extension: 'ttl', label: 'Turtle', mimetype: 'text/turtle' };
    },
    loadNanopubContent() {
      if (!this.nanopub) return;
      
      // Load content for current graph from nanopub
      this.loadGraphContent(this.currentGraph);
    },
    loadGraphContent(graphName) {
      if (!this.nanopub || !this.nanopub.resource) return;

      const resource = this.nanopub.resource;
      const graphData = resource[graphName];

      if (graphData) {
        // Convert graph data to string representation
        // This is a simplified version - full implementation would serialize properly
        if (typeof graphData === 'string') {
          this.graphContent = graphData;
        } else {
          this.graphContent = JSON.stringify(graphData, null, 2);
        }
      } else {
        this.graphContent = '';
      }
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.graphContent = e.target.result;
        
        // Detect format from filename
        const format = getFormatFromFilename(file.name);
        if (format) {
          const matchingFormat = this.formatOptions.find(f => f.extension === format.extension);
          if (matchingFormat) {
            this.selectedFormat = matchingFormat;
          }
        }
      };
      reader.onerror = () => {
        this.error = 'Failed to read file';
      };
      reader.readAsText(file);
    },
    handleSave() {
      if (!this.canSave) return;

      try {
        // Update the nanopub with the graph content
        if (!this.nanopub.resource) {
          this.nanopub.resource = {};
        }
        
        this.nanopub.resource[this.currentGraph] = this.graphContent;
        
        // Emit save event to parent
        this.$emit('save', this.nanopub);
        
        // Clear form if not editing
        if (!this.isEditing) {
          this.graphContent = '';
        }
      } catch (err) {
        this.error = 'Failed to save: ' + err.message;
      }
    },
    handleCancel() {
      this.$emit('cancel');
      
      // Reset editing state on nanopub
      if (this.nanopub) {
        this.$set(this.nanopub, 'editing', false);
      }
    },
    isArray(variable) {
      if (variable === undefined || variable === null) return false;
      if (typeof variable === 'string' || variable instanceof String) return false;
      return typeof variable === 'Array' || variable instanceof Array || variable.constructor === Array;
    }
  }
};
</script>

<style scoped>
.new-nanopub-form {
  padding: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  color: #495057;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  color: #495057;
  background-color: #fff;
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-control-file {
  display: block;
  width: 100%;
}

textarea.form-control {
  resize: vertical;
  font-family: monospace;
}

.form-actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1.5;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-primary {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
  border-color: #004085;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover {
  background-color: #5a6268;
  border-color: #545b62;
}

.alert {
  padding: 0.75rem 1.25rem;
  margin-top: 1rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}
</style>

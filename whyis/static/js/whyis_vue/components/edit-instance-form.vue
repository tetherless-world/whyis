<template>
  <div class="edit-instance-form">
    <div v-if="loading" class="loading">Loading instance data...</div>
    
    <form v-else @submit.prevent="submit">
      <div v-if="instance" class="form-content">
        <div class="form-group">
          <label>Instance ID</label>
          <input 
            v-model="instance['@id']" 
            class="form-control" 
            type="text" 
            disabled
          />
        </div>
        
        <div v-if="instance['@type']" class="form-group">
          <label>Type</label>
          <div class="type-list">
            <span v-for="(type, index) in listify(instance['@type'])" :key="index" class="badge">
              {{ type }}
            </span>
          </div>
        </div>
        
        <div v-if="instance.label" class="form-group">
          <label>Label</label>
          <input 
            v-model="instance.label[0]['@value']" 
            class="form-control" 
            type="text"
          />
        </div>
        
        <div v-if="instance.description" class="form-group">
          <label>Description</label>
          <textarea 
            v-model="instance.description[0]['@value']" 
            class="form-control" 
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>References</label>
          <input 
            v-model="referencesInput" 
            class="form-control" 
            type="text"
            placeholder="Comma-separated URIs"
          />
        </div>
        
        <div class="form-group">
          <label>Quoted From</label>
          <input 
            v-model="quotedFromInput" 
            class="form-control" 
            type="text"
            placeholder="Comma-separated URIs"
          />
        </div>
        
        <div class="form-group">
          <label>Derived From</label>
          <input 
            v-model="derivedFromInput" 
            class="form-control" 
            type="text"
            placeholder="Comma-separated URIs"
          />
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="$emit('cancel')">
            Cancel
          </button>
        </div>
        
        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import { makeID } from '../utilities/id-generator';
import { resolveURI } from '../utilities/uri-resolver';
import { postNewNanopub } from '../utilities/nanopub';
import { listify } from '../utilities/rdf-utils';

export default {
  name: 'EditInstanceForm',
  props: {
    nodeUri: {
      type: String,
      required: true
    },
    lodPrefix: {
      type: String,
      required: true
    },
    rootUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      saving: false,
      error: null,
      referencesInput: '',
      quotedFromInput: '',
      derivedFromInput: '',
      nanopub: {
        '@context': {
          '@vocab': `${this.lodPrefix}/`,
          '@base': `${this.lodPrefix}/`,
          'xsd': 'http://www.w3.org/2001/XMLSchema#',
          'whyis': 'http://vocab.rpi.edu/whyis/',
          'np': 'http://www.nanopub.org/nschema#',
          'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
          'sio': 'http://semanticscience.org/resource/',
          'isAbout': { '@id': 'http://semanticscience.org/resource/isAbout', '@type': '@uri' },
          'dc': 'http://purl.org/dc/terms/',
          'prov': 'http://www.w3.org/ns/prov#',
          'references': { '@id': 'dc:references', '@type': '@uri' },
          'quoted from': { '@id': 'prov:wasQuotedFrom', '@type': '@uri' },
          'derived from': { '@id': 'prov:wasDerivedFrom', '@type': '@uri' },
          'label': { '@id': 'rdfs:label', '@type': 'xsd:string' },
          'description': { '@id': 'dc:description', '@type': 'xsd:string' }
        },
        '@id': this.nodeUri,
        '@graph': {
          '@id': this.nodeUri,
          '@type': 'np:Nanopublication',
          'np:hasAssertion': {
            '@id': `${this.nodeUri}_assertion`,
            '@type': 'np:Assertion',
            '@graph': {
              '@id': this.nodeUri
            }
          },
          'np:hasProvenance': {
            '@id': `${this.nodeUri}_provenance`,
            '@type': 'np:Provenance',
            '@graph': {
              '@id': `${this.nodeUri}_assertion`,
              'references': [],
              'quoted from': [],
              'derived from': []
            }
          },
          'np:hasPublicationInfo': {
            '@id': `${this.nodeUri}_pubinfo`,
            '@type': 'np:PublicationInfo',
            '@graph': {
              '@id': this.nodeUri
            }
          }
        }
      }
    };
  },
  computed: {
    instance() {
      return this.nanopub['@graph']['np:hasAssertion']['@graph'];
    },
    provenance() {
      return this.nanopub['@graph']['np:hasProvenance']['@graph'];
    }
  },
  watch: {
    referencesInput(val) {
      this.provenance.references = this.parseURIList(val);
    },
    quotedFromInput(val) {
      this.provenance['quoted from'] = this.parseURIList(val);
    },
    derivedFromInput(val) {
      this.provenance['derived from'] = this.parseURIList(val);
    }
  },
  async mounted() {
    await this.loadInstanceData();
  },
  methods: {
    listify,
    parseURIList(input) {
      if (!input || !input.trim()) return [];
      return input.split(',').map(uri => ({ '@id': uri.trim() })).filter(item => item['@id']);
    },
    formatURIList(uriArray) {
      if (!uriArray || uriArray.length === 0) return '';
      return uriArray.map(item => item['@id']).join(', ');
    },
    async loadInstanceData() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`${this.rootUrl}about`, {
          params: {
            view: 'describe',
            uri: this.nodeUri
          }
        });
        
        const elements = response.data;
        
        // Find the element matching our node URI
        for (const element of elements) {
          if (element['@id'] === this.nodeUri) {
            // Merge properties into instance
            for (const property in element) {
              this.instance[property] = element[property];
            }
            break;
          }
        }
        
        // Initialize input fields from provenance
        if (this.provenance.references) {
          this.referencesInput = this.formatURIList(this.provenance.references);
        }
        if (this.provenance['quoted from']) {
          this.quotedFromInput = this.formatURIList(this.provenance['quoted from']);
        }
        if (this.provenance['derived from']) {
          this.derivedFromInput = this.formatURIList(this.provenance['derived from']);
        }
        
        this.loading = false;
      } catch (err) {
        this.error = err.message || 'Failed to load instance data';
        this.loading = false;
      }
    },
    async submit() {
      this.saving = true;
      this.error = null;
      
      try {
        // Set isAbout relationship
        this.nanopub['@graph'].isAbout = { '@id': this.instance['@id'] };
        
        // Resolve the entity URI
        const entityURI = resolveURI(this.instance['@id'], this.nanopub['@context']);
        
        // Save the nanopub
        await postNewNanopub(this.nanopub);
        
        // Redirect to the updated instance
        window.location.href = `${this.rootUrl}about?uri=${encodeURIComponent(entityURI)}`;
      } catch (err) {
        this.error = err.message || 'Failed to save changes';
        this.saving = false;
      }
    }
  }
};
</script>

<style scoped>
.edit-instance-form {
  max-width: 800px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.type-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: #007bff;
  color: white;
  border-radius: 3px;
  font-size: 0.875rem;
}

.form-actions {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.mt-3 {
  margin-top: 1rem;
}
</style>

<template>
  <div class="new-instance-form">
    <form @submit.prevent="submit">
      <div class="form-group">
        <label>Instance Type</label>
        <input 
          v-model="instance['@type']" 
          class="form-control" 
          type="text" 
          required
        />
      </div>
      
      <div class="form-group">
        <label>Label</label>
        <input 
          v-model="instance.label['@value']" 
          class="form-control" 
          type="text" 
          required
        />
      </div>
      
      <div class="form-group">
        <label>Description</label>
        <textarea 
          v-model="instance.description['@value']" 
          class="form-control" 
          rows="3"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label>References (comma-separated URIs)</label>
        <input 
          v-model="referencesInput" 
          class="form-control" 
          type="text"
          placeholder="http://example.org/resource1, http://example.org/resource2"
        />
      </div>
      
      <div class="form-group">
        <label>Quoted From (comma-separated URIs)</label>
        <input 
          v-model="quotedFromInput" 
          class="form-control" 
          type="text"
          placeholder="http://example.org/quote1, http://example.org/quote2"
        />
      </div>
      
      <div class="form-group">
        <label>Derived From (comma-separated URIs)</label>
        <input 
          v-model="derivedFromInput" 
          class="form-control" 
          type="text"
          placeholder="http://example.org/source1, http://example.org/source2"
        />
      </div>
      
      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Creating...' : 'Create Instance' }}
        </button>
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')">
          Cancel
        </button>
      </div>
      
      <div v-if="error" class="alert alert-danger mt-3">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script>
import { makeID, generateUUID } from '../utilities/id-generator';
import { resolveURI } from '../utilities/uri-resolver';
import { postNewNanopub } from '../utilities/nanopub';

export default {
  name: 'NewInstanceForm',
  props: {
    nodeType: {
      type: String,
      default: ''
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
    const npId = makeID();
    const instanceId = makeID();
    
    return {
      loading: false,
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
        '@id': `urn:${npId}`,
        '@graph': {
          '@id': `urn:${npId}`,
          '@type': 'np:Nanopublication',
          'np:hasAssertion': {
            '@id': `urn:${npId}_assertion`,
            '@type': 'np:Assertion',
            '@graph': {
              '@id': instanceId,
              '@type': [this.nodeType || 'http://www.w3.org/2002/07/owl#Thing'],
              'label': { '@value': '' },
              'description': { '@value': '' }
            }
          },
          'np:hasProvenance': {
            '@id': `urn:${npId}_provenance`,
            '@type': 'np:Provenance',
            '@graph': {
              '@id': `urn:${npId}_assertion`,
              'references': [],
              'quoted from': [],
              'derived from': []
            }
          },
          'np:hasPublicationInfo': {
            '@id': `urn:${npId}_pubinfo`,
            '@type': 'np:PublicationInfo',
            '@graph': {
              '@id': `urn:${npId}`
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
  methods: {
    parseURIList(input) {
      if (!input || !input.trim()) return [];
      return input.split(',').map(uri => ({ '@id': uri.trim() })).filter(item => item['@id']);
    },
    async submit() {
      this.loading = true;
      this.error = null;
      
      try {
        // Set isAbout relationship
        this.nanopub['@graph'].isAbout = { '@id': this.instance['@id'] };
        
        // Resolve the entity URI
        const entityURI = resolveURI(this.instance['@id'], this.nanopub['@context']);
        
        // Save the nanopub
        await postNewNanopub(this.nanopub);
        
        // Redirect to the new instance
        window.location.href = `${this.rootUrl}about?uri=${encodeURIComponent(entityURI)}`;
      } catch (err) {
        this.error = err.message || 'Failed to create instance';
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.new-instance-form {
  max-width: 800px;
  margin: 0 auto;
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

<template>
  <div class="search-results">
    <div v-if="loading" class="loading">
      <spinner :loading="true" text="Loading search results..." />
    </div>
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    <div v-else-if="entities && entities.length > 0" class="results-list">
      <div v-for="entity in entities" :key="entity.about || entity.uri" class="result-item">
        <slot name="result" :entity="entity">
          <!-- Default result display -->
          <div class="entity-result">
            <h4>
              <a :href="`${rootUrl}about?uri=${encodeURIComponent(entity.about || entity.uri)}`">
                {{ entity.label || entity.title || getLocalPart(entity.about || entity.uri) }}
              </a>
            </h4>
            <p v-if="entity.description" class="description">
              {{ entity.description }}
            </p>
            <div v-if="entity.types && entity.types.length > 0" class="types">
              <span v-for="type in entity.types" :key="type" class="badge badge-secondary me-1">
                {{ getLocalPart(type) }}
              </span>
            </div>
          </div>
        </slot>
      </div>
    </div>
    <div v-else class="no-results">
      <p>No results found for "{{ query }}"</p>
    </div>
  </div>
</template>

<script>
/**
 * SearchResult component - displays search results
 * Migrated from Angular directive "searchResult"
 * @component
 */
import axios from 'axios';
import Spinner from './utils/spinner.vue';

export default {
  name: 'SearchResult',
  
  components: {
    Spinner
  },
  
  props: {
    /**
     * The search query
     */
    query: {
      type: String,
      required: true
    },
    
    /**
     * Pre-loaded results (if available from server)
     */
    results: {
      type: Array,
      default: null
    }
  },
  
  data() {
    return {
      entities: null,
      loading: false,
      error: null,
      rootUrl: typeof window !== 'undefined' ? window.ROOT_URL : '/'
    };
  },
  
  watch: {
    query: {
      immediate: true,
      handler(newQuery) {
        // Only fetch if we don't already have results from props or global
        if (newQuery && !this.results && !(typeof window !== 'undefined' && window.RESULTS)) {
          this.fetchResults();
        }
      }
    }
  },
  
  created() {
    // Check if results were provided (from global RESULTS variable)
    if (this.results) {
      this.entities = this.results;
    } else if (typeof window !== 'undefined' && window.RESULTS) {
      this.entities = window.RESULTS;
    }
    // Note: fetchResults will be called by the watcher if query is set
  },
  
  methods: {
    /**
     * Fetch search results from the API
     */
    async fetchResults() {
      if (!this.query) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('searchApi', {
          params: { query: this.query },
          responseType: 'json'
        });
        
        this.entities = response.data || [];
      } catch (err) {
        console.error('Error fetching search results:', err);
        this.error = 'Failed to load search results. Please try again.';
        this.entities = [];
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Get the local part of a URI for display
     */
    getLocalPart(uri) {
      if (!uri) return '';
      const parts = uri.split(/[#\/]/);
      return parts[parts.length - 1] || uri;
    }
  }
};
</script>

<style scoped>
.search-results {
  margin: 20px 0;
}

.result-item {
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.result-item:last-child {
  border-bottom: none;
}

.entity-result h4 {
  margin: 0 0 10px 0;
  font-size: 1.2em;
}

.entity-result h4 a {
  color: #08233c;
  text-decoration: none;
}

.entity-result h4 a:hover {
  text-decoration: underline;
}

.description {
  color: #666;
  margin: 10px 0;
}

.types {
  margin-top: 10px;
}

.loading, .no-results {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.alert {
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid transparent;
  border-radius: 4px;
}

.alert-danger {
  color: #a94442;
  background-color: #f2dede;
  border-color: #ebccd1;
}
</style>

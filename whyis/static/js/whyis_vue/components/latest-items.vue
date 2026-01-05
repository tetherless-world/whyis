<template>
  <div class="latest-items">
    <div v-if="loading" class="loading">
      <spinner :loading="true" text="Loading latest items..." />
    </div>
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    <div v-else-if="entities && entities.length > 0" class="items-list">
      <div v-for="entity in entities" :key="entity.about" class="latest-item">
        <slot name="item" :entity="entity">
          <!-- Default item display -->
          <div class="entity-item">
            <h4>
              <a :href="`${rootUrl}about?uri=${encodeURIComponent(entity.about)}`">
                {{ entity.label || getLocalPart(entity.about) }}
              </a>
            </h4>
            <p v-if="entity.description" class="description">
              {{ entity.description }}
            </p>
            <div class="metadata">
              <span v-if="entity.fromNow" class="timestamp">
                Updated {{ entity.fromNow }}
              </span>
              <span v-if="entity.types && entity.types.length > 0" class="types">
                <span v-for="type in entity.types" :key="type" class="badge badge-info ms-2">
                  {{ getLocalPart(type) }}
                </span>
              </span>
            </div>
          </div>
        </slot>
      </div>
    </div>
    <div v-else class="no-items">
      <p>No recent items available</p>
    </div>
  </div>
</template>

<script>
/**
 * Latest component - displays latest/recent items
 * Migrated from Angular directive "latest"
 * @component
 */
import axios from 'axios';
import { getLabel } from '../utilities/label-fetcher';
import Spinner from './utils/spinner.vue';

export default {
  name: 'LatestItems',
  
  components: {
    Spinner
  },
  
  props: {
    /**
     * Maximum number of items to display
     */
    limit: {
      type: Number,
      default: null
    }
  },
  
  data() {
    return {
      entities: [],
      loading: false,
      error: null,
      rootUrl: typeof window !== 'undefined' ? window.ROOT_URL : '/'
    };
  },
  
  created() {
    this.fetchLatest();
  },
  
  methods: {
    /**
     * Fetch latest items from the API
     */
    async fetchLatest() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`${this.rootUrl}?view=latest`, {
          responseType: 'json'
        });
        
        let entities = response.data || [];
        
        // Process each entity
        entities.forEach(entity => {
          // Calculate relative time if moment is available
          if (entity.updated && typeof moment !== 'undefined' && moment.utc) {
            try {
              entity.fromNow = moment.utc(entity.updated).local().fromNow();
            } catch (err) {
              console.warn('Error formatting date with moment:', err);
            }
          }
          
          // Fetch labels for entities if needed
          if (entity.about) {
            getLabel(entity.about, this.rootUrl).then(label => {
              entity.label = label;
            }).catch(err => {
              console.warn('Error fetching label:', err);
            });
          }
        });
        
        // Apply limit if specified
        if (this.limit && this.limit > 0) {
          entities = entities.slice(0, this.limit);
        }
        
        this.entities = entities;
      } catch (err) {
        console.error('Error fetching latest items:', err);
        this.error = 'Failed to load latest items. Please try again.';
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
    },
    
    /**
     * Get URL for an entity
     */
    getURL(entity) {
      return entity.about;
    }
  }
};
</script>

<style scoped>
.latest-items {
  margin: 20px 0;
}

.latest-item {
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.latest-item:last-child {
  border-bottom: none;
}

.entity-item h4 {
  margin: 0 0 10px 0;
  font-size: 1.2em;
}

.entity-item h4 a {
  color: #08233c;
  text-decoration: none;
}

.entity-item h4 a:hover {
  text-decoration: underline;
}

.description {
  color: #666;
  margin: 10px 0;
}

.metadata {
  margin-top: 10px;
  font-size: 0.9em;
  color: #888;
}

.timestamp {
  font-style: italic;
}

.types {
  margin-left: 10px;
}

.loading, .no-items {
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

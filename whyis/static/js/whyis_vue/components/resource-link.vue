<template>
  <a :href="linkUrl" :title="displayLabel">
    {{ displayLabel }}
  </a>
</template>

<script>
/**
 * ResourceLink component - displays a link to a resource with its label
 * Migrated from Angular directive "resourceLink"
 * @component
 */
import { getLabel, getLabelSync } from '../utilities/label-fetcher';

export default {
  name: 'ResourceLink',
  
  props: {
    /**
     * The URI of the resource to link to
     */
    uri: {
      type: String,
      required: true
    },
    
    /**
     * Optional label to display (if not provided, will be fetched)
     */
    label: {
      type: String,
      default: null
    }
  },
  
  data() {
    return {
      fetchedLabel: null,
      rootUrl: typeof window !== 'undefined' ? window.ROOT_URL : '/'
    };
  },
  
  computed: {
    /**
     * The URL to link to (uses root URL + about page with uri parameter)
     */
    linkUrl() {
      return `${this.rootUrl}about?uri=${encodeURIComponent(this.uri)}`;
    },
    
    /**
     * The label to display - uses provided label, fetched label, or synced label
     */
    displayLabel() {
      if (this.label) {
        return this.label;
      }
      if (this.fetchedLabel) {
        return this.fetchedLabel;
      }
      return getLabelSync(this.uri);
    }
  },
  
  watch: {
    uri: {
      immediate: true,
      handler(newUri) {
        if (newUri && !this.label) {
          this.fetchLabel();
        }
      }
    }
  },
  
  methods: {
    /**
     * Fetch the label for the resource
     */
    async fetchLabel() {
      try {
        this.fetchedLabel = await getLabel(this.uri, this.rootUrl);
      } catch (error) {
        console.warn(`Failed to fetch label for ${this.uri}:`, error);
      }
    }
  }
};
</script>

<template>
  <div class="position-relative">
    <div class="autocomplete-wrapper" ref="wrapper">
      <!-- Input Field -->
      <div class="position-relative">
        <input
          ref="input"
          v-model="searchQuery"
          type="text"
          class="form-control form-control-lg"
          placeholder="Search knowledge base..."
          @input="onInput"
          @focus="onFocus"
          @blur="onBlur"
          @keydown="onKeydown"
          autocomplete="off"
        />
        
        <!-- Loading indicator -->
        <div 
          v-if="loading" 
          class="position-absolute top-50 end-0 translate-middle-y pe-3"
        >
          <div class="spinner-border spinner-border-sm" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>

      <!-- Dropdown List -->
      <div
        v-show="showDropdown && (filteredOptions.length > 0 || searchQuery.length >= 3)"
        class="dropdown-menu show position-absolute w-100 mt-1"
        style="max-height: 300px; overflow-y: auto; z-index: 1050;"
      >
        <!-- Search for option -->
        <button
          v-if="searchQuery.length >= 3"
          type="button"
          class="dropdown-item d-flex align-items-center fw-bold"
          :class="{ active: highlightedIndex === -1 }"
          @click="searchFor"
          @mouseenter="highlightedIndex = -1"
        >
          <i class="bi bi-search me-2"></i>
          <span>Search for "{{ searchQuery }}"</span>
        </button>
        
        <!-- Divider if there are results -->
        <div v-if="filteredOptions.length > 0" class="dropdown-divider"></div>
        
        <!-- Options List -->
        <template v-if="filteredOptions.length > 0">
          <button
            v-for="(option, index) in filteredOptions"
            :key="option.node || index"
            type="button"
            class="dropdown-item d-flex align-items-center"
            :class="{ active: index === highlightedIndex }"
            @click="selectOption(option)"
            @mouseenter="highlightedIndex = index"
          >
            <div>
              <span>{{ option.prefLabel || option.label }}</span>
              <span v-if="option.label && option.label !== option.prefLabel" class="text-muted ms-1">({{ option.label }})</span>
            </div>
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import axios from 'axios';

export default Vue.component('search-autocomplete', {
    data: () => ({
      searchQuery: '',
      filteredOptions: [],
      showDropdown: false,
      loading: false,
      highlightedIndex: -1,
      debounceTimer: null
    }),
    methods: {
        async resolveEntity(query) {
            if (query && query.length > 2) {
                try {
                    const response = await axios.get('/', {
                        params: { view: 'resolve', term: query + "*" },
                        responseType: 'json'
                    });
                    return response.data || [];
                } catch (error) {
                    console.error('Error resolving entities:', error);
                    return [];
                }
            } else {
                return [];
            }
        },
        
        onInput() {
          this.debouncedSearch();
        },
        
        onFocus() {
          if (this.searchQuery.length >= 3) {
            this.showDropdown = true;
          }
        },
        
        onBlur() {
          // Delay hiding dropdown to allow for clicks
          setTimeout(() => {
            this.showDropdown = false;
            this.highlightedIndex = -1;
          }, 200);
        },
        
        onKeydown(event) {
          switch (event.key) {
            case 'ArrowDown':
              event.preventDefault();
              this.navigateDown();
              break;
            case 'ArrowUp':
              event.preventDefault();
              this.navigateUp();
              break;
            case 'Enter':
              event.preventDefault();
              if (this.highlightedIndex === -1 && this.searchQuery.length >= 3) {
                // Enter pressed with no selection or on "Search for" option
                this.searchFor();
              } else if (this.highlightedIndex >= 0 && this.highlightedIndex < this.filteredOptions.length) {
                // Enter pressed on a specific result
                this.selectOption(this.filteredOptions[this.highlightedIndex]);
              }
              break;
            case 'Escape':
              this.showDropdown = false;
              this.highlightedIndex = -1;
              this.$refs.input.blur();
              break;
          }
        },
        
        debouncedSearch() {
          if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
          }
          
          this.debounceTimer = setTimeout(() => {
            this.performSearch();
          }, 300);
        },
        
        async performSearch() {
          const query = this.searchQuery.trim();
          
          if (query.length < 3) {
            this.filteredOptions = [];
            this.showDropdown = false;
            return;
          }
          
          this.loading = true;
          
          try {
            const results = await this.resolveEntity(query);
            this.filteredOptions = Array.isArray(results) ? results : [];
            this.showDropdown = true;
            this.highlightedIndex = -1;
          } catch (error) {
            console.error('Error fetching autocomplete data:', error);
            this.filteredOptions = [];
          } finally {
            this.loading = false;
          }
        },
        
        selectOption(option) {
          if (option && option.node) {
            window.location.href = '/about?view=view&uri=' + encodeURIComponent(option.node);
          }
        },
        
        searchFor() {
          // Navigate to search page with query
          const query = encodeURIComponent(this.searchQuery);
          window.location.href = '/about?view=search&query=' + query;
        },
        
        navigateDown() {
          // Start at -1 for "Search for" option, then go through results
          if (this.highlightedIndex < this.filteredOptions.length - 1) {
            this.highlightedIndex++;
          }
        },
        
        navigateUp() {
          // Can go back to -1 for "Search for" option
          if (this.highlightedIndex > -1) {
            this.highlightedIndex--;
          }
        },
        
        handleClickOutside(event) {
          if (!this.$refs.wrapper.contains(event.target)) {
            this.showDropdown = false;
            this.highlightedIndex = -1;
          }
        }
    },
    
    mounted() {
      document.addEventListener('click', this.handleClickOutside);
    },
    
    beforeDestroy() {
      document.removeEventListener('click', this.handleClickOutside);
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer);
      }
    }
});
</script>

<style scoped>
.autocomplete-wrapper {
  position: relative;
}

.dropdown-item.active {
  background-color: var(--bs-primary);
  color: var(--bs-white);
}

.dropdown-item:hover {
  background-color: var(--bs-light);
  color: var(--bs-dark);
}

.dropdown-item.active:hover {
  background-color: var(--bs-primary);
  color: var(--bs-white);
}
</style>

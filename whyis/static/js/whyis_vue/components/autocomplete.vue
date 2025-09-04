<template>
  <div class="autocomplete-wrapper" ref="wrapper">
    <!-- Selected Item Display -->
    <div v-if="selectedItem" class="selected-item-container mb-2">
      <div class="d-flex align-items-center justify-content-between bg-light border rounded p-2">
        <div class="flex-grow-1">
          <!-- Custom rendering slot for selected item -->
          <slot name="selected" :item="selectedItem">
            <span>{{ getDisplayValue(selectedItem) }}</span>
          </slot>
        </div>
        <button
          type="button"
          class="btn btn-sm btn-outline-danger ms-2"
          @click="clearSelection"
          :disabled="disabled"
        >
          <i class="bi bi-x"></i>
          Remove
        </button>
      </div>
    </div>

    <!-- Input Field -->
    <div class="position-relative">
      <input
        ref="input"
        v-model="searchQuery"
        type="text"
        class="form-control"
        :class="inputClass"
        :placeholder="placeholder"
        :disabled="disabled"
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
      v-show="showDropdown && (filteredOptions.length > 0 || showNoResults)"
      class="dropdown-menu show position-absolute w-100 mt-1"
      style="max-height: 200px; overflow-y: auto; z-index: 1050;"
    >
      <!-- Options List -->
      <template v-if="filteredOptions.length > 0">
        <button
          v-for="(option, index) in filteredOptions"
          :key="getOptionKey(option, index)"
          type="button"
          class="dropdown-item d-flex align-items-center"
          :class="{ active: index === highlightedIndex }"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <!-- Custom rendering slot for options -->
          <slot name="option" :item="option" :index="index">
            <span>{{ getDisplayValue(option) }}</span>
          </slot>
        </button>
      </template>

      <!-- No Results Message -->
      <div v-else-if="showNoResults" class="dropdown-item-text text-muted">
        <slot name="no-results" :query="searchQuery">
          No results found for "{{ searchQuery }}"
        </slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AutocompleteSelect',
  
  props: {
    // Current selected value
    value: {
      type: [Object, String, Number],
      default: null
    },
    
    // Function to fetch data from server
    // Should return a Promise that resolves to an array
    fetchData: {
      type: Function,
      required: true
    },
    
    // Minimum characters before triggering search
    minChars: {
      type: Number,
      default: 1
    },
    
    // Debounce delay in milliseconds
    debounce: {
      type: Number,
      default: 300
    },
    
    // Field to display from option object
    displayField: {
      type: String,
      default: 'label'
    },
    
    // Field to use as unique identifier
    keyField: {
      type: String,
      default: 'id'
    },
    
    // Placeholder text
    placeholder: {
      type: String,
      default: 'Search...'
    },
    
    // Disabled state
    disabled: {
      type: Boolean,
      default: false
    },
    
    // Additional CSS classes for input
    inputClass: {
      type: [String, Array, Object],
      default: ''
    },
    
    // Show "no results" message
    showNoResults: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      searchQuery: '',
      filteredOptions: [],
      selectedItem: null,
      showDropdown: false,
      loading: false,
      highlightedIndex: -1,
      debounceTimer: null
    }
  },
  
  computed: {
    // For easier Vue 3 migration - computed properties work the same
  },
  
  watch: {
    value: {
      handler(newValue) {
        this.selectedItem = newValue
        if (newValue) {
          this.searchQuery = this.getDisplayValue(newValue)
          this.showDropdown = false
        } else {
          this.searchQuery = ''
        }
      },
      immediate: true
    }
  },
  
  mounted() {
    // Click outside to close dropdown
    document.addEventListener('click', this.handleClickOutside)
  },
  
  beforeDestroy() {
    // Cleanup - this will need to be beforeUnmount in Vue 3
    document.removeEventListener('click', this.handleClickOutside)
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
    }
  },
  
  methods: {
    onInput() {
      if (this.selectedItem) {
        this.clearSelection()
      }
      
      this.debouncedSearch()
    },
    
    onFocus() {
      if (this.searchQuery.length >= this.minChars && !this.selectedItem) {
        this.showDropdown = true
      }
    },
    
    onBlur() {
      // Delay hiding dropdown to allow for clicks
      setTimeout(() => {
        this.showDropdown = false
        this.highlightedIndex = -1
      }, 150)
    },
    
    onKeydown(event) {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault()
          this.navigateDown()
          break
        case 'ArrowUp':
          event.preventDefault()
          this.navigateUp()
          break
        case 'Enter':
          event.preventDefault()
          if (this.highlightedIndex >= 0) {
            this.selectOption(this.filteredOptions[this.highlightedIndex])
          }
          break
        case 'Escape':
          this.showDropdown = false
          this.highlightedIndex = -1
          this.$refs.input.blur()
          break
      }
    },
    
    debouncedSearch() {
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer)
      }
      
      this.debounceTimer = setTimeout(() => {
        this.performSearch()
      }, this.debounce)
    },
    
    async performSearch() {
      const query = this.searchQuery.trim()
      
      if (query.length < this.minChars) {
        this.filteredOptions = []
        this.showDropdown = false
        return
      }
      
      this.loading = true
      
      try {
        const results = await this.fetchData(query)
        this.filteredOptions = Array.isArray(results) ? results : []
        this.showDropdown = true
        this.highlightedIndex = -1
      } catch (error) {
        console.error('Error fetching autocomplete data:', error)
        this.filteredOptions = []
        this.$emit('error', error)
      } finally {
        this.loading = false
      }
    },
    
    selectOption(option) {
      this.selectedItem = option
      this.searchQuery = this.getDisplayValue(option)
      this.showDropdown = false
      this.highlightedIndex = -1
      this.filteredOptions = []
      
      // Emit events for parent component
      this.$emit('input', option) // v-model support
      this.$emit('select', option)
    },
    
    clearSelection() {
      this.selectedItem = null
      this.searchQuery = ''
      this.filteredOptions = []
      this.showDropdown = false
      
      // Emit events for parent component
      this.$emit('input', null) // v-model support
      this.$emit('clear')
      
      // Focus input for better UX
      this.$nextTick(() => {
        this.$refs.input.focus()
      })
    },
    
    navigateDown() {
      if (this.filteredOptions.length === 0) return
      
      this.highlightedIndex = Math.min(
        this.highlightedIndex + 1,
        this.filteredOptions.length - 1
      )
    },
    
    navigateUp() {
      if (this.filteredOptions.length === 0) return
      
      this.highlightedIndex = Math.max(this.highlightedIndex - 1, -1)
    },
    
    getDisplayValue(item) {
      if (!item) return ''
      
      if (typeof item === 'string' || typeof item === 'number') {
        return String(item)
      }
      
      // Try multiple possible label fields in order of preference
      return item[this.displayField] || 
             item.preflabel || 
             item.prefLabel || 
             item.label || 
             item.name || 
             item.title ||
             item.node ||
             item.uri ||
             item.id ||
             'Unknown'
    },
    
    getOptionKey(option, index) {
      if (typeof option === 'object' && option !== null) {
        return option[this.keyField] || index
      }
      return option || index
    },
    
    handleClickOutside(event) {
      if (!this.$refs.wrapper.contains(event.target)) {
        this.showDropdown = false
        this.highlightedIndex = -1
      }
    }
  }
}
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

.selected-item-container {
  transition: all 0.2s ease;
}

/* Vue 3 migration note: scoped styles work the same way */
</style>
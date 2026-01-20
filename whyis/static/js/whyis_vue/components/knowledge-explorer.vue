<template>
  <div class="knowledge-explorer">
    <div class="graph-container" ref="graphContainer"></div>
    
    <!-- Toolbar -->
    <div class="explorer-toolbar">
      <div class="toolbar-section">
        <input 
          v-model="searchText" 
          @input="onSearchTextChange"
          placeholder="Search entities..."
          class="search-input"
        />
        <button @click="handleAdd" class="btn-add">Add to Graph</button>
      </div>
      
      <div class="toolbar-section">
        <label>
          Probability Threshold:
          <input 
            v-model.number="probThreshold" 
            type="range" 
            min="0" 
            max="1" 
            step="0.01"
          />
          {{ probThreshold }}
        </label>
      </div>
      
      <div class="toolbar-section">
        <button @click="handleIncomingOutgoing" :disabled="!hasSelection">
          Load Incoming & Outgoing
        </button>
        <button @click="handleIncoming" :disabled="!hasSelection">
          Load Incoming
        </button>
        <button @click="handleOutgoing" :disabled="!hasSelection">
          Load Outgoing
        </button>
        <button @click="handleRemove" :disabled="!hasSelection">
          Remove Selected
        </button>
      </div>
      
      <div v-if="loading.length > 0" class="loading-indicator">
        Loading: {{ loading.join(', ') }}
      </div>
    </div>
    
    <!-- Details sidebar -->
    <div v-if="selectedElements.length > 0" class="details-sidebar">
      <h3>Selected Elements ({{ selectedElements.length }})</h3>
      <div v-for="element in selectedElements" :key="element.id" class="element-details">
        <h4>{{ element.label || element.uri || element.id }}</h4>
        <p v-if="element.summary" class="summary">{{ element.summary }}</p>
        <div v-if="element.types && element.types.length > 0">
          <strong>Types:</strong>
          <ul>
            <li v-for="type in element.types" :key="type.uri">
              {{ type.label || type.uri }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';
import { createLinksService, createGraphElements } from '@/utilities/kg-links';
import { resolveEntity } from '@/utilities/resolve-entity';
import { getSummary } from '@/utilities/rdf-utils';

// Register fcose layout
cytoscape.use(fcose);

export default {
  name: 'KnowledgeExplorer',
  
  props: {
    elements: {
      type: Object,
      default: () => createGraphElements()
    },
    style: {
      type: Array,
      default: null
    },
    layout: {
      type: Object,
      default: () => ({
        name: 'fcose',
        animate: true,
        nodeDimensionsIncludeLabels: true
      })
    },
    title: {
      type: String,
      default: 'Knowledge Explorer'
    },
    start: {
      type: String,
      default: null
    },
    startList: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      cy: null,
      searchText: '',
      selectedEntities: null,
      selectedElements: [],
      selectedNodes: [],
      selectedEdges: [],
      loading: [],
      probThreshold: 0.93,
      numSearch: 1,
      linksService: null
    };
  },
  
  computed: {
    hasSelection() {
      return this.selectedElements.length > 0;
    }
  },
  
  mounted() {
    this.initializeCytoscape();
    this.linksService = createLinksService();
    
    // Initialize with start entities if provided
    if (this.start) {
      this.incomingOutgoing([this.start]);
    } else if (this.startList && this.startList.length > 0) {
      this.incomingOutgoing(this.startList);
    }
  },
  
  beforeDestroy() {
    if (this.cy) {
      this.cy.destroy();
    }
  },
  
  methods: {
    initializeCytoscape() {
      const styleSheet = this.style || this.getDefaultStyle();
      
      this.cy = cytoscape({
        container: this.$refs.graphContainer,
        style: styleSheet,
        elements: [],
        hideLabelsOnViewport: true,
        boxSelectionEnabled: true
      });
      
      // Event handlers
      this.cy.on('select unselect', (e) => {
        this.updateSelection();
      });
      
      this.cy.on('tap', (e) => {
        if (e.target === this.cy) {
          // Clicked on background
          this.cy.elements().removeClass('faded highlighted');
        }
      });
    },
    
    getDefaultStyle() {
      return [
        {
          selector: 'node',
          style: {
            'text-valign': 'center',
            'width': 'label',
            'height': 'label',
            'padding': '0.5em',
            'border-width': 1,
            'cursor': 'pointer',
            'color': 'black',
            'font-size': '12px',
            'text-wrap': 'wrap',
            'text-max-width': '50em',
            'shape': 'data(shape)',
            'border-color': 'data(borderColor)',
            'background-color': 'data(backgroundColor)',
            'content': 'data(label)'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(width)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'target-arrow-color': 'data(color)',
            'line-color': 'data(color)',
            'label': 'data(label)',
            'font-size': '10px'
          }
        },
        {
          selector: ':selected',
          style: {
            'border-color': '#b2d7fd',
            'border-width': 2,
            'line-color': '#b2d7fd',
            'target-arrow-color': '#b2d7fd',
            'opacity': 1
          }
        },
        {
          selector: '.faded',
          style: {
            'opacity': 0.25,
            'text-opacity': 0
          }
        },
        {
          selector: '.highlighted',
          style: {
            'background-color': '#000000',
            'line-color': '#000000',
            'target-arrow-color': '#000000'
          }
        }
      ];
    },
    
    updateSelection() {
      this.selectedElements = this.cy.$(':selected').map(el => ({
        id: el.id(),
        ...el.data()
      }));
      this.selectedNodes = this.cy.$('node:selected').map(el => el.data());
      this.selectedEdges = this.cy.$('edge:selected').map(el => el.data());
      
      // Update details for selected elements
      this.selectedElements.forEach(element => {
        this.updateElementDetails(element);
      });
    },
    
    async updateElementDetails(data) {
      if (!data.label && data.uri) {
        try {
          const response = await this.$http.get('/about', {
            params: { uri: data.uri, view: 'label' }
          });
          data.label = response.data;
          this.render();
        } catch (error) {
          console.error('Error fetching label:', error);
        }
      }
      
      if (!data.described && data.uri) {
        data.described = true;
        try {
          const response = await this.$http.get('/about', {
            params: { uri: data.uri, view: 'describe' },
            responseType: 'json'
          });
          
          if (response.data && response.data.forEach) {
            response.data.forEach(x => {
              if (x['@id'] === data.uri) {
                Object.assign(data, x);
              }
            });
          }
          
          data.summary = getSummary(data);
          if (data.summary && data.summary['@value']) {
            data.summary = data.summary['@value'];
          }
          
          this.render();
        } catch (error) {
          console.error('Error fetching description:', error);
        }
      }
    },
    
    render() {
      if (!this.cy) return;
      if (!this.elements || !this.elements.all) return;
      
      // Update cytoscape with new elements
      this.cy.elements().remove();
      this.cy.add(this.elements.all());
      
      // Run layout
      this.cy.layout(this.layout).run();
    },
    
    async incomingOutgoing(entities) {
      if (!entities || entities.length === 0) {
        entities = this.cy.$('node:selected').map(d => d.id());
      }
      
      for (const entity of entities) {
        this.loading.push(entity);
        
        try {
          await this.linksService(entity, 'incoming', this.elements, this.render, this.probThreshold, this.numSearch);
          await this.linksService(entity, 'outgoing', this.elements, this.render, this.probThreshold, this.numSearch);
        } catch (error) {
          console.error('Error loading links:', error);
        } finally {
          this.loading = this.loading.filter(d => d !== entity);
        }
        
        this.render();
      }
    },
    
    async incoming(entities) {
      if (!entities || entities.length === 0) {
        entities = this.cy.$('node:selected').map(d => d.id());
      }
      
      for (const entity of entities) {
        this.loading.push(entity);
        
        try {
          await this.linksService(entity, 'incoming', this.elements, this.render, this.probThreshold, this.numSearch);
        } catch (error) {
          console.error('Error loading incoming links:', error);
        } finally {
          this.loading = this.loading.filter(d => d !== entity);
        }
        
        this.render();
      }
    },
    
    async outgoing(entities) {
      if (!entities || entities.length === 0) {
        entities = this.cy.$('node:selected').map(d => d.id());
      }
      
      for (const entity of entities) {
        this.loading.push(entity);
        
        try {
          await this.linksService(entity, 'outgoing', this.elements, this.render, this.probThreshold, this.numSearch);
        } catch (error) {
          console.error('Error loading outgoing links:', error);
        } finally {
          this.loading = this.loading.filter(d => d !== entity);
        }
        
        this.render();
      }
    },
    
    remove() {
      const selected = this.cy.$(':selected');
      this.cy.remove(selected);
      
      const selectedMap = {};
      selected.forEach(d => {
        selectedMap[d.id()] = d;
      });
      
      this.elements.nodes = this.elements.nodes.filter(d => !selectedMap[d.data.id]);
      this.elements.edges = this.elements.edges.filter(d => 
        !selectedMap[d.data.id] && 
        !selectedMap[d.data.source] && 
        !selectedMap[d.data.target]
      );
    },
    
    onSearchTextChange(text) {
      this.searchText = text;
    },
    
    async handleAdd() {
      if (this.selectedEntities) {
        await this.incomingOutgoing(this.selectedEntities.map(d => d.node));
      } else if (this.searchText && this.searchText.length > 3) {
        try {
          const entities = await resolveEntity(this.searchText);
          await this.incomingOutgoing(entities.map(d => d.node));
        } catch (error) {
          console.error('Error resolving entities:', error);
        }
      }
    },
    
    handleIncomingOutgoing() {
      this.incomingOutgoing();
    },
    
    handleIncoming() {
      this.incoming();
    },
    
    handleOutgoing() {
      this.outgoing();
    },
    
    handleRemove() {
      this.remove();
    }
  }
};
</script>

<style scoped>
.knowledge-explorer {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.graph-container {
  flex: 1;
  width: 100%;
  min-height: 500px;
  border: 1px solid #ccc;
}

.explorer-toolbar {
  padding: 10px;
  background: #f5f5f5;
  border-top: 1px solid #ccc;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.toolbar-section {
  display: flex;
  gap: 5px;
  align-items: center;
}

.search-input {
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 3px;
  min-width: 200px;
}

button {
  padding: 5px 10px;
  border: 1px solid #007bff;
  background: #007bff;
  color: white;
  border-radius: 3px;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-add {
  background: #28a745;
  border-color: #28a745;
}

.btn-add:hover {
  background: #218838;
}

.loading-indicator {
  padding: 5px 10px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 3px;
  font-size: 12px;
}

.details-sidebar {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 300px;
  background: white;
  border-left: 1px solid #ccc;
  overflow-y: auto;
  padding: 15px;
  box-shadow: -2px 0 5px rgba(0,0,0,0.1);
}

.element-details {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.element-details h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.summary {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.details-sidebar ul {
  margin: 5px 0;
  padding-left: 20px;
}

.details-sidebar li {
  font-size: 13px;
  margin: 3px 0;
}
</style>

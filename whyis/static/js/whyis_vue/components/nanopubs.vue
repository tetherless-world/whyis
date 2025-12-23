<template>
  <div class="nanopubs-container">
    <div v-if="loading" class="loading">Loading nanopublications...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-for="nanopub in nanopubs" :key="nanopub['@id']" class="nanopub-item">
        <div class="nanopub-content">
          <div v-if="nanopub.editing">
            <new-nanopub
              :nanopub="nanopub"
              verb="Update"
              :editing="true"
              @save="handleSaveNanopub"
            />
          </div>
          <div v-else>
            <div class="nanopub-body" v-html="trustHtml(nanopub.body || '')"></div>
            <div class="nanopub-actions" v-if="canEdit(nanopub)">
              <button @click="editNanopub(nanopub)" class="btn btn-sm btn-primary">Edit</button>
              <button @click="deleteNanopub(nanopub)" class="btn btn-sm btn-danger">Delete</button>
            </div>
          </div>
        </div>
      </div>

      <!-- New Nanopub Form -->
      <div v-if="!disableNanopubing" class="new-nanopub-section">
        <h4>Create New Nanopublication</h4>
        <new-nanopub
          :nanopub="newNanopub"
          verb="Create"
          @save="handleCreateNanopub"
        />
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="toDelete" class="modal-overlay" @click="cancelDelete">
        <div class="modal-dialog" @click.stop>
          <div class="modal-header">
            <h5>Confirm Delete</h5>
            <button @click="cancelDelete" class="close">&times;</button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this nanopublication?</p>
          </div>
          <div class="modal-footer">
            <button @click="cancelDelete" class="btn btn-secondary">Cancel</button>
            <button @click="confirmDelete" class="btn btn-danger">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { listNanopubs as listNanopubsAPI, describeNanopub, postNewNanopub, deleteNanopub as deleteNanopubAPI } from '../utilities/nanopub';
import { getLabel } from '../utilities/label-fetcher';
import NewNanopub from './new-nanopub.vue';

export default {
  name: 'Nanopubs',
  components: {
    NewNanopub
  },
  props: {
    resource: {
      type: String,
      required: true
    },
    disableNanopubing: {
      type: Boolean,
      default: false
    },
    currentUser: {
      type: Object,
      default: () => (typeof USER !== 'undefined' ? USER : {})
    }
  },
  data() {
    return {
      nanopubs: [],
      newNanopub: null,
      toDelete: null,
      loading: true,
      error: null
    };
  },
  created() {
    this.newNanopub = this.createNanopub();
    this.loadNanopubs();
  },
  methods: {
    createNanopub() {
      return {
        '@id': null,
        resource: {
          assertion: '',
          provenance: '',
          pubinfo: ''
        },
        about: this.resource
      };
    },
    async loadNanopubs() {
      try {
        this.loading = true;
        this.error = null;
        const result = await listNanopubsAPI(this.resource);
        this.nanopubs = Array.isArray(result) ? result : (result.data || []);
      } catch (err) {
        this.error = 'Failed to load nanopublications: ' + err.message;
      } finally {
        this.loading = false;
      }
    },
    canEdit(nanopub) {
      const user = this.currentUser;
      if (!user || !user.uri) return false;
      if (user.admin === 'True' || user.admin === true) return true;
      return nanopub.contributor === user.uri;
    },
    async editNanopub(nanopub) {
      try {
        const data = await describeNanopub(nanopub['@id'] || nanopub.uri);
        // Merge data into nanopub
        Object.assign(nanopub, { resource: data });
        this.$set(nanopub, 'editing', true);
      } catch (err) {
        this.error = 'Failed to load nanopub for editing: ' + err.message;
      }
    },
    async handleSaveNanopub(nanopub) {
      try {
        // Update is done via POST with existing nanopub data
        await postNewNanopub(nanopub.resource, nanopub['@context']);
        await this.loadNanopubs();
      } catch (err) {
        this.error = 'Failed to update nanopublication: ' + err.message;
      }
    },
    async handleCreateNanopub(nanopub) {
      try {
        await postNewNanopub(nanopub.resource, nanopub['@context']);
        this.newNanopub = this.createNanopub();
        await this.loadNanopubs();
      } catch (err) {
        this.error = 'Failed to create nanopublication: ' + err.message;
      }
    },
    deleteNanopub(nanopub) {
      this.toDelete = nanopub;
    },
    cancelDelete() {
      this.toDelete = null;
    },
    async confirmDelete() {
      try {
        const uri = this.toDelete['@id'] || this.toDelete.uri;
        await deleteNanopubAPI(uri);
        this.toDelete = null;
        await this.loadNanopubs();
      } catch (err) {
        this.error = 'Failed to delete nanopublication: ' + err.message;
        this.toDelete = null;
      }
    },
    trustHtml(html) {
      // In Vue, we use v-html which doesn't require explicit trust
      // This method exists for API compatibility with Angular version
      return html;
    },
    getLabel
  }
};
</script>

<style scoped>
.nanopubs-container {
  padding: 1rem;
}

.loading, .error {
  padding: 1rem;
  text-align: center;
}

.error {
  color: #d9534f;
  background-color: #f2dede;
  border: 1px solid #ebccd1;
  border-radius: 4px;
}

.nanopub-item {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
}

.nanopub-content {
  position: relative;
}

.nanopub-actions {
  margin-top: 0.5rem;
}

.nanopub-actions button {
  margin-right: 0.5rem;
}

.new-nanopub-section {
  margin-top: 2rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-dialog {
  background-color: white;
  border-radius: 4px;
  max-width: 500px;
  width: 90%;
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.btn-primary {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}

.btn-danger {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
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
</style>

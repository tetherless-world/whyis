<template>
<div>
    <div v-if="!hideButton" v-on:click="showDialogBox" >
        <slot>
            <!--Default button -->
            <button class="btn btn-outline-primary btn-sm"
                style="border:none; background:transparent">
                <i class="bi bi-plus"></i> Add type(s)
            <span class="visually-hidden">Specify additional type, subclass, or superclass.</span>
            </button>
        </slot>
    </div>
    
    <div>
    <!-- Bootstrap Modal -->
    <div class="modal fade" id="addTypeModal" tabindex="-1" :class="{'show': active}" :style="{display: active ? 'block' : 'none'}" v-if="active">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header utility-dialog-box_header">
            <h5 class="modal-title">Specify additional types/classes</h5>
            <button type="button" class="btn-close" @click="onCancel" aria-label="Close"></button>
          </div>
          <div class="modal-body" style="margin:20px;">
            <!-- Custom autocomplete using Bootstrap form controls -->
            <div class="mb-3">
              <div class="form-floating">
                <input type="text" class="form-control" id="typeSearch" v-model="selectedType" 
                       @input="resolveEntityType($event.target.value)" 
                       @focus="showSuggestedTypes"
                       @blur="processAutocompleteMenu(true)"
                       placeholder="Search for types">
                <label for="typeSearch">Search for types</label>
              </div>
              <!-- Dropdown results -->
              <div v-if="typeList.length > 0" class="dropdown-menu show" style="position: relative; width: 100%; max-height: 200px; overflow-y: auto;">
                <button v-for="item in typeList" :key="item.node" 
                        class="dropdown-item" 
                        @click="selectedTypeChange(item)">
                  <span v-if="item.preflabel">{{ item.preflabel }}</span>
                  <span v-else>{{ item.label }}</span>
                  <small class="text-muted d-block">{{ item.node }}{{ item.property }}</small>
                </button>
              </div>
              <div v-if="typeList.length === 0 && selectedType" class="alert alert-info mt-2">
                <p v-if="selectedType">No types or classes matching "{{ selectedType }}" were found.</p>
                <p v-else>Enter a type name.</p>
                <button type="button" class="btn btn-link p-0" @click="useCustomURI">Use a custom type URI</button>         
              </div>
            </div>
            
            <div v-if="useCustom" class="mb-3">
              <div class="row g-3">
                <div class="col">
                  <div class="form-floating">
                    <input type="text" class="form-control" id="customTypeURI" v-model="customTypeURI" placeholder="Full URI of type">
                    <label for="customTypeURI">Full URI of type</label>
                  </div>
                </div>
                <div class="col-auto">
                  <button type="button" class="btn btn-primary h-100" @click="submitCustomURI">
                    Confirm URI
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Selected types as badges -->
            <div class="mb-3">
              <div v-for="(chip, key) in typeChips" :key="key + 'chips'" class="d-inline-block me-2 mb-2">
                <span class="badge bg-secondary d-flex align-items-center">
                  <span v-if="typeChips[key].preflabel">{{ typeChips[key].preflabel }}</span>
                  <span v-else>{{ typeChips[key].label }}</span>
                  <button type="button" class="btn-close btn-close-white ms-2" @click="removeChip(key)" aria-label="Remove"></button>
                </span>
              </div>
            </div>
        
            <div class="d-flex justify-content-end gap-2">
              <button type="button" class="btn btn-secondary" @click.prevent="onCancel">
                Cancel
              </button>
              <button type="button" class="btn btn-primary" @click.prevent="onSubmit">
                Submit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
</div>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";
import axios from 'axios'
import { postNewNanopub } from '../utilities/nanopub'

export default Vue.component('add-type', {
    props: ['uri', 'hideButton'],
    data: function() {
        return {
            id: null,
            useCustom: false,
            customTypeURI: null,
            typeList: [],
            selectedType: null,
            typeChips: [],
            status: false,
            active: false,
            query: null,
            awaitingResolve: false,
        };
    },
    methods: {
        showSuggestedTypes(){
            this.processAutocompleteMenu();
            this.typeList = this.getSuggestedTypes(this.uri);
        },
        useCustomURI(){
            this.useCustom = true;
        },
        submitCustomURI(){
            var newChip = {
                label: this.customTypeURI,
                node: this.customTypeURI, 
            }
            this.typeChips.push(newChip);
            this.customTypeURI = "";
            this.useCustom = false
        },
        resolveEntityType(query){
            var thisVue = this;
            this.query = query
            if (!thisVue.awaitingResolve) {
                setTimeout(function () {
                    console.log(thisVue.query)
                    thisVue.typeList = thisVue.getTypeList(thisVue.query);
                    thisVue.awaitingResolve = false;
                }, 1000); 
            }
            thisVue.awaitingResolve = true;
        },
        selectedTypeChange(item){
            this.typeChips.push(item);
        },
        // Create dialog boxes
        showDialogBox () {
            this.active=true;
        },
        removeChip(index){
            this.typeChips.splice(index, 1);
        },
        resetDialogBox(){
            this.active = !this.active;
            this.typeChips = [];
            this.customTypeURI = "";
            this.useCustom = false;
        },
        onCancel() {
            return this.resetDialogBox();
        },
        onSubmit() {
            this.saveNewTypes()
            .then(() => window.location.reload());
            return this.resetDialogBox();
        },
        async saveNewTypes () {
            let p = Promise.resolve()
            const types = this.processTypeChips();
            const jsonLd = {
                '@id': this.uri,
                '@type': types, 
            }
            await p
            try{
                return postNewNanopub(jsonLd)
            } catch(err){
                return alert(err)
            }
        },
        processTypeChips () {
            var processedChips = this.typeChips
            Object.keys(processedChips).map(function(key, index) {
                if (processedChips[key]["node"]){
                    processedChips[key] = processedChips[key]["node"];
                }
            });
            return processedChips
        },
        // Formats the dropdown menu. Runs only while the menu is open
        processAutocompleteMenu (param) {
            const itemListContainer = document.getElementsByClassName("dropdown-menu")
            if(itemListContainer.length >= 1) {
                //itemListContainer[0].style['z-index'] = 12;
                return status = true
            }
        },

        async getSuggestedTypes (uri){
            const suggestedTypes = await axios.get(
                `${ROOT_URL}about?view=suggested_types&uri=${uri}`)
            return suggestedTypes.data
        },

        async getTypeList (query) {
            var combinedList = [];
            const [rdfsClass, owlClass] = await axios.all([
                axios.get(
                `${ROOT_URL}about?term=${query}*&view=resolve&type=http://www.w3.org/2000/01/rdf-schema%23Class`),
                axios.get(
                `${ROOT_URL}about?term=${query}*&view=resolve&type=http://www.w3.org/2002/07/owl%23Class`)
            ]).catch((err) => {
                throw(err)
            })
            combinedList = owlClass.data.concat(rdfsClass.data)
            .sort((a, b) => (a.score < b.score) ? 1 : -1);
            let grouped = this.groupBy(combinedList, "node")
            return grouped
        },

        // Group entries by the value of a particular key
        groupBy (original, key) {
            let groupedDictionary = original.reduce(function(grouped, index) {
                grouped[index[key]] = grouped[index[key]] || index;
                return grouped;
            }, {});
            var values = Object.keys(groupedDictionary).map(function(key) {
                return groupedDictionary[key]
            })
            return values
        },
    },
    created: function () {
        // If the component was called with hideButton enabled,
        // render the dialog box without needing a click from the button component
        if(this.hideButton){
            this.active=true;
        }
    }
});

</script>

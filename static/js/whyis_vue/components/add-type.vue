<template>
<div>
    <slot>
        <md-button id="addtypebutton" @click="showNewInstitution()" class="md-button-icon">+ Add type(s)</md-button>
    </slot>
    
    <div>
    <md-dialog :md-active.sync="active" style="margin-top: -4rem" :md-click-outside-to-close="true">
        <div style="margin:10px">
            <div class="utility-dialog-box_header" >
            <md-dialog-title> Add new types/classes</md-dialog-title>
            </div>
            <md-autocomplete
                :value="selectedType" 
                :md-options="typeList" 
                :md-open-on-focus="true" 
                @md-changed="resolveEntityType"
                v-on:md-selected="selectedTypeChange"
                @md-opened="showSuggestedTypes"
            >
                <!-- @md-opened="setListStyle" -->
                <!-- @md-closed="setListStyle(true)" -->
            <!-- >  -->
                <label>Search for types</label>

                <template style="width: 90% !important; left: 1px !important;" slot="md-autocomplete-item" slot-scope="{ item }">
                <label style="white-space: pre-wrap" md-term="term" md-fuzzy-search="true">{{item.label}}</label>
                </template>
            
                <template style="width: 90% !important; left: 1px !important" slot="md-autocomplete-empty" slot-scope="{ term }">
                <p>No types or classes matching "{{ term }}" were found.</p>
                </template>
            </md-autocomplete>
            <div
                v-for="(chip, key) in typeChips" 
                v-bind:key="key + 'chips'">
                <md-chip md-deletable v-model=typeChips[key]>{{typeChips[key].label}}</md-chip>
            </div>
        
            <div class="utility-margin-big viz-2-col">
                <div class="utility-align--right utility-margin-top"> 
                </div>
                <div class="utility-align--right utility-margin-top">
                <a @click.prevent="onCancel" class="btn-text btn-text--default"> &larr; Exit</a> &nbsp; &nbsp;
                <a @click.prevent="onSubmitNew" class="btn-text btn-text--default">Submit &rarr; </a>
                </div>
            </div>
        </div>
    </md-dialog>
    </div>
</div>
</template>

<script>
import Vue from "vue";
import {getTypeList, getSuggestedTypes} from "../utilities/autocomplete-menu";
import { EventServices } from '../modules';
import { processFloatList, resetProcessFloatList } from '../utilities/dialog-box-adjust';

export default Vue.component('add-type', {
    props: ['attributes'],
    data: function() {
        return {
            id: null,
            typeList: [],
            selectedType: null,
            typeChips: [],
            status: false,
            active: false,
        };
    },
    methods: {
        async showSuggestedTypes(){
            this.typeList = await getSuggestedTypes(this.attributes);
        },
        async resolveEntityType(query){
            this.typeList = await getTypeList(query);
        },
        selectedTypeChange(item){
            this.typeChips.push(item);
        },
        // Create dialog boxes
        showNewInstitution () {
            this.active=true;
            return processFloatList()
            // EventServices
            // .$emit('open-new-instance', {status: true, title:"Add types or classes"})
            // return
        },
        onCancel() {
            this.active = !this.active;
            return resetProcessFloatList();
        },
    },
    created() {
    //   EventServices
    //   .$on('open-add-type', (data) => {
    //     this.status = data.status
    //     this.id = data.id;
    //   })
    }
});
</script>

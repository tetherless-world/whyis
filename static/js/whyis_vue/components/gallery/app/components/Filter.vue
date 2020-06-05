<template>
  <div>
    <md-dialog :md-active.sync="active" style="margin-top: -4rem">
      <div class="utility-dialog-box_header">
        <md-dialog-title >{{ loginRequestSent? "Login" : "Filter Chart" }}</md-dialog-title>
      </div>
      <div class="utility-dialog-box_login" v-if="loginRequestSent">
        <md-field :class="messageClass">
          <label>Email:</label>
          <md-input v-model="required" required></md-input>
          <span class="md-error">There is an error</span>
        </md-field>

        <md-field>
          <label>Password:</label>
          <md-input v-model="password" type="password" required></md-input>
          <span class="md-error">There is an error</span>
        </md-field>
        <div class="viz-2-col">
          <button class="btn btn_small btn--default" @click="onConfirm">Sign In</button>
          <div class="utility-align--right utility-margin-top">
            <a href="#" class="btn-text btn-text--default"> Forgot Password? </a>
          </div>
        </div>
        <div class="utility-margin-big viz-3-col">
          <a href="#" class="btn-text btn-text--default">Sign Up &rarr; </a>
          <a href="#" class="btn-text btn-text--default">Duke Login &rarr; </a>
          <a href="#" class="btn-text btn-text--default">Gmail Login &rarr; </a>
        </div>
      </div>

      <div class="utility-dialog-box_login" v-else>
        <div class="md-layout-item">
          <md-field>
            <label for="movie">Filter By</label>
            <md-select v-model="filterby" name="filterby" id="filterby" placeholder="Filter By">
              <md-option value="title">Title</md-option>
              <md-option value="description">Description</md-option>
            </md-select>
          </md-field>
        </div>
        <md-autocomplete v-model="selectedText" :md-options="filterby == 'title' ? chartResults.title:chartResults.description" :md-open-on-focus="false">
          <label>Filter Keyword</label>

          <template slot="md-autocomplete-item" slot-scope="{ item, term }">
            <md-highlight-text :md-term="term">{{ item }}</md-highlight-text>
          </template>

          <template slot="md-autocomplete-empty" slot-scope="{ term }">
            No {{ filterby }} matching "{{ term }}" were found. <a @click="createNew">Create a new</a> chart! &nbsp; &nbsp;
          </template>
        </md-autocomplete>
        <div class="utility-margin-big viz-2-col">
          <div class="utility-align--right utility-margin-top">
            
          </div>
          <div class="utility-align--right utility-margin-top">
            <a @click.prevent="onCancel" class="btn-text btn-text--default"> &larr; Exit</a> &nbsp; &nbsp;
            <a @click.prevent="onConfirm" class="btn-text btn-text--default">Submit &rarr; </a>
          </div>
        </div>
      </div>
    </md-dialog>
  </div>
</template>
<style scoped lang="scss" src="../static/css/main.scss"></style>
<script>
  import { eventCourier as ec } from '../store';
  import { processFloatList, resetProcessFloatList } from '../js/index'
  import { goToView } from '../../../../utilities/views'
  export default {
    name: 'FilterBox',
    data () {
      return {
        active: false,
        required: null,
        hasMessages: false,
        loginRequestSent: false,
        filterby: "employees",
        selectedText: null,
        password: null,
        chartResults: ec.appState,
      }
    },
    computed: {
      messageClass () {
        return {
          'md-invalid': this.hasMessages
        }
      }
    },
    watch: {
      active(newValue, OldValue) {
        if(newValue == false){
          resetProcessFloatList();
        }
      }
    },
    methods: {
      onConfirm() {
        this.active = !this.active
        this.loginRequestSent = false
        ec.$emit('close-filter-box', this.active)
        return ec.authenticate({username: this.required, password:this.password})
      },
      onCancel() {
        this.active = !this.active
        ec.$emit('close-filter-box', this.active)
        return resetProcessFloatList();
      },
      createNew(){
        return goToView(this.globalargs, "new", "open")
      },
    },
    created() {
      ec.$on('open-filter-box', (data) => {
        if(data.type == "filter") {
          this.active = data.open
          return processFloatList()
        } else {
          this.active = data.open
          this.loginRequestSent = true
        }
      });
    }
  }
</script>
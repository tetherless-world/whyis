<template>
  <div style="margin: 20px">
    <div class="md-layout">
      <div class="md-headline">General Information</div>
      <md-field>
        <label>Title</label>
        <md-input v-model="title"></md-input>
      </md-field>

      <div class="md-layout md-gutter">
        <div class="md-layout-item md-size-15">
          <label>Contact Point</label>
        </div>

        <div class="md-layout-item md-size-30">
          <md-field>
            <label>First name</label>
            <md-input v-model="cpfirstname"></md-input>
          </md-field>
        </div>

        <div class="md-layout-item md-size-30">
          <md-field>
            <label>Last name</label>
            <md-input v-model="cplastname"></md-input>
          </md-field>
        </div>

        <div class="md-layout-item md-size-25">
          <md-field>
            <label>Email</label>
            <md-input v-model="cpemail"></md-input>
          </md-field>
        </div>
      </div>

      <md-field>
        <label>Text Description</label>
        <md-textarea v-model="textdescription"></md-textarea>
      </md-field>

      <md-divider style="border-style: solid" width="100%"></md-divider>

      <div class="md-headline" style="margin-top: 10px; margin-bottom: 10px">
        Contributors
      </div>

      <table class="table" width="100%">
        <thead>
          <tr>
            <td><strong>Organization/Institutions</strong></td>
            <td><strong>Author(s)</strong></td>
            <td></td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in contributors" v-bind:key="index">
            <td><input type="text" v-model="row['org']" /></td>
            <td><input type="text" v-model="row['authors']" /></td>
            <td>
              <a v-on:click="removeElement(index)" style="cursor: pointer"
                >Remove</a
              >
            </td>
          </tr>
        </tbody>
      </table>
      <div>
        <button
          class="button btn-primary"
          @click="addOrg"
          style="margin-bottom: 10px"
        >
          Add row
        </button>
      </div>

      <md-divider style="border-style: solid" width="100%"></md-divider>

      <div class="md-headline" style="margin-top: 10px; margin-bottom: 10px">
        Publication Information
      </div>

      <div style="width: 100%">
        <div class="md-layout md-gutter">
          <div class="md-layout-item md-size-50">
            <label>Date Published</label>
            <md-field>
              <md-input v-model="datepub" type="date"></md-input>
            </md-field>
          </div>

          <div class="md-layout-item md-size-50">
            <label>Date Last Modified</label>
            <md-field>
              <md-input v-model="datemod" type="date"></md-input>
            </md-field>
          </div>
        </div>

        <div>
          <md-field>
            <label>DOI(s) of Related Publication(s)</label>
            <md-input v-model="dois"></md-input>
            <span class="md-helper-text">Separate multiple DOIs with ','</span>
          </md-field>
        </div>

        <md-card-actions>
          <md-button v-on:click="submitForm" class="md-primary"
            >Submit</md-button
          >
        </md-card-actions>
      </div>
    </div>
  </div>
</template>


<script src="https://unpkg.com/vue@2.1.10/dist/vue.js"></script>
<script>
export default {
  name: "TextFields",
  data: () => ({
    title: "",
    cpfirstname: "",
    cplastname: "",
    cpemail: "",
    textdescription: "",
    contributors: [],
    datepub: null,
    datemod: "",
    dois: [],
  }),
  methods: {
    addOrg: function () {
      var elem = document.createElement("tr");
      this.contributors.push({
        org: "",
        authors: "",
      });
    },
    removeElement: function (index) {
      this.contributors.splice(index, 1);
    },
    submitForm: function () {
      console.log(JSON.stringify(this._data));
    },
  },
};
</script>

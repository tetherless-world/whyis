<template>
    <div id="app" class="test">
        <div id="data-table"></div>
        <TableControl 
            @apiPost="testApiPost"
            @apiGet="testApiGet"
        >
        </TableControl>
    </div>
</template>

<script>
import Vue from 'vue';
import Tabulator from 'tabulator-tables';
import MockApi from '../api/api.js';
import TableControl from './tablecontrol.vue';

export default Vue.component('Tableview', {
    name: 'Tableview',
    methods: {
        testApiPost() {
            console.log(this.tabulator.data);
            let compiledData = new File([this.tabulator.data], "file.txt");
            console.log(this.api.postFile(compiledData));
        },
        async testApiGet(){
            var response = await this.api.getFile();
            console.log(response);
            this.tabulator.setData(response);
        }
    },
    mounted(){
    //instantiate Tabulator when element is mounted
    this.tabulator = new Tabulator('#data-table', {
        reactiveData:true, //enable data reactivity
        columns:[ //Define Table Columns
            {title:"Name", field:"name", width:150, editor:true},
            {title:"Age", field:"age", align:"left", editor:true},
            {title:"Favourite Color", field:"col", editor:true},
            {title:"Date Of Birth", field:"dob", sorter:"date", align:"center", editor:true},
        ],
    });
    // Create API instance
    this.api = new MockApi();
  },
})
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
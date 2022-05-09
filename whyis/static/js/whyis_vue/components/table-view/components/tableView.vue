<template>
    <div id="app" class="test">
        <h1>Tabular File I/O</h1>
        <div id="data-table"></div>
        <tableControl 
            @apiPost="testApiPost"
            @apiGet="testApiGet"
            @createCol="addColumn"
            @createRow="addRow"
        >
        </tableControl>
        <!--<columnAddition v-bind:style="[showInput ? 'inline' : 'none']"></columnAddition>-->
    </div>
</template>

<script>
import Vue from 'vue';
import Tabulator from 'tabulator-tables';
import MockApi from '../api/mockapi.js';
import tableControl from './tableControl.vue';
import columnAddition from './columnAddition.vue';

export default Vue.component('tableview', {
    name: 'tableview',
    data() {
        return {
            showInput: false,
        }
    },
    methods: {
        testApiPost() {
            console.log(this.tabulator.getData());
            console.log(this.api.postFile(this.tabulator.getData()));
        },
        async testApiGet(){
            var response = await this.api.getFile();
            const columns = {};
            response.map((value) => {
                Object.entries(value).map((header) => {
                    columns[header[0]] = typeof(header[1]);
                })
            })
            let formattedCol = [];
            for (var el in columns) {
                let temp = {}
                temp['title'] = el;
                temp['field'] = el;
                temp['sorter'] = columns[el];
                temp['align'] = 'center';
                temp['editor'] = true;
                formattedCol.push(temp);
            }
            this.tabulator.setColumns(formattedCol);
            this.tabulator.setData(response);
        },
        addColumn(){
            this.showInput = true;
        },
        addRow(){
            //TODO
        }
    },
    mounted(){
        //instantiate Tabulator when element is mounted
        this.tabulator = new Tabulator('#data-table', {
            reactiveData:true, //enable data reactivity
        });
        // Create API instance
        this.api = new MockApi();
  },
})
</script>

<style lang="css">
#app {
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
        margin-top: 60px;
    }
</style>

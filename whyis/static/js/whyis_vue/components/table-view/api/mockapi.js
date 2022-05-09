import Api from './api.js';

export default class MockApi extends Api {
    postFile(file) {
        let x = new Promise((resolve, reject) => {
          file ?
          setTimeout(function() {
            resolve(file);
          }, 300)
          : reject();
        });   
        x.then((value) => {
            //Set data in backend 
            console.log("File contents:", value);
        });
        return x;
    }
    getFile() {
        return new Promise(function(resolve, reject) {
            setTimeout(() => {
                resolve([
                    {id:1, name:"Billy Bob", age:"12", col:"red", dob:""},
                    {id:2, name:"Mary May", age:"1",col:"blue", dob:"14/05/1982"},
                    {id:3, name:"Christine Lobowski", age:"42", height:0, col:"green", dob:"22/05/1982", cheese:"true"},
                    {id:4, name:"Brendon Philips", age:"125", gender:"male", height:1, col:"orange", dob:"01/08/1980"},
                    {id:5, name:"Margret Marmajuke", age:"16", gender:"female", height:5, col:"yellow", dob:"31/01/1999"},
                    {id:6, name:"Billy Bob", age:"12", gender:"male", height:1, col:"red", dob:"", cheese:1},
                    {id:7, name:"Mary May", age:"1", gender:"female", height:2, col:"blue", dob:"14/05/1982", cheese:true},
                    {id:8, name:"Christine Lobowski", age:"42", height:0, col:"green", dob:"22/05/1982", cheese:"true"},
                    {id:9, name:"Brendon Philips", age:"125", gender:"male", height:1, col:"orange", dob:"01/08/1980"},
                    {id:10, name:"Margret Marmajuke", age:"16", gender:"female", height:5, col:"yellow", dob:"31/01/1999"},
                ]);
            }, 300);
        });
    }
}

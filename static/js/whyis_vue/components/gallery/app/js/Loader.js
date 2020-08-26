import { eventCourier as ec } from './../store'
let reqState = false;
let parsedArg = null;

const loadDataArr = async(args) => {
    reqState = true;
    parsedArg = args;
    let data, processedData;
    if(!args) return false;
    data = await fetch(args, {
        method: "POST"
    });
    processedData = await data.json();
    ec.addItem(processedData)
    return reqState = false
}

/** Re-run every 1min */
setInterval(() => {
    if(reqState == false && parsedArg != null){
        return loadDataArr(parsedArg)
    }
}, 9000)

export default loadDataArr;
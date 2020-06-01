import { eventCourier as ec } from './../store'

const loadDataArr = async(args) => {
    let data, processedData;
    if(!args) return false;
    data = await fetch(args, {
        method: "POST"
    });
    processedData = await data.json();
    return ec.addItem(processedData)
}

export default loadDataArr;
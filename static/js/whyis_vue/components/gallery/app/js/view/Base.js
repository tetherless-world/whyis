let elements;
const base = document.getElementsByClassName("vega-actions");
if(base.length > 0){
    elements = {
        saveAsPNG: base[0].children[1],
        saveAsSVG: base[0].children[0]
    }
}

export default elements;
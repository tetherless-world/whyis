let run;

const processFloatList = () => {
    run = setInterval(() => {
        const floatList = document.getElementsByClassName("md-menu-content-bottom-start")
        if(floatList.length >= 1) {
            floatList[0].setAttribute("style", "z-index:1000 !important; width: 410px; max-width: 410px; position: absolute; top: 579px; left:50%; transform:translateX(-50%); will-change: top, left;")
            return status = true
        }
    }, 40)

    return run
}

const resetProcessFloatList = () => {
    if(run){
        return clearInterval(run);
    }
}

export {
    processFloatList,
    resetProcessFloatList
} 
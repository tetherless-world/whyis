/**
 * Utilities for adjusting dialog box positioning and styling.
 * These functions manage the visual appearance of Material Design dialog boxes.
 * 
 * @module dialog-box-adjust
 */

let run;

/**
 * Continuously processes and adjusts floating dialog boxes to ensure proper positioning.
 * Monitors for Material Design menu content elements and applies custom styling to center them.
 * 
 * @returns {number} The interval ID that can be used to stop the process
 * @example
 * const intervalId = processFloatList();
 * // Dialog boxes will now be automatically centered
 */
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

/**
 * Stops the dialog box positioning process by clearing the active interval.
 * Call this function when dialog positioning is no longer needed.
 * 
 * @returns {undefined} Clears the interval if one is running
 * @example
 * resetProcessFloatList(); // Stops automatic dialog positioning
 */
const resetProcessFloatList = () => {
    if(run){
        return clearInterval(run);
    }
}

export {
    processFloatList,
    resetProcessFloatList
} 
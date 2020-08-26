import elements from "./view/Base";
class ImageExtractor {
    constructor() {
        this.newEvent = new CustomEvent('click')
        this.image = null;
        this.initialize();
        this.events();
    }

    extract(e) {
        e.preventDefault();
        return this.image = e.target.href
    }

    events() {
        if(elements.saveAsPNG) {
            return elements.saveAsPNG.dispatchEvent(this.newEvent)
        } else if(elements.saveAsSVG) {
            return elements.saveAsSVG.dispatchEvent(this.newEvent)
        } else {
            return false;
        }
    }

    initialize() {
        if(elements.saveAsPNG) return elements.saveAsPNG.addEventListener('click', (e) => this.extract(e))
        if(elements.saveAsSVG) return elements.saveAsSVG.addEventListener('click', (e) => this.extract(e))
        return false;
    }
}

export default ImageExtractor;
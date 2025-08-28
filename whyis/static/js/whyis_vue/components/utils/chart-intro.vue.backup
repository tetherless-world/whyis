<template>
    <div>
        <div v-if="screen == 1">
            <div style="width: 100% !important; text-align:center; margin-top:4.7rem">
                <img src="/js/whyis_vue/components/gallery/app/static/image/Slide1.gif" class="viz-intro-image" alt="slide-1">
            </div>
            <div style="margin-bottom: 1.5rem !important;">
                <div><span class="md-display-1 btn--animated viz-intro-title-text">Welcome!</span></div>
                <div class="utility-margin-top viz-intro-text btn--animated">
                    <div style="margin-bottom: .5rem !important;">
                        Inside the Gallery, you will find charts built from data in the NanoMine knowledge graph.
                    </div> 
                    These custom charts showcase the variety of data within NanoMine and aim to generate new insights and questions. 
                </div>
            </div>
        </div>
        <div v-else-if="screen == 2">
            <div style="width: 100% !important; text-align:center; margin-top:4.7rem">
                <img src="/js/whyis_vue/components/gallery/app/image/Slide2.gif" class="viz-intro-image" alt="slide-2">
            </div>
            <div style="margin-bottom: 1.5rem !important;">
                <div><span class="md-display-1 btn--animated viz-intro-title-text">Interact.</span></div>
                <div class="utility-margin-top viz-intro-text btn--animated">
                    <div style="margin-bottom: 1rem !important;">
                        Charts are created using Vega-Lite, which brings data visualizations to life through various interactive elements.
                    </div> 
                    Examples you may find in the Gallery include brush selection, cross-filtering, pan/zoom, hover interactions, and much more...
                </div>
            </div>
        </div>
        <div v-else-if="screen == 3">
            <div style="width: 100% !important; text-align:center; margin-top:4.7rem">
                <img src="/js/whyis_vue/components/gallery/app/image/Slide3.gif" class="viz-intro-image" alt="slide-3">
            </div>
            <div style="margin-bottom: 1.5rem !important;">
                <div><span class="md-display-1 btn--animated viz-intro-title-text">Explore.</span></div>
                <div class="utility-margin-top viz-intro-text btn--animated">
                    <div style="margin-bottom: 1rem !important;">
                        Each chart offers a unique lens into the NanoMine database.
                    </div>
                    To dig deeper into the data, check out the <a @click.prevent="cancelDel" class="btn-text btn-text--simple">faceted browser</a>. If you are familiar with RDF, you can query the knowledge graph directly at our
                    <a @click.prevent="cancelDel" class="btn-text btn-text--simple">SPARQL endpoint</a>.
                </div>
            </div>
        </div>
        <div v-else>
            <div style="width: 100% !important; text-align:center; margin-top:4.7rem">
                <img src="/js/whyis_vue/components/gallery/app/image/Slide4.gif" class="viz-intro-image" alt="slide-4">
            </div>
            <div style="margin-bottom: 1.5rem !important;">
                <div><span class="md-display-1 btn--animated viz-intro-title-text">Create.</span></div>
                <div class="utility-margin-top viz-intro-text btn--animated">
                    <div style="margin-bottom: 1rem !important;">
                        Users who want to learn more about SPARQL and Vega-Lite are encouraged to contribute to the Gallery.
                    </div>
                    Logged-in users can compose custom queries and chart specifications via an editor interface and save their custom charts to NanoMine.
                </div>
            </div>
        </div>
    </div>
</template>
<style lang="scss" src="../../assets/css/main.scss"></style>
<script>
    import Vue from 'vue'

    export default Vue.component('tip-intro', {
        props: ['screen']
    })
</script>

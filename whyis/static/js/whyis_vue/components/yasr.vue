<template>
    <div v-bind:id="id"></div>
</template>

<script>
export default {
  name: 'yasr',
    props: {
        id: {
            type: String,
            default: () => "YASR"
        },
        results: {
            type: Object,
            default: () => null
        }
    },
    methods: {
        setResults (results) {
            if (results) {
                this.yasr.setResponse(results)
            }
        }
    },
    mounted () {
        this.yasr = window.YASR(this.$el, {
            outputPlugins: ['table'],
            useGoogleCharts: false,
            persistency: {
                results: {
                    key: () => false
                }
            }
        });
        this.setResults(this.results);
    },
    watch: {
        results (newVal, oldVal) {
            this.setResults(newVal)
        }
    }
}
</script>

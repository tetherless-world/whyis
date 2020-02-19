<template>
    <div class="yasqe"></div>
</template>

<script>
import Vue from "vue"

export default Vue.component('yasqe', {
    props: {
        query: {
            type: String,
            default: () => ""
        },
        endpoint: {
            type: String,
            default: () => "/sparql"
        }
    },
    mounted () {
        const yasqeContext = this
        this.yasqe = window.YASQE(this.$el, {
            persistent: null,
            sparql: {
                showQueryButton: true,
                endpoint: this.endpoint,
                requestMethod: "POST",
                callbacks: {
                    error () {
                        console.error('YASQE query error', arguments)
                    },
                    success (resp) {
                        yasqeContext.$emit('query-success', resp)
                    },
                }
            },
        })
        this.yasqe.setValue(this.query)
        this.yasqe.setSize("100%", "100%")
    }
})
</script>

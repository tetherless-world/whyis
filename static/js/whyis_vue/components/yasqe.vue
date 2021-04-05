<template>
    <div class="yasqe"></div>
</template>

<script>
import Vue from "vue"

export default Vue.component('yasqe', {
    props: {
        value: {
            type: String,
            default: () => ""
        },
        endpoint: {
            type: String,
            default: () => "/sparql"
        },
        showBtns: {
            type: Boolean,
            default: false
        }
    },
    mounted () {
        const yasqeContext = this
        this.yasqe = window.YASQE(this.$el, {
            persistent: null,
            sparql: {
                showQueryButton: !this.showBtns,
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
            readOnly: true,
        })
        this.yasqe.setValue(this.value)
        this.yasqe.on('changes', () => {
            yasqeContext.$emit('input', yasqeContext.yasqe.getValue())
        })
        this.yasqe.setSize("100%", "100%")
    },
    watch: {
        value() {
            this.yasqe.setValue(this.value)
        }
    }
})
</script>

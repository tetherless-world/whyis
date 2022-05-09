<template>
    <md-card>
        <md-card-header>
            <md-card-header-text>
                <div class="md-title">{{attributes.label}}</div>
                <div v-if="attributes.type.length > 0" class="md-subhead">{{attributes['type'][0].label}}</div>
            </md-card-header-text>
            <md-card-media md-big v-if="attributes.thumbnail">
                <img :src="attributes.thumbnail" :alt="attributes.label"/>
            </md-card-media>
        </md-card-header>
        <md-card-expand>
            <md-card-expand-content>
                <md-card-content>
                    <div v-if="attributes.type.length > 1" layout="row" class="md-subhead">
                        <span v-for="(type, index) in attributes.type">{{type.label}}<span
                                v-if="index < attributes.type.length - 1">, </span> </span>
                    </div>
                    <p v-for="desc in attributes.description"><strong>{{desc.label}}:</strong> {{desc.value}}</p>
                    <p>
                        <strong>Identifier: </strong> {{ attributes['@id']}}
                    </p>
                    <p v-for="attribute in attributes.attributes">
                        <strong>{{attribute.label}}: </strong>
                        <span v-for="(value, index) in attribute.values">
          {{ value.value}} <em v-if="value.unit_label">{{value.unit_label}}</em><span
                                v-if="index < attribute.values.length - 1">, </span>
          </span>
                    </p>
                </md-card-content>
            </md-card-expand-content>
        </md-card-expand>
        <md-card-actions>
            <md-card-expand-trigger>
                <md-button class="md-icon-button">
                    <md-icon>keyboard_arrow_down</md-icon>
                </md-button>
            </md-card-expand-trigger>
        </md-card-actions>
    </md-card>
</template>

<script>
import Vue from "vue";

export default Vue.component('kg-card', {
    data: function() {
        return {};
    },
    props: ['attributes']
});
</script>

<template>
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-start">
            <div>
                <h5 class="card-title mb-1">{{ attributes.label }}</h5>
                <h6 v-if="attributes.type.length > 0" class="card-subtitle text-muted">{{ attributes['type'][0].label }}</h6>
            </div>
            <div v-if="attributes.thumbnail" class="flex-shrink-0 ms-3">
                <img :src="attributes.thumbnail" :alt="attributes.label" class="img-thumbnail" style="width: 80px; height: 80px; object-fit: cover;"/>
            </div>
        </div>
        
        <div class="collapse" :id="'card-expand-' + cardId">
            <div class="card-body">
                <div v-if="attributes.type.length > 1" class="mb-3">
                    <h6 class="text-muted">Types:</h6>
                    <span v-for="(type, index) in attributes.type" :key="index">
                        {{ type.label }}<span v-if="index < attributes.type.length - 1">, </span>
                    </span>
                </div>
                
                <div v-for="desc in attributes.description" :key="desc.label" class="mb-2">
                    <strong>{{ desc.label }}:</strong> {{ desc.value }}
                </div>
                
                <div class="mb-2">
                    <strong>Identifier:</strong> {{ attributes['@id'] }}
                </div>
                
                <div v-for="attribute in attributes.attributes" :key="attribute.label" class="mb-2">
                    <strong>{{ attribute.label }}:</strong>
                    <span v-for="(value, index) in attribute.values" :key="index">
                        {{ value.value}} <em v-if="value.unit_label">{{ value.unit_label }}</em><span v-if="index < attribute.values.length - 1">, </span>
                    </span>
                </div>
            </div>
        </div>
        
        <div class="card-footer">
            <button class="btn btn-outline-secondary btn-sm" type="button" :data-bs-target="'#card-expand-' + cardId" data-bs-toggle="collapse" aria-expanded="false">
                <i class="bi bi-chevron-down"></i>
            </button>
        </div>
    </div>
</template>

<script>
import Vue from "vue";

export default Vue.component('kg-card', {
    data: function() {
        return {
            cardId: Math.random().toString(36).substr(2, 9) // Generate unique ID for collapse functionality
        };
    },
    props: ['attributes']
});
</script>

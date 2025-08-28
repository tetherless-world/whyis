<template>
  <div>
      <button class="btn btn-primary me-2" @click="$emit('apiPost')">Post File</button>
      <button class="btn btn-secondary me-2" @click="$emit('apiGet')">Get File</button>
      <button class="btn btn-outline-secondary me-2" @click="$emit('createCol')" disabled>Add Column</button>
      <button class="btn btn-outline-secondary" @click="$emit('createRow')" disabled>Add Row</button>
  </div>
</template>

<script>
export default {
  name: 'tableControl',
  props: {
    method: { type: Function },
  },
  emits: ['apiPost', 'apiGet', 'createCol', 'createRow']
};
</script>

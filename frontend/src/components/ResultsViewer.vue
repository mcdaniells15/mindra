<!--
  FILE: ResultsViewer.vue
  DESCRIPTION:
    Displays all 3 Grok responses and scoring summary.
-->

<template>
    <div v-if="results">
      <h2>Plain Explanation</h2>
      <p>{{ results.plain }}</p>
      <h2>Mid-Level Explanation</h2>
      <p>{{ results.mid }}</p>
      <h2>Deep Explanation</h2>
      <p>{{ results.deep }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ResultsViewer',
    props: ['results']
  }
  </script>
  
<!--
  FILE: App.vue
  DESCRIPTION:
    Root component of the Mindra frontend.
    Loads layout and handles communication between input and output views.

  COMPONENTS USED:
    - QueryInput.vue: accepts user queries
    - ResultsViewer.vue: shows Grok responses and ML feedback

  LOGIC:
    - Receives query input → sends to backend → displays results
-->

<template>
    <div id="app">
      <h1>Mindra Tutor</h1>
      <QueryInput @query-submitted="setResults" />
      <ResultsViewer v-if="results" :results="results" />
    </div>
  </template>
  
  <script>
  import QueryInput from './components/QueryInput.vue'
  import ResultsViewer from './components/ResultsViewer.vue'
  
  export default {
    name: 'App',
    components: {
      QueryInput,
      ResultsViewer
    },
    data() {
      return {
        results: null
      };
    },
    methods: {
      setResults(data) {
        this.results = data;
      }
    }
  };
  </script>
  
  <style scoped>
  #app {
    padding: 2rem;
    font-family: Arial, sans-serif;
  }
  </style>
  
<!--
  FILE: QueryInput.vue
  DESCRIPTION:
    User enters a query and submits to backend. Emits result to App.
-->

<template>
    <div>
      <form @submit.prevent="submitQuery">
        <input v-model="userQuery" placeholder="Ask a question..." />
        <button type="submit">Submit</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    name: 'QueryInput',
    data() {
      return { userQuery: '' }
    },
    methods: {
      async submitQuery() {
        const res = await fetch('/api/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: this.userQuery })
        });
        const data = await res.json();
        this.$emit('query-submitted', data);
      }
/*Example usage

async submitQuery() {
  const dummyPayload = {
    userId: "user_abc",
    tokenized: {
      keyTerms: ["osmosis", "water", "membrane"],
      numberedSteps: [
        "1. Water moves",
        "2. Across membrane",
        "3. Until balanced"
      ],
      sections: [
        { type: "definition", content: "Osmosis is water moving through a membrane." }
      ]
    },
    metadata: {
      age: 18,
      educationLevel: "college"
    }
  };

  const res = await fetch('/api/score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dummyPayload)
  });

  const data = await res.json();
  this.$emit('query-submitted', data);
}
 */
    }
  }
  </script>
  
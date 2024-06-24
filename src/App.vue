<template>
  <div class="main">
    <CodeView />
  </div>
</template>
<script>
import CodeView from "@/views/CodeView.vue";

export default {
  name: "App",
  components: {
    CodeView
  }
};
</script>
<style>
.main {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
}
</style>

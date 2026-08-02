<script setup>
import GlobalLoading from './components/GlobalLoading.vue'
import GlobalToast from './components/GlobalToast.vue'
</script>

<template>
  <router-view />
  <GlobalLoading />
  <GlobalToast />
</template>

<!-- CesiumContainer.vue — 三维地球 -->
<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as Cesium from 'cesium'

const container = ref(null)
let viewer = null

onMounted(() => {
  viewer = new Cesium.Viewer(container.value, {
    animation: false,
    timeline: false,
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
  })
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(104, 30.5, 500000),
    orientation: { heading: 0, pitch: -Cesium.Math.PI_OVER_FOUR, roll: 0 },
  });
  (window).__cesiumViewer = viewer
})

onUnmounted(() => {
  if (viewer) { viewer.destroy(); viewer = null; delete window.__cesiumViewer }
})

defineExpose({ getViewer: () => viewer })
</script>

<template>
  <div ref="container" style="width:100%;height:100%;"></div>
</template>

<!-- FloatingToolbar.vue -->
<script setup>
import { ref, nextTick, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { fromLonLat, toLonLat } from 'ol/proj'

const mapStore = useMapStore()
const mode = ref('2d')
const syncOn = ref(true)
let viewer = null, ready = false

function resetView() {
  const map = mapStore.map; if (!map) return
  map.getView().animate({ center: fromLonLat([104, 30.5], 'EPSG:3857'), zoom: 6.5, duration: 600 })
}

async function setMode(m) {
  mode.value = m
  if (m === '2d3d') mapStore.closePanel()
  if ((m === '2d3d' || m === '3d') && !ready) {
    await nextTick()
    const Cesium = await import('cesium')
    const el = document.getElementById('cesium-div')
    if (!el || viewer) return
    viewer = new Cesium.Viewer(el, { animation:false, timeline:false, baseLayerPicker:false, geocoder:false, homeButton:false, sceneModePicker:false, navigationHelpButton:false, fullscreenButton:false })
    viewer.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(104,30.5,500000), orientation:{ heading:0, pitch:-Cesium.Math.PI_OVER_FOUR, roll:0 }})
    Cesium.GeoJsonDataSource.load('/geoserver/landslide/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=landslide:landslide&outputFormat=application/json', { stroke:Cesium.Color.RED, fill:Cesium.Color.RED.withAlpha(0.3), markerSize:16 }).then(ds=>viewer.dataSources.add(ds))
    Cesium.GeoJsonDataSource.load('/geoserver/landslide/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=landslide:sichuan_boundary&outputFormat=application/json', { stroke:Cesium.Color.CYAN, strokeWidth:2, fill:Cesium.Color.TRANSPARENT }).then(ds=>viewer.dataSources.add(ds))
    ready = true; setupSync(viewer)
  }
}

// ====== 二三维视角同步 ======
let olHandler = null, csHandler = null, syncing = false

async function setupSync(v) {
  const Cesium = await import('cesium')
  const map = mapStore.map; if (!map || !v) return
  if (olHandler) map.un('moveend', olHandler)

  // OL → Cesium
  olHandler = () => {
    if (syncing || !syncOn.value) return; syncing = true
    const [lon, lat] = toLonLat(map.getView().getCenter(), 'EPSG:3857')
    v.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(lon, lat, 40000000 / Math.pow(2, map.getView().getZoom())), duration: 0.5 })
    setTimeout(() => { syncing = false }, 600)
  }
  map.on('moveend', olHandler)

  // Cesium → OL
  v.camera.moveEnd.addEventListener(() => {
    if (syncing || !syncOn.value) return; syncing = true
    const c = Cesium.Cartographic.fromCartesian(v.camera.position)
    const lon = Cesium.Math.toDegrees(c.longitude)
    const lat = Cesium.Math.toDegrees(c.latitude)
    const zoom = Math.log2(40000000 / Math.max(c.height, 100))
    map.getView().animate({ center: fromLonLat([lon, lat], 'EPSG:3857'), zoom, duration: 300 })
    setTimeout(() => { syncing = false }, 400)
  })
}
</script>

<template>
  <div class="float-tools">
    <button class="ft-btn" title="重置视图" @click="resetView">⌂</button>
    <button class="ft-btn" :class="{ active: mode==='2d' }" @click="setMode('2d')" title="二维">🗺</button>
    <button class="ft-btn" :class="{ active: mode==='2d3d' }" @click="setMode('2d3d')" title="二三维">🌍</button>
    <button class="ft-btn" :class="{ active: mode==='3d' }" @click="setMode('3d')" title="三维">🛰</button>
    <button class="ft-btn sync-btn" :class="{ off: !syncOn }" @click="syncOn = !syncOn" title="视角同步">🔗</button>
  </div>

  <Teleport to="body">
    <div
      v-show="mode === '2d3d' || mode === '3d'"
      :style="{ position: 'fixed', top: 0, bottom: 0, zIndex: 4, left: mode === '2d3d' ? '50%' : '0', width: mode === '2d3d' ? '50%' : '100%' }"
    >
      <div id="cesium-div" style="width:100%;height:100%;"></div>
    </div>
  </Teleport>
</template>

<style scoped>
.float-tools { position: absolute; bottom: 180px; left: calc(19% + 12px); display: flex; flex-direction: column; gap: 6px; z-index: 25; }
.ft-btn { width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; border-radius: 8px; background: var(--bg-panel); border: 1px solid var(--border); color: rgba(200,220,240,0.7); cursor: pointer; font-size: 16px; transition: all .2s; }
.ft-btn:hover { color: #00e5ff; border-color: rgba(0,200,255,0.3); }
.ft-btn.active { color: #00e5ff; border-color: var(--accent); background: rgba(0,212,255,0.1); }
.sync-btn.off { color: rgba(200,220,240,0.3); }
</style>

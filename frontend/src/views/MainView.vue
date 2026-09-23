<!-- MainView.vue -->
<script setup>
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useMapStore } from '@/stores/mapStore'
import { registerProjections } from '@/utils/projections'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import XYZ from 'ol/source/XYZ'
import Zoom from 'ol/control/Zoom'
import ScaleLine from 'ol/control/ScaleLine'
import OverviewMap from 'ol/control/OverviewMap'
import MousePosition from 'ol/control/MousePosition'
import { createStringXY } from 'ol/coordinate'
import { fromLonLat, get as getProjection } from 'ol/proj'
import TopBar from '@/components/TopBar.vue'
import LeftPanel from '@/components/LeftPanel.vue'
import RightPanel from '@/components/RightPanel.vue'
import FloatingToolbar from '@/components/FloatingToolbar.vue'

const mapStore = useMapStore()

onMounted(() => {
  registerProjections()
  console.log('=== 坐标验证 ===')
  console.log('4490:', getProjection('EPSG:4490') ? 'OK' : 'FAIL', 'BD09:', getProjection('EPSG:BD09') ? 'OK' : 'FAIL')

  const TK = import.meta.env.VITE_TK
  const defLayer = new TileLayer({
    source: new XYZ({ url: `http://t{0-7}.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${TK}`, crossOrigin: 'anonymous' }),
    properties: { name: 'tianditu_vec' },
  })

  const map = new Map({
    target: 'ol-map',
    layers: [defLayer],
    view: new View({ projection: 'EPSG:3857', center: fromLonLat([104, 30.5]), zoom: 6.5, minZoom: 1, maxZoom: 19 }),
    controls: [],
  })

  map.addControl(new Zoom({ zoomInLabel: '+', zoomOutLabel: '−' }))
  map.addControl(new ScaleLine({ units: 'metric' }))
  map.addControl(new MousePosition({ coordinateFormat: createStringXY(4), projection: 'EPSG:4326', className: 'custom-mouse-position', target: document.getElementById('mouse-position') }))
  map.addControl(new OverviewMap({ className: 'ol-overviewmap ol-custom-overviewmap', collapsed: false, collapseLabel: '»', label: '«', layers: [new TileLayer({ source: defLayer.getSource() })] }))

  const { map: mapRef } = storeToRefs(mapStore)
  mapRef.value = map; window.__map = map
})
</script>

<template>
  <div class="main-layout">
    <div class="map-area"><div id="ol-map"></div></div>
    <TopBar />
    <LeftPanel />
    <RightPanel />
    <FloatingToolbar />
    <div id="mouse-position"></div>
  </div>
</template>

<style>
.main-layout { width: 100%; height: 100%; position: relative; overflow: hidden; }
.map-area { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
#ol-map { width: 100%; height: 100%; }
.ol-zoom { left: calc(19% + 16px) !important; top: 10px !important; z-index: 10 !important; }
.ol-scale-line { right: calc(19% + 8px) !important; bottom: 8px !important; left: auto !important; z-index: 10 !important; }
.ol-custom-overviewmap { bottom: 10px; left: calc(19% + 8px); right: auto; top: auto; z-index: 10 !important; }
.ol-custom-overviewmap .ol-overviewmap-box { border: 2px solid var(--accent); }
#mouse-position { position: absolute; top: 10px; right: calc(19% + 8px); z-index: 25; color: rgb(218, 241, 10); font-size: 13px; font-weight: bold; background: rgba(10, 25, 50, 0.5); padding: 4px 12px; border-radius: 4px; border: 1px solid rgba(0, 212, 255, 0.15); backdrop-filter: blur(4px); cursor: default; user-select: text; }
</style>

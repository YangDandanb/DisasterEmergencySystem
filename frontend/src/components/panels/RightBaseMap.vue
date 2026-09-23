<!-- RightBaseMap.vue — 底图切换 + 动态投影 -->
<script setup>
import { storeToRefs } from 'pinia'
import { useMapStore } from '@/stores/mapStore'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import XYZ from 'ol/source/XYZ'
import TileGrid from 'ol/tilegrid/TileGrid'
import OverviewMap from 'ol/control/OverviewMap'
import { fromLonLat, toLonLat } from 'ol/proj'
import proj4 from 'proj4'
import Point from 'ol/geom/Point'
import { wgs84ToGcj02, gcj02ToBd09 } from '@/utils/coordTransform'

proj4.defs('EPSG:BD09MC', '+proj=merc +a=6378206 +b=6356584.31424518 +lat_ts=0.0 +lon_0=0.0 +x_0=0 +y_0=0 +k=1.0 +units=m +no_defs')

const mapStore = useMapStore()
const { currentBaseMap } = storeToRefs(mapStore)

const TK = import.meta.env.VITE_TK
const BASE_MAPS = [
  { id: 'tianditu_vec', name: '天地图矢量(默认)', url: 'http://t{0-7}.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=' + TK },
  { id: 'gaode', name: '高德地图', url: 'http://webrd0{1-4}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}' },
  { id: 'tianditu_img', name: '天地图(影像)', url: 'http://t{0-7}.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=' + TK },
  { id: 'baidu', name: '百度地图', url: '', customTileGrid: true },
  { id: 'osm', name: 'OpenStreetMap', url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png' },
  { id: 'arcgis', name: 'ArcGIS 影像', url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' },
]

const layerPool = {}
let poolReady = false

function ensurePool() {
  if (poolReady) return
  BASE_MAPS.forEach(bm => {
    let src
    if (bm.customTileGrid) {
      const resolutions = []
      for (let z = 0; z <= 18; z++) resolutions.push(Math.pow(2, 18 - z))
      src = new XYZ({
        tileGrid: new TileGrid({ origin: [0, 0], resolutions, tileSize: [256, 256] }),
        tileUrlFunction: (tileCoord) => {
          const z = tileCoord[0], x = tileCoord[1], y = -(tileCoord[2] + 1)
          return 'http://online' + ((x + y) % 4) + '.map.bdimg.com/onlinelabel/?qt=tile&x=' + x + '&y=' + y + '&z=' + z + '&styles=pl'
        },
      })
    } else {
      src = new XYZ({ url: bm.url, crossOrigin: 'anonymous' })
    }
    layerPool[bm.id] = new TileLayer({ source: src, visible: false, properties: { name: bm.id } })
  })
  poolReady = true
}

function onSwitch(id) {
  ensurePool()
  const map = mapStore.map
  if (!map) return
  currentBaseMap.value = id
  const newLayer = layerPool[id]
  if (!newLayer) return
  const oldLayer = map.getLayers().getArray().find(l => l instanceof TileLayer && l.get('name'))
  if (oldLayer) map.removeLayer(oldLayer)
  newLayer.setVisible(true)
  map.getLayers().insertAt(0, newLayer)

  map.getLayers().forEach(layer => {
    if (!(layer instanceof VectorLayer)) return
    let s = layer.getSource()
    if (!s) return
    if (s.getSource) s = s.getSource()
    s.forEachFeature(feature => {
      const geom = feature.getGeometry()
      if (!geom) return
      // 首次保存原始 WGS-84 坐标
      let wgs = feature.get("_wgs84")
      if (!wgs) {
        const extent = geom.getExtent()
        const cx = (extent[0] + extent[2]) / 2
        const cy = (extent[1] + extent[3]) / 2
        wgs = toLonLat([cx, cy], "EPSG:3857")
        feature.set("_wgs84", wgs)
      }
      // 基于原始 WGS-84 计算目标位置（无累积误差）
      let [lon, lat] = wgs
      let target
      if (id === "gaode") {
        [lon, lat] = wgs84ToGcj02(lon, lat)
        target = fromLonLat([lon, lat], "EPSG:3857")
      } else if (id === "baidu") {
        [lon, lat] = gcj02ToBd09(...wgs84ToGcj02(lon, lat))
        target = proj4("EPSG:4326", "EPSG:BD09MC", [lon, lat])
      } else {
        target = fromLonLat([lon, lat], "EPSG:3857")
      }
      // 计算偏移量并平移
      const extent = geom.getExtent()
      const cx = (extent[0] + extent[2]) / 2
      const cy = (extent[1] + extent[3]) / 2
      const dx = target[0] - cx
      const dy = target[1] - cy
      if (geom instanceof Point) {
        geom.setCoordinates(target)
      } else {
        geom.translate(dx, dy)
      }
    })
  })

  const ovCtrl = map.getControls().getArray().find(c => c instanceof OverviewMap)
  if (ovCtrl) map.removeControl(ovCtrl)
  map.addControl(new OverviewMap({
    className: 'ol-overviewmap ol-custom-overviewmap',
    collapsed: false, collapseLabel: '»', label: '«',
    layers: [new TileLayer({ source: newLayer.getSource() })],
  }))
}
</script>

<template>
  <div class="base-map-grid">
    <div v-for="bm in BASE_MAPS" :key="bm.id" class="bm-card" :class="{ active: currentBaseMap === bm.id }" @click="onSwitch(bm.id)">
      <div class="bm-icon">🗺️</div><div class="bm-name">{{ bm.name }}</div>
    </div>
  </div>
</template>

<style scoped>
.base-map-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.bm-card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 5px; padding: 14px 6px; text-align: center; cursor: pointer; transition: all .2s; }
.bm-card:hover { border-color: var(--accent); }
.bm-card.active { border-color: var(--accent); box-shadow: 0 0 10px rgba(0,212,255,0.2); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 8px rgba(0,200,255,0.15); } 50% { box-shadow: 0 0 20px rgba(0,200,255,0.35); } }
.bm-icon { font-size: 22px; margin-bottom: 4px; }
.bm-name { font-size: 11px; color: var(--text-secondary); }
</style>
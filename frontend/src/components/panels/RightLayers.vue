<!-- RightLayers.vue — M2 图层管理：创建图层 + 显示开关 -->
<script setup>
import { ref, markRaw, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import GeoJSON from 'ol/format/GeoJSON'
import Cluster from 'ol/source/Cluster'
import Overlay from 'ol/Overlay'
import { Circle as CircleStyle, Fill, Stroke, Style, Text } from 'ol/style'
import Icon from 'ol/style/Icon'
import { boundingExtent } from 'ol/extent'

const mapStore = useMapStore()

const layers = ref([
  { uid: 'sichuan_boundary', title: '四川省边界', type: 'platform', visible: true, olLayer: null },
  { uid: 'landslides', title: '滑坡灾害点', type: 'platform', visible: true, olLayer: null },
  { uid: 'hospitals', title: '医院分布', type: 'platform', visible: false, olLayer: null },
  { uid: 'fire_stations', title: '消防站分布', type: 'platform', visible: false, olLayer: null },
  { uid: 'shelters', title: '避难所分布', type: 'platform', visible: false, olLayer: null },
])

function createSichuanBoundary() {
  return new VectorLayer({
    source: new VectorSource({ url: '/geoserver/landslide/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=landslide:sichuan_boundary&outputFormat=application/json', format: new GeoJSON({ dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' }) }),
    style: new Style({ stroke: new Stroke({ color: '#00d4ff', width: 2 }) }),
  })
}

function createLandslideLayer() {
  const src = new VectorSource({ url: '/geoserver/landslide/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=landslide:landslide&outputFormat=application/json', format: new GeoJSON({ dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' }) })
  const defaultStyle = new Style({ image: new CircleStyle({ radius: 7, fill: new Fill({ color: '#3399CC' }), stroke: new Stroke({ color: '#fff', width: 1.5 }) }) })
  return new VectorLayer({ source: src, style: defaultStyle })
}

function createFacilityLayer(url, srcSvg, clusterColor) {
  const src = new VectorSource({ url, format: new GeoJSON({ dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' }) })
  const cs = new Cluster({ distance: 50, source: src })
  const cache = {}
  return new VectorLayer({
    source: cs,
    style: (f) => {
      const feats = f.get('features'), size = feats.length
      if (size === 1) {
        const k = 's'
        if (!cache[k]) cache[k] = new Style({ image: new Icon({ anchor: [0.5, 0.5], anchorXUnits: 'fraction', anchorYUnits: 'fraction', src: srcSvg, scale: 0.06 }) })
        return cache[k]
      }
      const k = 'c_' + size
      if (!cache[k]) {
        const r = Math.min(12 + size * 0.3, 22)
        cache[k] = new Style({
          image: new CircleStyle({ radius: r, fill: new Fill({ color: clusterColor }), stroke: new Stroke({ color: '#00d4ff', width: 2 }) }),
          text: new Text({ text: size.toString(), fill: new Fill({ color: '#fff' }), font: 'bold 12px sans-serif' }),
        })
      }
      return cache[k]
    },
  })
}

let inited = false
watch(() => mapStore.map, (map) => {
  if (!map || inited) return
  inited = true

  layers.value[0].olLayer = markRaw(createSichuanBoundary())
  map.addLayer(layers.value[0].olLayer)

  layers.value[1].olLayer = markRaw(createLandslideLayer())
  map.addLayer(layers.value[1].olLayer)
  window.__landslideSrc = layers.value[1].olLayer.getSource() // 暴露给左侧图表联动

  const hospLayer = markRaw(createFacilityLayer('/geoserver/landslide/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=landslide:hospital&outputFormat=application/json', '/医院.svg', 'rgba(0,180,240,0.7)'))
  hospLayer.set('title', '医院分布'); hospLayer.setVisible(false)
  layers.value[2].olLayer = hospLayer; map.addLayer(hospLayer)

  const fireLayer = markRaw(createFacilityLayer('/geoserver/landslide/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=landslide:fire_station&outputFormat=application/json', '/消防站.svg', 'rgba(255,120,0,0.7)'))
  fireLayer.set('title', '消防站分布'); fireLayer.setVisible(false)
  layers.value[3].olLayer = fireLayer; map.addLayer(fireLayer)

  const shelterLayer = markRaw(createFacilityLayer('/geoserver/landslide/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=landslide:shelter&outputFormat=application/json', '/避难所.svg', 'rgba(0,200,100,0.7)'))
  shelterLayer.set('title', '避难所分布'); shelterLayer.setVisible(false)
  layers.value[4].olLayer = shelterLayer; map.addLayer(shelterLayer)

  // ====== Popup 气泡弹窗 ======
  const popupEl = document.createElement('div')
  popupEl.className = 'landslide-popup'
  popupEl.style.cssText = 'position:absolute;background:rgba(4,55,118,0.95);color:#e0f0ff;padding:14px 16px;border-radius:6px;border:1px solid rgba(0,212,255,0.3);font-size:13px;line-height:1.8;min-width:220px;pointer-events:auto;z-index:99;box-shadow:0 0 20px rgba(0,0,0,0.5);display:none;'
  const popup = new Overlay({ element: popupEl, autoPan: true, autoPanAnimation: { duration: 250 } })
  map.addOverlay(popup)

  map.on('click', (e) => {
    // 先检查滑坡点
    const lsFeature = map.forEachFeatureAtPixel(e.pixel, f => f, { layerFilter: l => l === layers.value[1].olLayer })
    if (lsFeature) {
      const p = lsFeature.getProperties()
      popupEl.innerHTML = [
        '<div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-weight:bold;color:#00d4ff;font-size:14px;">📋 滑坡详情</span><span id="popup-del-btn" style="cursor:pointer;color:#ff6b6b;font-size:12px;">🗑 删除</span></div>',
        '<div><span style="color:#8899cc;">编号：</span>' + (p.id || '-') + '</div>',
        '<div><span style="color:#8899cc;">等级：</span><span style="color:#ff4444;">' + (p.level_full || p.level || '-') + '</span></div>',
        '<div><span style="color:#8899cc;">位置：</span>' + (p.province || '') + ' ' + (p.city || '') + ' ' + (p.county || '') + '</div>',
        '<div><span style="color:#8899cc;">时间：</span>' + (p.year || '') + '-' + String(p.month || '').padStart(2,'0') + '-' + String(p.day || '').padStart(2,'0') + '</div>',
        '<div><span style="color:#8899cc;">诱因：</span>' + (p.trigger || '-') + '</div>',
        '<div style="margin-top:4px;"><span style="color:#8899cc;">死亡：</span><span style="color:#ff6b6b;">' + (p.deaths || 0) + '</span>  <span style="color:#8899cc;">受伤：</span><span style="color:#ffaa33;">' + (p.injuries || 0) + '</span>  <span style="color:#8899cc;">失踪：</span>' + (p.missing || 0) + '</div>',
        '<div style="text-align:right;font-size:11px;color:#556688;margin-top:6px;">点击空白处关闭</div>',
      ].join('')
      popupEl.style.display = 'block'
      popup.setPosition(lsFeature.getGeometry().getCoordinates())
      // 删除按钮事件
      setTimeout(() => {
        const delBtn = document.getElementById('popup-del-btn')
        if (delBtn) delBtn.onclick = async () => {
          await fetch('/api/landslides/' + p.id, { method: 'DELETE' })
          window.__landslideSrc?.removeFeature(lsFeature)
          popupEl.style.display = 'none'
        }
      }, 50)
      return
    }
    // 聚合点缩放
    const cf = map.getFeaturesAtPixel(e.pixel)?.find(f => f.get('features')?.length > 1)
    if (cf) {
      const members = cf.get('features')
      map.getView().fit(boundingExtent(members.map(r => r.getGeometry().getCoordinates())), { duration: 1000, padding: [50, 50, 50, 50] })
      return
    }
    // 空白处关闭弹窗
    popupEl.style.display = 'none'
  })
}, { immediate: true })

function toggle(uid) {
  const l = layers.value.find(x => x.uid === uid)
  if (!l) return
  l.visible = !l.visible
  if (l.olLayer) l.olLayer.setVisible(l.visible)
}
</script>

<template>
  <div>
    <p style="color:var(--accent);font-size:12px;margin-bottom:8px;">📦 平台层</p>
    <div v-for="l in layers.filter(l => l.type === 'platform')" :key="l.uid" class="layer-row">
      <span style="flex:1;color:#e0f0ff;font-size:12px;">{{ l.title }}</span>
      <el-switch size="small" :model-value="l.visible" @change="toggle(l.uid)" />
    </div>

    <p style="color:var(--accent);font-size:12px;margin:12px 0 8px;">👤 用户层</p>
    <div v-if="!mapStore.userLayers.length" style="color:var(--text-secondary);font-size:11px;text-align:center;padding:12px;">
      暂无用户图层<br/>使用「工具」面板绘制
    </div>
    <div v-for="l in mapStore.userLayers" :key="l.uid" class="layer-row">
      <span style="flex:1;color:#e0f0ff;font-size:12px;">{{ l.title }}</span>
      <el-switch size="small" :model-value="l.visible" @change="mapStore.toggleUserLayer(l.uid)" />
      <span @click="mapStore.removeUserLayer(l.uid)" style="cursor:pointer;color:var(--danger);font-size:12px;margin-left:4px;">✕</span>
    </div>
  </div>
</template>

<style scoped>
.layer-row { display:flex; align-items:center; gap:8px; padding:7px 8px; border-bottom:1px solid var(--border); }
.layer-row:hover { background:rgba(0,212,255,0.04); }
</style>

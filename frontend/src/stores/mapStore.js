/**
 * mapStore.js — 地图 + 用户图层
 */
import { defineStore } from 'pinia'
import { ref, shallowRef } from 'vue'

export const useMapStore = defineStore('map', () => {
  const map = shallowRef(null)
  const activeMenu = ref('')
  const currentBaseMap = ref('tianditu_vec')
  const userLayers = ref([])

  function setActiveMenu(id) { activeMenu.value = activeMenu.value === id ? '' : id }
  function closePanel() { activeMenu.value = '' }

  function addUserLayer(title, olLayer) {
    userLayers.value.push({ uid: 'u_' + Date.now(), title, type: 'user', visible: true, olLayer })
  }
  function removeUserLayer(uid) {
    const l = userLayers.value.find(l => l.uid === uid)
    if (l?.olLayer) { l.olLayer.getSource()?.clear(); map.value?.removeLayer(l.olLayer) }
    userLayers.value = userLayers.value.filter(l => l.uid !== uid)
  }
  function toggleUserLayer(uid) {
    const l = userLayers.value.find(l => l.uid === uid)
    if (l) { l.visible = !l.visible; l.olLayer?.setVisible(l.visible) }
  }

  return { map, activeMenu, currentBaseMap, userLayers, setActiveMenu, closePanel, addUserLayer, removeUserLayer, toggleUserLayer }
})

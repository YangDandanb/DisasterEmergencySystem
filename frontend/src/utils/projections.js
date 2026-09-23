/**
 * projections.js — 自定义投影定义
 * 注册 proj4js 投影到 OpenLayers
 */
import proj4 from 'proj4'
import { register } from 'ol/proj/proj4'

export function registerProjections() {
  proj4.defs('EPSG:4490', '+proj=longlat +ellps=GRS80 +no_defs')
  proj4.defs('EPSG:BD09', '+proj=merc +a=6378206 +b=6356584.31424518 +lat_ts=0.0 +lon_0=0.0 +x_0=0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs')
  register(proj4)
}

# 地质灾害应急救援辅助决策WebGIS平台

## 软件开发技术文档

> **技术决策说明**：按照课程要求，后端必须使用 **Python（FastAPI）**，不使用 SpringBoot。你提供的模板中 SpringBoot 为示例占位，本文档已修正为 FastAPI。

---

## 第一章 项目概述

### 1.1 项目背景

滑坡是我国最常见的地质灾害之一，主要分布于四川、重庆、云南、贵州等山区。滑坡发生后容易造成道路阻断、房屋损毁、人员伤亡。然而传统灾害管理存在信息分散、数据更新慢、决策效率低的问题。

本平台基于 WebGIS 技术，针对滑坡灾害构建集灾害监测、空间分析、风险评估、应急救援于一体的辅助决策系统。系统采用 B/S 架构，用户通过浏览器即可访问全部功能。

### 1.2 建设目标

| 目标 | 说明 |
|------|------|
| 灾害信息可视化 | 滑坡灾害点在地图上直观展示，支持多源底图切换和动态投影 |
| 空间分析能力 | 缓冲区分析、最近设施查找、最优路径规划 |
| 风险评估能力 | 基于坡度、水系距离、历史分布生成风险区划图 |
| 应急救援辅助 | 实时显示周边医院、消防站、避难所，计算到达时间 |
| 统计分析 | 多维度灾害数据统计，ECharts 图表可视化 |

---

## 第二章 需求分析

### 2.1 功能需求

#### （1）地图浏览与控件

| 功能 | 实现方式 |
|------|----------|
| 地图缩放/平移 | `ol.control.Zoom` + 鼠标滚轮 + 拖拽 |
| 比例尺 | `ol.control.ScaleLine`，动态跟随缩放级别 |
| 鹰眼图 | `ol.control.OverviewMap`，右下角全局概览 |
| 鼠标位置 | `ol.control.MousePosition`，度分秒/十进制可切换 |
| 图层管理 | 自定义 LayerSwitcher，树形展示+透明度调节 |

#### （2）底图切换

支持 6 种底图，切换时矢量数据跟随动态投影：

| 底图 | 坐标系 | 数据源 |
|------|--------|--------|
| 天地图（矢量） | CGCS2000 (EPSG:4490) | tianditu.gov.cn WMTS |
| 天地图（影像） | CGCS2000 (EPSG:4490) | tianditu.gov.cn WMTS |
| 高德地图 | GCJ-02 | autonavi.com XYZ |
| 百度地图 | BD-09 | baidu.com XYZ（自定义 TileGrid） |
| OpenStreetMap | WGS-84 (EPSG:3857) | openstreetmap.org XYZ |
| 必应地图 | EPSG:3857 | bing.com Tile |

#### （3）图层管理

系统管理以下图层，**仅滑坡灾害点、行政边界、医院、消防站、避难所五个图层展示在地图上**，路网、水系、DEM 仅用于后台分析，不展示：

| 分类 | 图层 | 展示 | 数据来源 | 可编辑 | 用途说明 |
|------|------|------|----------|--------|----------|
| 平台层 | 行政区边界 | ✅ 展示 | GeoJSON | 否 | 底图叠加 |
| 平台层 | 道路网络 | ❌ 不展示 | PostGIS | 否 | 仅用于 pgRouting 路径规划 |
| 平台层 | 河流水系 | ❌ 不展示 | PostGIS | 否 | 仅用于风险评估（距河流距离） |
| 平台层 | DEM 地形 | ❌ 不展示 | 栅格文件 | 否 | 仅用于风险评估（坡度提取） |
| 用户层 | 滑坡灾害点 | ✅ 展示 | PostGIS WFS | 是 | 核心业务数据 |
| 用户层 | 风险区划图 | ✅ 展示 | GeoServer WMS | 否 | 风险评估结果 |
| 用户层 | 医院分布 | ✅ 展示 | PostGIS WFS | 是 | 应急设施 |
| 用户层 | 避难所分布 | ✅ 展示 | PostGIS WFS | 是 | 应急设施 |
| 用户层 | 消防站分布 | ✅ 展示 | PostGIS WFS | 是 | 应急设施 |
| 用户层 | 救援路径 | ✅ 动态展示 | 前端绘制 | 是 | 路径规划结果 |
| 用户层 | 缓冲区 | ✅ 动态展示 | 前端绘制 | 是 | 缓冲区分析结果 |

每层支持：可见性开关、透明度滑块、图例显示。

#### （4）灾害信息查询

- **点击查询**：点击地图上的滑坡点 → 弹出信息窗口（编号、等级、时间、规模、影响人数）
- **条件查询**：按灾害等级、时间范围、区域筛选 → 表格列表展示结果
- **空间查询**：框选矩形/绘制多边形 → 返回区域内所有灾害点

#### （5）风险评估分析

基于以下因子加权叠加生成风险区划图：
- 坡度（DEM 计算）— 权重 40%
- 距河流距离（缓冲区）— 权重 30%
- 历史滑坡密度（核密度）— 权重 30%

结果分三级：高风险区（红）、中风险区（橙）、低风险区（黄）。

#### （6）应急救援分析

- **最近设施查找**：选定灾害点 → 自动查找最近医院、最近消防站、最近避难所
- **距离计算**：基于路网的实际距离 + 直线距离（对比展示）
- **到达时间估算**：按道路等级设定速度（高速 80km/h、国道 60km/h、县道 40km/h）

#### （7）路径规划

- 起点：救援站（消防站/应急中心）
- 终点：滑坡灾害点
- 算法：使用 PostGIS `pgr_dijkstra()` 基于道路网络计算最优路径
- 展示：地图上高亮显示路线 + 距离 + 预计时间

#### （7.1）路径规划自适应半径策略

为避免全量路网拓扑构建带来的性能瓶颈，路径规划采用 **"自适应半径 + 按需提取"** 策略：

**核心逻辑**：系统自动计算滑坡点与救援站之间的直线距离，按该距离的 1.5 倍自动提取局部路网进行拓扑构建，无需用户手动调参。

| 步骤 | 说明 |
|------|------|
| 1. 计算直线距离 | 使用 haversine 公式计算滑坡点 ↔ 救援站的直线距离 d（单位：km） |
| 2. 确定路网范围 | 路网提取半径 R = d × 1.5，确保路网覆盖起终点并留有余量 |
| 3. 构建局部拓扑 | 以滑坡点为中心，R 为半径提取路网，构建临时拓扑 |
| 4. 执行路径规划 | 调用 `pgr_dijkstra` 计算最短路径，返回路线 GeoJSON |
| 5. 兜底处理 | 若 d < 5km → R 取 5km；若 d > 30km → 提示用户"距离过远，建议选择更近的救援站" |

**设计优势**：近距离救援站 → 提取小范围路网 → 计算速度极快（< 1 秒）；远距离救援站 → 自动扩大范围 → 保证路径可达；用户全程无需操作，一键完成路径规划；大幅降低全量拓扑构建的时间开销。

#### （8）绘制工具

- 点标记（灾害点标注）
- 线绘制（疏散路线）
- 面绘制（影响范围标注）
- 圆绘制（缓冲区分析范围）

#### （9）量算工具

- 距离量算：连续点击 → 多段累加显示总距离
- 面积量算：绘制多边形 → 实时显示面积

#### （10）统计分析

- 热力图：滑坡灾害密度热力分布
- 按灾害等级统计（饼图）
- 按年份统计（柱状图/折线图）
- 按省份统计（横向柱状图）
- 年度变化趋势（折线图）

#### （11）实时滑坡点添加功能

系统支持用户添加新的滑坡点，用于模拟实时灾害发生后的应急救援分析。该功能包含两种输入方式：

**方式一：手动输入经纬度**：用户在表单中输入经度、纬度、灾害名称、等级、触发因素、描述等信息，系统校验坐标格式，自动存储到数据库。

**方式二：地图点选**：用户点击"绘制点"工具，在地图上任意位置点击，系统自动读取该位置的经纬度，弹出属性填写表单，用户补充灾害信息后提交保存。

**添加后自动触发分析流程**：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 数据入库 | 新滑坡点写入 `landslide` 表，带 `is_real_time` 标记（区分历史数据） |
| 2 | 地图刷新 | 地图上新增该点，使用特殊颜色（如闪烁红色）区分历史点 |
| 3 | 自动风险评分 | 后台提取该点的坡度值、距最近河流距离、周边历史滑坡密度 → 计算综合风险评分 |
| 4 | 展示结果 | 左侧面板显示该点的风险评分（高/中/低）及详细因子数值 |
| 5 | 后续分析 | 用户可围绕该点执行缓冲区分析、最近设施查找、路径规划等操作 |

### 2.2 非功能需求

| 类别 | 指标 |
|------|------|
| 性能 | 地图加载 < 5s，查询响应 < 2s |
| 兼容性 | Chrome、Edge、Firefox |
| 可扩展性 | 支持新增泥石流、崩塌等灾害类型 |
| 安全性 | JWT 用户认证（可选） |

---

## 第三章 系统总体设计

### 3.1 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | 3.4+ |
| 构建工具 | Vite | 5.x |
| 地图库 | OpenLayers | 10.x |
| UI 组件 | Element Plus | 2.x |
| 图表 | ECharts | 5.x |
| 状态管理 | Pinia | 2.x |
| HTTP | Axios | 1.x |
| 投影 | proj4js | 2.x |
| 后端框架 | FastAPI (Python) | 0.111+ |
| ORM | SQLAlchemy + GeoAlchemy2 | 2.x |
| 空间处理 | GDAL/OGR (python) | 3.x |
| 数据库 | PostgreSQL + PostGIS | 15 + 3.x |
| GIS 服务 | GeoServer | 2.25 |
| 容器化 | Docker Compose | — |

### 3.2 系统架构图

```
┌─────────────────────────────────────────────────────┐
│              Browser (Vue3 + OpenLayers)             │
│  ┌─────────┐ ┌──────────┐ ┌───────────────────────┐ │
│  │OpenLayers│ │Element+  │ │ECharts + Pinia        │ │
│  │地图核心  │ │侧边栏面板│ │统计图表 + 状态管理     │ │
│  └─────────┘ └──────────┘ └───────────────────────┘ │
├──────┬──────────────┬──────────────┬────────────────┤
│Axios │ XYZ/WMTS     │ WMS/WFS 请求  │ 底图瓦片请求    │
│REST  │ (天地图等)   │ (GeoServer)   │ (高德/百度/OSM) │
├──────┴──────────────┴──────────────┴────────────────┤
│              FastAPI (Python) 后端                   │
│  ┌──────────┐ ┌──────────┐ ┌─────────────────────┐  │
│  │ REST API │ │ 业务逻辑  │ │ GDAL 空间分析        │  │
│  │ 路由层   │ │ 服务层    │ │ (缓冲区/坡度/密度)   │  │
│  └──────────┘ └──────────┘ └─────────────────────┘  │
├──────────────────────┬──────────────────────────────┤
│  SQLAlchemy 直连     │  GeoServer 2.25              │
│  (CRUD + 统计查询)   │  (WMS/WMTS/WFS 标准服务)     │
├──────────────────────┴──────────────────────────────┤
│       PostgreSQL 15 + PostGIS 3                      │
│       (空间数据库 + pgRouting 路径规划)              │
└─────────────────────────────────────────────────────┘
```

### 3.3 架构分层说明

| 层 | 职责 |
|----|------|
| 表现层 (Vue3) | 页面展示、用户交互、地图渲染、图表 |
| 业务层 (FastAPI) | RESTful API、数据查询、空间分析调度、业务逻辑 |
| GIS 服务层 (GeoServer) | WMS/WMTS/WFS 标准 OGC 服务发布 |
| 数据层 (PostGIS) | 空间数据存储、空间索引、pgRouting |

---

## 第四章 数据准备

### 4.1 行政区边界数据

- 来源：阿里云 DataV GeoAtlas（http://datav.aliyun.com/portal/school/atlas/area_selector）
- 格式：GeoJSON
- 层级：全国 → 省 → 市

### 4.2 道路网络数据

- 来源：Geofabrik / OpenStreetMap
- 格式：Shapefile / GeoJSON
- 字段：道路名称、道路等级（高速/国道/省道/县道）
- 用途：pgRouting 路径规划（不在地图上展示）

### 4.3 河流水系数据

- 来源：Geofabrik / OpenStreetMap
- 格式：Shapefile
- 用途：风险评估 — 距河流距离因子（不在地图上展示）

### 4.4 DEM 数字高程数据

- 来源：NASA SRTM（Shuttle Radar Topography Mission）
- 分辨率：30m
- 格式：GeoTIFF
- 用途：坡度计算 — 风险评估因子（不在地图上展示）

### 4.5 滑坡灾害数据

**方案 A（真实数据）**：NASA Global Landslide Catalog
- 全球历史滑坡记录，包含经纬度、时间、触发因素
- 字段：id, latitude, longitude, event_date, landslide_type, fatality_count

**方案 B（模拟数据，兜底方案）**：Python 脚本生成
- 以四川、云南、贵州、重庆为重点区域
- 随机生成 50~100 个滑坡点
- 字段：id, name, longitude, latitude, event_time, level（Ⅰ/Ⅱ/Ⅲ/Ⅳ）, scale, affected_people

**建议**：方案 A 作为基础 + 方案 B 补充缺失字段。

### 4.6 应急设施数据

| 数据类型 | 来源 | 数量 |
|----------|------|------|
| 医院 | OSM (amenity=hospital) | ~500 全国 |
| 消防站 | OSM (amenity=fire_station) | ~200 全国 |
| 避难所 | 模拟数据生成 | ~100 全国 |

### 4.7 数据使用总览表

本章节汇总所有数据的来源、用途和使用方式，明确哪些数据用于地图展示、哪些数据仅用于后台分析。

| 数据 | 来源 | 是否展示 | 展示方式 | 分析用途 | 存储方式 |
|------|------|----------|----------|----------|----------|
| 滑坡灾害点 | 国家地球系统科学数据中心 | ✅ 展示 | WFS 点图层，按等级分色渲染 | 查询、统计、缓冲区分析、风险评分 | PostGIS |
| 行政边界 | 阿里云 DataV GeoAtlas | ✅ 展示 | WMS 线面图层 | 区域裁剪、空间过滤 | PostGIS |
| 医院 POI | 高德 API | ✅ 展示 | WFS 点图层，特殊图标 | 最近设施查找、路径规划终点 | PostGIS |
| 消防站 POI | 高德 API | ✅ 展示 | WFS 点图层，特殊图标 | 最近设施查找、路径规划起点 | PostGIS |
| 避难所 POI | 高德 API | ✅ 展示 | WFS 点图层，特殊图标 | 最近设施查找 | PostGIS |
| 路网 | Geofabrik (OSM) | ❌ 不展示 | — | pgRouting 路径规划 | PostGIS |
| 河流水系 | Geofabrik (OSM) | ❌ 不展示 | — | 风险评估（距河流距离计算） | PostGIS |
| DEM / 坡度图 | NASA SRTM | ❌ 不展示 | — | 风险评估（坡度值提取） | 栅格文件 |

> **设计说明**：路网、水系、DEM 不展示在地图上，原因如下：
> 1. 路网数据量大，展示会覆盖底图上的道路信息，反而造成视觉混乱。用户通过底图（天地图/高德/OSM）已能清晰看到道路分布。
> 2. 水系面同样数据量大，且用户关注的核心是滑坡点和救援设施，而非地理底图细节。
> 3. 上述数据仅在后台用于路径规划（路网）和风险评估（水系、DEM），结果以分析图层的形式（如高亮路线、缓冲区圆、风险评分标签）呈现给用户。

---

## 第五章 数据库设计


### 5.1 滑坡灾害表 (landslide)

```sql
CREATE TABLE landslide (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200),              -- 灾害点名称
    event_time    TIMESTAMP,                 -- 发生时间
    level         VARCHAR(10),               -- 灾害等级 (Ⅰ/Ⅱ/Ⅲ/Ⅳ)
    scale         VARCHAR(20),               -- 规模描述 (小型/中型/大型/特大型)
    affected_people INTEGER,                 -- 影响人数
    trigger_factor VARCHAR(50),              -- 触发因素 (降雨/地震/人为)
    description   TEXT,                      -- 描述
    geom          GEOMETRY(Point, 4326),     -- 空间位置 (WGS-84)
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);

-- 空间索引
CREATE INDEX idx_landslide_geom ON landslide USING GIST (geom);
-- 时间索引
CREATE INDEX idx_landslide_time ON landslide (event_time);
```

### 5.2 医院表 (hospital)

```sql
CREATE TABLE hospital (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(200),
    address  VARCHAR(500),
    level    VARCHAR(10),                    -- 医院等级 (三甲/三乙/二甲)
    capacity INTEGER,                        -- 床位数
    contact  VARCHAR(50),                    -- 联系电话
    geom     GEOMETRY(Point, 4326)
);

CREATE INDEX idx_hospital_geom ON hospital USING GIST (geom);
```

### 5.3 避难所表 (shelter)

```sql
CREATE TABLE shelter (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(200),
    capacity INTEGER,                        -- 容纳人数
    type     VARCHAR(50),                    -- 类型 (学校/广场/体育馆)
    geom     GEOMETRY(Point, 4326)
);

CREATE INDEX idx_shelter_geom ON shelter USING GIST (geom);
```

### 5.4 消防站表 (fire_station)

```sql
CREATE TABLE fire_station (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(200),
    address  VARCHAR(500),
    contact  VARCHAR(50),
    geom     GEOMETRY(Point, 4326)
);

CREATE INDEX idx_fire_geom ON fire_station USING GIST (geom);
```

### 5.5 道路表 (road) — pgRouting

```sql
-- 道路节点表
CREATE TABLE road_vertices (
    id    BIGINT PRIMARY KEY,
    geom  GEOMETRY(Point, 4326)
);

-- 道路边表 (pgRouting 要求 source/target/cost)
CREATE TABLE road_edges (
    id        BIGINT PRIMARY KEY,
    source    BIGINT REFERENCES road_vertices(id),
    target    BIGINT REFERENCES road_vertices(id),
    cost      FLOAT,                        -- 通行成本 (长度/速度)
    reverse_cost FLOAT,                     -- 反向成本
    road_name VARCHAR(200),
    road_level VARCHAR(20),                 -- highway/primary/secondary
    speed     INTEGER,                      -- 设计时速 km/h
    geom      GEOMETRY(LineString, 4326)
);

CREATE INDEX idx_road_edges_geom ON road_edges USING GIST (geom);
CREATE INDEX idx_road_edges_source ON road_edges (source);
CREATE INDEX idx_road_edges_target ON road_edges (target);
```

### 5.6 用户表 (user) — 可选

```sql
CREATE TABLE "user" (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,          -- bcrypt 加密
    role     VARCHAR(20) DEFAULT 'viewer'   -- admin/editor/viewer
);
```

---

## 第六章 前端页面设计

> **设计参照**：xm-webgis-bs 项目的全屏地图 + 绝对定位覆盖面板布局模式，使用 Vue3 + Element Plus + TypeScript 重写。

### 6.1 整体布局

```
┌─────────────────────────────────────────────────────┐
│                   顶部标题栏                         │
│    地质灾害应急救援辅助决策WebGIS平台                 │
├──────┬──────────────────────────────┬───────────────┤
│      │         菜单栏               │               │
│      │  [底图] [图层] [查询]       │ [分析] [工具]  │
├──────┼──────────────────────────────┼───────────────┤
│ 左   │                              │  右           │
│ 侧   │                              │  侧           │
│ 信   │        OpenLayers 地图       │  面           │
│ 息   │        (width: 60%)          │  板           │
│ 面   │                              │  (width: 20%) │
│ 板   │                              │               │
│      │                              │  根据菜单切换  │
│ (永  │                              │  显示不同面板  │
│ 久   │                              │               │
│ 可   │                              │               │
│ 见)  ├──────────────────────────────┤               │
│      │     底部统计图表栏           │               │
│width │     (ECharts 图表)           │               │
│ 20%  │                              │               │
└──────┴──────────────────────────────┴───────────────┘
```

### 6.2 左侧信息面板（永久可见，宽 20%）

参照 xm-webgis-bs 的 LeftRow 布局，从上到下三个区域：

**区域一：实时概要**
- 滑坡点总数、今日新增、高风险点数、受影响人数
- 数据卡片样式（Element Plus `el-statistic`）

**区域二：灾害等级统计**
- ECharts 环形图 — 按灾害等级（Ⅰ/Ⅱ/Ⅲ/Ⅳ）分布
- 带图例和百分比标签

**区域三：省份排名**
- 横向柱状图 — 各省滑坡数量 Top 10
- 每 5 秒自动轮播滚动

### 6.3 右侧功能面板（宽 20%，根据菜单切换滑入）

参照 xm-webgis-bs 的 M0~M6 右侧面板设计：

| 面板 ID | 名称 | 内容 |
|---------|------|------|
| M1 | 底图切换 | 6 种底图缩略图卡片，点击切换；当前选中高亮 |
| M2 | 图层管理 | 平台层 + 用户层列表，每项：可见开关 + 透明度滑块 + 图例 + 删除按钮（用户层） |
| M3 | 查询面板 | 折叠面板：关键词搜索 + 等级筛选 + 时间范围 + 空间框选 → 结果表格 |
| M4 | 工具面板 | 绘制工具（点/线/面/圆）+ 量算工具 + 书签管理 |
| M5 | 分析面板 | 热力图生成 + 风险区划图加载 + 最近设施查找 + 缓冲区分析 |
| M6 | 关于 | 平台介绍、数据来源说明、操作帮助 |

### 6.4 菜单栏

居中悬浮菜单，左右分组：
- 左组：【底图】【图层】【查询】
- 右组：【分析】【工具】【关于】

点击菜单项 → 切换右侧面板显示（CSS `--right` 变量控制：0=显示，-500px=隐藏）。

### 6.5 底部统计栏

折叠式底部面板：
- 年度灾害趋势折线图（X 轴：年份，Y 轴：灾害数量）
- 月度分布热力日历图
- 触发因素占比饼图（降雨/地震/人为/未知）

### 6.6 浮动工具栏

参照 xm-webgis-bs 的 ToolBar：
- 位置：absolute，左侧面板右边，底部统计栏上方
- 按钮：重置视图、测距、测面、清除绘制、保存书签

### 6.7 组件目录结构

```
frontend/src/
├── views/
│   └── MainView.vue                 # 主视图（唯一页面，全屏地图布局）
├── components/
│   ├── map/
│   │   └── MapContainer.vue         # 地图初始化 + 底图管理
│   ├── panels/
│   │   ├── LeftPanel.vue            # 左侧永久面板容器
│   │   ├── LeftTop.vue              # 实时概要卡片
│   │   ├── LeftCenter.vue           # 灾害等级环形图
│   │   ├── LeftBottom.vue           # 省份排名柱状图
│   │   ├── RightPanel.vue           # 右侧滑入面板容器
│   │   ├── RightBaseMap.vue         # M1 - 底图切换
│   │   ├── RightLayers.vue          # M2 - 图层管理
│   │   ├── RightQuery.vue           # M3 - 查询面板
│   │   ├── RightTools.vue           # M4 - 工具面板
│   │   ├── RightAnalysis.vue        # M5 - 分析面板
│   │   └── RightAbout.vue           # M6 - 关于
│   ├── toolbar/
│   │   └── FloatingToolbar.vue      # 浮动工具按钮
│   └── common/
│       ├── StatCard.vue             # 数据卡片
│       └── LayerItem.vue            # 图层列表项
├── composables/
│   ├── useMap.ts                    # 地图实例 + 图层管理
│   ├── useBaseMap.ts               # 底图切换逻辑
│   ├── useDraw.ts                   # 绘制交互
│   ├── useMeasure.ts               # 量算交互
│   ├── useQuery.ts                  # 查询逻辑
│   └── useProjection.ts            # 投影动态切换
├── stores/
│   ├── mapStore.ts                  # 地图状态 (activeMenu, layers, projection)
│   └── dataStore.ts                 # 业务状态 (landslides, hospitals, statistics)
├── api/
│   ├── index.ts                     # Axios 实例
│   ├── landslide.ts                 # 滑坡 API
│   ├── facility.ts                  # 设施 API
│   └── statistics.ts               # 统计 API
├── utils/
│   ├── projections.ts              # proj4 投影定义
│   ├── coordTransform.ts           # WGS/GCJ/BD 坐标互转
│   └── mapConfig.ts                # 底图 URL 配置
├── router/index.ts
├── App.vue
└── main.ts
```

---

## 第七章 后端接口设计

### 7.1 滑坡灾害接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/landslides` | 查询列表（支持 bbox 空间过滤、等级、时间范围） |
| GET | `/api/landslides/{id}` | 单条详情 |
| POST | `/api/landslides` | 新增灾害点 |
| PUT | `/api/landslides/{id}` | 更新灾害点 |
| DELETE | `/api/landslides/{id}` | 删除灾害点 |
| GET | `/api/landslides/export` | 导出为 GeoJSON / Excel |

### 7.2 应急设施接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/hospitals` | 医院列表（支持 nearest 参数按点排序） |
| GET | `/api/shelters` | 避难所列表（支持 nearest 参数） |
| GET | `/api/fire-stations` | 消防站列表（支持 nearest 参数） |

### 7.3 空间分析接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/analysis/buffer` | 缓冲区分析（输入点 + 半径 → 返回缓冲区内设施） |
| POST | `/api/analysis/nearest` | 最近设施查找（输入点 + 设施类型 → 返回最近 N 个） |
| POST | `/api/analysis/shortest-path` | 最短路径规划（起止点 → pgRouting 计算） |
| GET | `/api/analysis/risk-zone` | 风险区划（返回 GeoJSON 多边形） |
| GET | `/api/analysis/heatmap` | 滑坡密度热力数据 |

### 7.4 统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/statistics/by-level` | 按灾害等级统计 |
| GET | `/api/statistics/by-year` | 按年份统计 |
| GET | `/api/statistics/by-province` | 按省份统计 |
| GET | `/api/statistics/by-trigger` | 按触发因素统计 |
| GET | `/api/statistics/overview` | 概览数据（总数、新增、高风险数） |

### 7.5 GeoServer OGC 接口（Vite 代理）

| 服务 | 代理路径 | 说明 |
|------|----------|------|
| WMS | `/geoserver/landslide/wms` | GetMap / GetFeatureInfo |
| WMTS | `/geoserver/gwc/service/wmts` | 瓦片缓存 |
| WFS | `/geoserver/landslide/wfs` | GetFeature (GeoJSON) / Transaction |

### 7.6 后端目录结构

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── landslides.py          # 滑坡 CRUD
│   │   ├── facilities.py          # 设施查询
│   │   ├── analysis.py            # 空间分析
│   │   └── statistics.py          # 统计接口
│   ├── core/
│   │   ├── config.py              # 配置 (数据库连接串、CORS)
│   │   └── database.py            # SQLAlchemy + GeoAlchemy2 引擎
│   ├── models/
│   │   ├── landslide.py
│   │   ├── facility.py
│   │   └── road.py
│   ├── schemas/
│   │   ├── landslide.py           # Pydantic 请求/响应模型
│   │   └── analysis.py
│   ├── services/
│   │   ├── landslide_service.py   # 业务逻辑
│   │   ├── spatial_service.py     # 空间分析 (PostGIS 查询)
│   │   └── statistics_service.py  # 统计聚合
│   └── main.py                    # FastAPI 应用入口
├── alembic/                        # 数据库迁移
├── requirements.txt
└── docker-compose.yml              # PostGIS + GeoServer
```

---

## 第八章 系统测试

### 8.1 功能测试

| 功能模块 | 测试内容 | 预期结果 |
|----------|----------|----------|
| 地图加载 | 打开页面 | 地图显示，缩放/平移正常，控件可见 |
| 底图切换 | 逐一切换 6 种底图 | 瓦片加载正常，无白块 |
| 动态投影 | 天地图→百度地图 加载同一 GeoJSON | 点位偏差 < 50m |
| 图层管理 | 开关图层、调节透明度 | 图层即时响应 |
| 点击查询 | 点击滑坡点 | 弹出信息窗口，属性正确 |
| 条件查询 | 按等级/时间筛选 | 表格结果正确过滤 |
| 距离量算 | 测量已知参考距离 | 误差 < 5% |
| 面积量算 | 测量已知参考面积 | 误差 < 5% |
| 绘制工具 | 绘制点/线/面并保存 | 数据持久化到数据库 |
| 缓冲区分析 | 选点 → 5km 缓冲区 | 返回缓冲区内设施列表 |
| 路径规划 | 消防站→滑坡点 | 生成路线 + 距离 + 时间 |
| 统计图表 | 查看各统计图表 | 数据与数据库一致 |
| 热力图 | 生成滑坡热力图 | 热点区域正确显示 |

### 8.2 性能测试

| 场景 | 数据量 | 指标 |
|------|--------|------|
| 地图初始加载 | — | < 5 秒 |
| 灾害点列表加载 | 100 个点 | < 1 秒 |
| 灾害点列表加载 | 500 个点 | < 2 秒 |
| 灾害点列表加载 | 1000 个点 | < 3 秒 |
| 缓冲区分析 | — | < 2 秒 |
| 路径规划 | 全国路网 | < 3 秒 |

### 8.3 兼容性测试

| 浏览器 | 版本 | 结果 |
|--------|------|------|
| Chrome | 最新版 | ✓ |
| Edge | 最新版 | ✓ |
| Firefox | 最新版 | ✓ |

---

## 第九章 课程知识点覆盖

| 知识点 | 覆盖方式 |
|--------|----------|
| ✅ WebGIS 架构 | B/S 三层架构 + GeoServer GIS 服务层 |
| ✅ OpenLayers 地图开发 | 地图渲染、控件、交互、图层管理 |
| ✅ 图层管理 | 平台层/用户层分类，可见性+透明度控制 |
| ✅ 多源底图切换 | 天地图/高德/百度/OSM/Bing（6 种） |
| ✅ 动态投影 | proj4js + OpenLayers，WGS-84 ↔ GCJ-02 ↔ BD-09 |
| ✅ 地图控件 | 缩放、比例尺、鹰眼、鼠标位置、图层树 |
| ✅ 属性查询 | 点击查询 + 条件查询 + 空间框选查询 |
| ✅ 空间查询 | bbox 过滤、空间关系查询 (ST_Within/ST_Intersects) |
| ✅ 缓冲区分析 | PostGIS ST_Buffer，前端交互式半径输入 |
| ✅ 最近设施分析 | PostGIS ST_Distance + ORDER BY + LIMIT |
| ✅ 路径规划 | pgRouting Dijkstra 算法 + 道路网络 |
| ✅ WMS 服务 | GeoServer 发布 + 前端 `ol.source.TileWMS` 加载 |
| ✅ WMTS 服务 | GeoServer GeoWebCache + `ol.source.WMTS` 加载 |
| ✅ WFS 服务 | GeoServer 发布 + `ol.source.Vector` + `ol.format.WFS` |
| ✅ PostGIS 空间数据库 | 空间数据类型、GIST 索引、空间函数 |
| ✅ 矢量绘制 | `ol.interaction.Draw` 点/线/面/圆 |
| ✅ 距离量算 | `ol.sphere.getLength()` 椭球面测距 |
| ✅ 面积量算 | `ol.sphere.getArea()` 椭球面测面积 |
| ✅ 热力图 | `ol/layer/Heatmap` 核密度可视化 |
| ✅ ECharts 可视化 | 饼图/柱状图/折线图/散点图 |
| ✅ RESTful API | FastAPI + Swagger 文档 |

---

## 第十章 开发计划（2 周半）

| 阶段 | 天数 | 任务 | 产出 |
|------|------|------|------|
| 1 | Day 1-2 | 环境搭建：Vite+Vue3 项目初始化、FastAPI 项目初始化、Docker 启动 PostGIS+GeoServer | 可运行的空项目 |
| 2 | Day 3-5 | 地图核心：OpenLayers 集成、6 种底图配置+切换、7 种控件、动态投影 | 多底图可切换地图 |
| 3 | Day 6-8 | 后端搭建：数据库模型+迁移、5 张表 CRUD API、GeoServer 图层发布、模拟数据生成 | 完整后端 + WMS/WFS |
| 4 | Day 9-11 | 前端面板：左侧面板（概要+图表）、右侧面板（底图/图层/查询/工具/分析）、底部统计栏 | 功能完整的界面 |
| 5 | Day 12-14 | 高级功能：路径规划、缓冲区分析、最近设施、热力图、前后端联调 | 核心业务功能 |
| 6 | Day 15-17 | 文档撰写、整体联调、样式优化、Bug 修复、演示准备 | 可演示系统 + 设计文档 |

---

## 第十一章 前端UI设计方案（最新修订版）

> **2026-06-26 修订**：完全推翻之前的全屏地图+玻璃面板方案。
> 经讨论确认：**DataV大屏风格 + Flexbox地图居中 + 左右不透明卡片面板**。

### 11.1 整体设计方向

| 维度 | 选择 |
|------|------|
| 风格 | **DataV 数据可视化大屏**（深色底+霓虹边框+科技感） |
| 布局 | **CSS Flexbox 三栏布局**（左20% + 地图60% + 右20%），不透明面板 |
| 面板风格 | **卡片式**：面板内用独立卡片承载各模块，卡片间留空隙 |
| 菜单 | **顶部水平菜单栏**（居中，分组） |
| 左侧面板内容 | 统计卡片 + 实时监测数据 + 可搜索灾害点列表 |
| 右侧面板内容 | 菜单切换功能面板（图源/图层/查询/工具/分析/关于） |

### 11.2 布局结构图

```
┌─────────────────────────────────────────────────────────────┐
│    ════════════ 地质灾害应急救援辅助决策WebGIS平台 ════════════   │
│           [图源][图层][查询]  │  [分析][工具][关于]               │
├──────────┬────────────────────────────────┬─────────────────┤
│ 左侧面板 │                                │  右侧面板         │
│ (20%)   │         OpenLayers 地图         │  (20%)           │
│         │          (60%)                  │                  │
│ ┌──────┐ │                                │  ┌────────────┐  │
│ │ 统计  │ │   🗺 滑坡灾害点               │  │ 菜单切换内容 │  │
│ │ 卡片  │ │   🏥 医院 🏕 避难所            │  │            │  │
│ └──────┘ │                                │  │ M1-M6      │  │
│ ┌──────┐ │                                │  │            │  │
│ │ 监测  │ │                                │  └────────────┘  │
│ │ 卡片  │ │                                │                  │
│ └──────┘ │                                │                  │
│ ┌──────┐ │                                │                  │
│ │ 列表  │ │                                │                  │
│ │ 卡片  │ │                                │                  │
│ └──────┘ │                                │                  │
├──────────┴────────────────────────────────┴─────────────────┤
│ 滑坡总数:60 │ 高风险:29 │ 受影响:17,169人 │ 近30天:7           │
└─────────────────────────────────────────────────────────────┘
```

### 11.3 配色方案

| 用途 | 色值 | 说明 |
|------|------|------|
| 页面底色 | `#0a0e27` | 极深蓝黑，DataV 标准背景 |
| 面板/卡片背景 | `#0d1440` | 深蓝面板底 |
| 卡片背景 | `#111a45` | 比面板稍亮 |
| 主强调色 | `#00d4ff` | 霓虹青，标题/按钮/激活态 |
| 次强调色 | `#00ff88` | 霓虹绿，正向指标/成功 |
| 警告色 | `#ff6b6b` | 珊瑚红，高风险/警告 |
| 文字主色 | `#e0f0ff` | 浅蓝白，主文字 |
| 文字副色 | `#8899cc` | 灰蓝，辅助文字 |
| 边框 | `rgba(0,212,255,0.15)` | 半透明霓虹边框 |
| 卡片顶部装饰条 | `#00d4ff` | 默认青色装饰线 |

### 11.4 关键CSS实现要点

1. **布局**：不再使用 absolute 定位。`MainView` 使用 `display: flex; flex-direction: column;`，主体三栏用 `display: flex;`
2. **地图容器**：`flex: 1`（占60%），两侧面板 `width: 20%`
3. **卡片**：`background: #111a45; border: 1px solid rgba(0,212,255,0.15); border-radius: 4px;` — 顶部加 3px 色条
4. **数字展示**：大字号 `font-size: 28px; font-weight: bold; text-shadow: 0 0 10px rgba(0,212,255,0.5);`
5. **菜单按钮**：`background: rgba(0,212,255,0.1); color: #8899cc;` 激活时 `color: #00d4ff; border-bottom: 2px solid #00d4ff;`
6. **ECharts**：使用深色背景+霓虹色系，`backgroundColor: 'transparent'`，文字颜色 `#8899cc`

### 11.5 左侧面板三张卡片

| 卡片 | 内容 | 高度占比 |
|------|------|----------|
| 统计卡片 | 4个指标并排（总数/高风险/受影响/新增），大数字+发光 | ~25% |
| 监测卡片 | 模拟最新位移/雨量/水位数据，带趋势小箭头 | ~25% |
| 列表卡片 | 可搜索+滚动的滑坡点列表，点击行→地图定位+高亮 | ~50% |

### 11.6 与旧版关键差异

| 对比维度 | 旧版(xm-webgis-bs复制) | 新版(DataV大屏) |
|----------|----------------------|------------------|
| 布局方式 | absolute定位覆盖地图 | Flexbox三栏布局 |
| 面板 | 玻璃透明悬浮 | 不透明卡片式 |
| 地图尺寸 | 全屏100% | 居中60% |
| 背景 | 玻璃模糊效果 | 纯深色底 |
| 配色 | #1dc1f5青+灰蓝 | #00d4ff霓虹青+深蓝黑 |




### 5.8 路径规划路网动态提取策略

> 为避免全量路网拓扑构建带来的性能瓶颈，系统采用 **“按需提取、动态构建”** 的策略：以灾害点为中心，根据用户设定的半径动态提取局部路网，仅对该子集构建拓扑并执行路径规划。

#### 5.8.1 设计原则

| 原则 | 说明 |
|------|------|
| 按需提取 | 不以全省路网构建拓扑，仅提取灾害点周边局部路网 |
| 半径可控 | 用户可通过前端滑块调节搜索半径，系统动态响应 |
| 等级过滤 | 永久剔除低等级道路（如乡道、小路），仅保留主干道 |
| 性能兜底 | 通过最大半径限制，防止极端情况下数据量过大 |

#### 5.8.2 半径参数配置

| 参数 | 值 | 说明 |
|------|-----|------|
| 默认半径 | **25 km** | 覆盖县级救援力量1小时车程范围，兼顾性能与业务需求 |
| 可调范围 | **5 ~ 50 km** | 前端滑块控制，步长1km，用户可根据实际场景灵活调整 |
| 硬性上限 | **50 km** | 后端强制校验，超过则直接拒绝请求，防止服务器过载 |

#### 5.8.3 道路等级过滤规则

为控制拓扑构建的数据量，系统仅保留以下高等级道路类型（永久剔除 `tertiary` 以下等级）：

```sql
highway IN (
    'motorway', 'motorway_link',
    'trunk', 'trunk_link',
    'primary', 'primary_link',
    'secondary', 'secondary_link'
)


### 5.9 大规模空间数据快速加载策略

> 针对路网等大规模空间数据（全省路网 Shapefile 约 100~300 MB），若采用传统方式（前端直接请求全量 GeoJSON 或后端全表查询），将导致浏览器卡顿、接口超时。系统采用以下多层级优化策略，确保数据加载和查询的实时性。

#### 5.9.1 优化策略总览

| 层级 | 策略 | 核心思想 |
|------|------|----------|
| 前端加载 | WMS/WMTS 瓦片替代 WFS 矢量 | 只传图片，不传数据 |
| 后端查询 | 强制 BBox 空间范围过滤 | 只查当前屏幕可见区域 |
| 数据库索引 | GIST 空间索引 | 毫秒级空间过滤 |
| 数据存储 | 几何简化（ST_Simplify） | 减少顶点数，压缩存储 |
| 长任务处理 | 异步化（BackgroundTasks） | 避免 HTTP 超时 |

#### 5.9.2 前端加载：WMS/WMTS 瓦片服务

**问题**：前端通过 WFS 请求全量路网 GeoJSON（全省数据可达 100~300 MB），浏览器渲染卡顿，白屏时间 > 10 秒。

**解决方案**：将路网图层发布为 GeoServer WMS 服务，前端使用 `ol.source.TileWMS` 加载瓦片图片。

**前端代码示例（OpenLayers）**：

```javascript
// 使用 WMS 瓦片加载路网（仅传输当前屏幕图片）
const roadLayer = new ol.layer.Tile({
    source: new ol.source.TileWMS({
        url: 'http://localhost:8080/geoserver/landslide/wms',
        params: {
            'LAYERS': 'landslide:road_edges',
            'TILED': true,
            'FORMAT': 'image/png'
        },
        tileGrid: new ol.tilegrid.TileGrid({
            resolutions: [...],
            origin: [-180, 90]
        })
    })
});

##### 5.9.3.1 应用场景说明

“强制 BBox 空间范围过滤”的核心逻辑是：**所有与地图位置相关的后端查询，都必须接收前端当前视图的边界框（BBox），只查询屏幕可见区域的数据，禁止全表扫描。** 在本系统中，主要应用于以下三个场景：

---

**场景一：地图平移/缩放时的动态数据加载**

当用户缩放或拖动地图时，前端 OpenLayers 通过 `map.getView().calculateExtent()` 实时获取当前屏幕四个角的经纬度，并将其作为参数传递给后端接口。后端仅返回该范围内的数据。

**传统做法（不推荐）**：`SELECT * FROM landslide` → 返回全四川数千个点 → 数据量 500KB+ → 响应 > 3 秒

**BBox 做法（推荐）**：`SELECT * FROM landslide WHERE geom && ST_MakeEnvelope(...)` → 仅返回当前屏幕内约 50 个点 → 数据量 < 5KB → 响应 < 0.1 秒

---

**场景二：右侧面板的“框选查询”（空间查询）**

用户在地图上绘制矩形框后，前端将矩形四角坐标传给后端：

`POST /api/landslides/query` + `{ "bbox": [102.0, 27.0, 103.0, 28.0] }`

后端仅查询该矩形框内的灾害点和设施，实现精准的空间筛选。

---

**场景三：左侧面板的“当前区域统计”**

每次地图移动停止后，前端自动将 BBox 传给统计接口（如 `GET /api/statistics/overview`），左侧面板的数字（总数、高风险数、受影响人数等）仅统计当前屏幕范围内的灾害点，并实时更新。这既提升了性能，也保证了统计数据的上下文相关性。

---

**为什么要在性能优化章节强调这一点？**

| 对比项 | 不用 BBox（全表扫描） | 使用 BBox（空间索引扫描） |
| :--- | :--- | :--- |
| 返回数据量 | 全表数据（数千条） | 当前屏幕数据（数十条） |
| 数据库扫描方式 | 全表扫描 | GIST 索引扫描 |
| 典型响应时间 | 3 ~ 5 秒 | < 0.1 秒 |
| 网络传输开销 | 500 KB+ | < 10 KB |

> BBox 过滤是 GIS 系统性能优化的“第一道关口”，必须在所有空间查询接口中强制实施。
-- ==========================================
-- 滑坡数据库查询示例
-- 执行: psql -U postgres -d landslide_db -f queries.sql
-- ==========================================

-- 1. 各表数据量
SELECT 'landslide' AS 表名, count(*) AS 条数 FROM landslide
UNION ALL SELECT 'hospital', count(*) FROM hospital
UNION ALL SELECT 'fire_station', count(*) FROM fire_station
UNION ALL SELECT 'shelter', count(*) FROM shelter;

-- 2. 灾害等级分布
SELECT level, count(*) AS 数量 FROM landslide GROUP BY level ORDER BY count(*) DESC;

-- 3. 滑坡最多的城市 Top 10
SELECT city, count(*) AS 数量 FROM landslide WHERE city != '' GROUP BY city ORDER BY count(*) DESC LIMIT 10;

-- 4. 诱因统计
SELECT trigger, count(*) AS 数量 FROM landslide WHERE trigger != '' GROUP BY trigger ORDER BY count(*) DESC;

-- 5. 年度趋势
SELECT year, count(*) AS 数量 FROM landslide WHERE year > 0 GROUP BY year ORDER BY year;

-- 6. 月度分布
SELECT month, count(*) AS 数量 FROM landslide WHERE month > 0 GROUP BY month ORDER BY month;

-- 7. 死亡人数最多的滑坡 Top 5
SELECT id, city, county, level, deaths, injuries, missing FROM landslide ORDER BY deaths DESC LIMIT 5;

-- 8. 成都 50km 内的医院数量（空间查询）
SELECT count(*) AS 成都50km内医院 FROM hospital
WHERE ST_DWithin(geometry::geography, ST_SetSRID(ST_MakePoint(104.0657, 30.6598), 4326)::geography, 50000);

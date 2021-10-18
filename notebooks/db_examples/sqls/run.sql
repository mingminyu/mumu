--[sql1]
SELECT * FROM test.ddd_211015 WHERE 1=1 AND owner_id='${owner_id}' LIMIT 10
;
--[end]


--[sql2]
SELECT * FROM test.ddd_211015 WHERE 1=1 AND owner_id='${owner_id}' LIMIT 5
;
--[end]

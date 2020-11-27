SELECT r.id, r.name, COUNT(s.room_id) as num_of_students
 FROM student AS s
 INNER JOIN room AS r ON s.room_id=r.id
 GROUP BY r.id;

SELECT r.id, r.name
 FROM student AS s
 INNER JOIN room AS r ON s.room_id=r.id
 GROUP BY r.id
 ORDER BY AVG(s.birthday)
 LIMIT 5;

SELECT r.id, r.name
 FROM student AS s
 INNER JOIN room AS r ON s.room_id=r.id
 GROUP BY r.id
 ORDER BY STD(s.birthday) ASC
 LIMIT 5;

SELECT r.id, r.name
 FROM student AS s
 INNER JOIN room as r
 ON s.room_id=r.id
 GROUP BY id
 HAVING COUNT(DISTINCT sex)=2;
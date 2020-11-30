#список комнат и количество студентов в каждой из них#
SELECT r.id, r.name, COUNT(s.room_id) as num_of_students
 FROM student AS s
 INNER JOIN room AS r ON s.room_id=r.id
 GROUP BY r.id;

#top 5 комнат, где самые маленький средний возраст студентов#
SELECT r.id, r.name
 FROM student AS s
 INNER JOIN room AS r ON s.room_id=r.id
 GROUP BY r.id
 ORDER BY AVG(s.birthday)
 LIMIT 5;

#top 5 комнат с самой большой разницей в возрасте студентов#
SELECT r.id, r.name
 FROM student AS s
 INNER JOIN room AS r ON s.room_id=r.id
 GROUP BY r.id
 ORDER BY STD(s.birthday) ASC
 LIMIT 5;

#список комнат где живут разнополые студенты#
SELECT r.id, r.name
 FROM student AS s
 INNER JOIN room as r
 ON s.room_id=r.id
 GROUP BY id
 HAVING COUNT(DISTINCT sex)=2;
----- FIRST PAGE -----

-- donations
SELECT sum(donation_amount) FROM donations WHERE donor_type='Individual'

-- funding
SELECT sum(donation_amount) FROM donations WHERE donor_type='Organization'

--program attendance
SELECT count(*) FROM events WHERE program_ind = 1

--event attendance
SELECT count(*) from events where program_ind = 0

--donor count
SELECT member_count + non_member_count
from
(SELECT count(distinct member_id) - 1 as member_count
, sum(case when member_id = 999999999 then 1 else 0 end) as non_member_count
from donations where donor_type = 'Individual') a

--funder count
SELECT sum(case when member_id = 999999999 and donor_type = 'Organization' then 1 else 0 end) as funder_count
from donations


-------- THIRD PAGE --------

--top 5 visited events
SELECT * FROM (
SELECT event_name,event_dt, attendee_count FROM (
SELECT event_id, event_name,event_dt, COUNT(*) as attendee_count FROM events
WHERE program_ind = 0 GROUP BY 1,2,3
) a
ORDER BY attendee_count DESC) b limit 5

-------- FOURTH PAGE ---------

---top

--attendance by program
SELECT event_name, COUNT(*) as attendee_count FROM events
WHERE program_ind = 1 GROUP BY 1 ORDER BY attendee_count desc;

--funding by program
SELECT program_funded, SUM(donation_amount) as donations FROM donations WHERE program_ind=1
GROUP BY 1 ORDER BY donations desc;

----bottom

--attendance by month and program
SELECT event_name,SUBSTRING(event_dt::varchar,1,7) as month, COUNT(*) as attendance FROM events
WHERE program_ind=1
GROUP BY 1,2 ORDER BY 1 asc,2 asc

--funding by month by program
SELECT program_funded,SUBSTRING(donation_date::varchar,1,7) as month, SUM(donation_amount) FROM donations
WHERE program_ind=1
GROUP BY 1,2 ORDER BY 1 asc,2 asc;


------- FITFTH PAGE BOTTOM --------

-- donations over time
SELECT SUBSTRING(donation_date::varchar,1,7) as month, SUM(donation_amount) FROM donations
WHERE program_ind=1
GROUP BY 1 ORDER BY 1 asc


--------- SIXTH PAGE --------

-- membership over time
SELECT SUBSTRING(join_date,1,7) as month, COUNT(*) FROM members
GROUP BY 1 ORDER BY 1

--age of members
SELECT (CURRENT_DATE - birth_date)/365::int as age, COUNT(*) FROM members
GROUP BY 1 ORDER BY 1 ASC

-- donations
SELECT sum(donation_amount) FROM donations WHERE donor_type='Individual'

-- funding
SELECT sum(donation_amount) FROM donations WHERE donor_type='Organization'

--top 5 visited events
SELECT event_name,event_dt, attendee_count FROM (
SELECT event_id, event_name,event_dt, COUNT(*) as attendee_count FROM events
WHERE program_ind = 0 GROUP BY 1,2,3
) a
ORDER BY attendee_count DESC LIMIT 5

--attendance by program
SELECT event_name, COUNT(*) as attendee_count FROM events
WHERE program_ind = 1 GROUP BY 1 ORDER BY attendee_count desc

--funding by program
SELECT program_funded, SUM(donation_amount) as donations FROM donations WHERE program_ind=1
GROUP BY 1 ORDER BY donations desc

--attendance by month and program
SELECT event_name,SUBSTRING(event_dt,1,7) as month, COUNT(*) as attendance FROM events
WHERE program_ind=1
GROUP BY 1,2 ORDER BY 1 asc,2 asc

--funding by month by program
SELECT program_funded,SUBSTRING(donation_date,1,7) as month, SUM(donation_amount) FROM donations
WHERE program_ind=1
GROUP BY 1,2 ORDER BY 1 asc,2 asc

-- donations over time
SELECT SUBSTRING(donation_date,1,7) as month, SUM(donation_amount) FROM donations
WHERE program_ind=1
GROUP BY 1 ORDER BY 1 asc

-- membership over time
SELECT SUBSTRING(join_dt,1,7) as month, COUNT(*) FROM members
GROUP BY 1 ORDER BY 1

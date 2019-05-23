SELECT match.match_id, start_time, end_time, COUNT(DISTINCT killer_name) as player_count, COUNT(killer_name) AS kill_suicide_count
FROM match INNER JOIN match_frag ON match.match_id = match_frag.match_id
GROUP BY match.match_id
ORDER BY start_time ASC;
SELECT match_id, killer_name AS player_name, COUNT(killer_name) AS kill_count
FROM match_frag
GROUP BY match_id, player_name
ORDER BY match_id ASC, kill_count DESC;
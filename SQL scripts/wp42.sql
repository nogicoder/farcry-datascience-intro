SELECT match_id, killer_name AS player_name, COUNT(victim_name) AS death_count
FROM match_frag
GROUP BY match_id, player_name
ORDER BY match_id ASC, death_count DESC;
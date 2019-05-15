SELECT killer_name, COUNT(killer_name) AS kill_count
FROM match_frag
GROUP BY killer_name
ORDER BY kill_count DESC, killer_name ASC;
SELECT COUNT(killer_name) AS kill_count
FROM match_frag
WHERE victim_name IS NOT NULL;
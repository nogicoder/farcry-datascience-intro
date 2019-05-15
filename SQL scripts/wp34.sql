SELECT COUNT(killer_name) AS suicide_count
FROM match_frag
WHERE victim_name IS NULL;
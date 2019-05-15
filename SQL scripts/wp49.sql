SELECT match_id, killer_name, COUNT(DISTINCT weapon_code) as weapon_count
FROM match_frags
GROUP BY match_id, killer_name
ORDER BY weapon_count DESC;
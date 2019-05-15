SELECT match_id, victim_name as player_name, killer_name as worst_enemy_name, kill_count
FROM
    (SELECT match_id, victim_name, killer_name, COUNT(killer_name) as kill_count, MIN(frag_time) as frag_time, ROW_NUMBER()
OVER(
PARTITION BY match_id, victim_name
ORDER BY COUNT(killer_name) DESC, MIN(frag_time) ASC)
    FROM match_frags
    WHERE victim_name IS NOT NULL
    GROUP BY match_id, victim_name, killer_name
    ORDER BY match_id, victim_name, kill_count DESC) AS T
WHERE row_number = 1;
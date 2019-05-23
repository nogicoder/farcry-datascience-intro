SELECT match_id, killer_name as player_name, victim_name as favorite_victim_name, kill_count
FROM
    (SELECT match_id, killer_name, victim_name, COUNT(victim_name) as kill_count, MIN(frag_time) as frag_time, ROW_NUMBER()
OVER(
PARTITION BY match_id, killer_name
ORDER BY COUNT(victim_name) DESC, MIN(frag_time) ASC)
    FROM match_frag
    WHERE victim_name IS NOT NULL
    GROUP BY match_id, killer_name, victim_name
    ORDER BY match_id, killer_name, kill_count DESC) AS T
WHERE row_number = 1;

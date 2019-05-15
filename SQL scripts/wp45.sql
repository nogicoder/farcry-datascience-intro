CREATE VIEW match_statistics
AS
    SELECT match_id, player_name, SUM(kill_count) AS kill_count, SUM(suicide_count) AS suicide_count, SUM(death_count) AS death_count, ROUND(SUM(kill_count)*100/CAST((SUM(kill_count) + SUM(suicide_count) + SUM(death_count)) AS FLOAT), 2) AS efficiency
    FROM
        (                    SELECT match_id, player_name, SUM(kill_count) as kill_count, SUM(suicide_count) as suicide_count, 0 AS death_count
            FROM
                (                                    SELECT T2.match_id, T2.killer_name as player_name, COUNT(T2.killer_name) as kill_count, 0 AS suicide_count
                    FROM match_frag T2
                    WHERE victim_name IS NOT NULL
                    GROUP BY T2.match_id, T2.killer_name
                UNION
                    SELECT T2.match_id, T2.killer_name as player_name, 0 AS kill_count, COUNT(T2.killer_name) as suicide_count
                    FROM match_frag T2
                    WHERE victim_name IS NULL
                    GROUP BY T2.match_id, T2.killer_name) AS T
            GROUP BY match_id, player_name
        UNION
            SELECT match_id, victim_name as player_name, 0 AS kill_count, 0 AS suicide_count, COUNT(victim_name) as death_count
            FROM match_frag
            WHERE victim_name IS NOT NULL
            GROUP BY match_id, victim_name) AS T
    GROUP BY match_id, player_name
    ORDER BY match_id ASC, efficiency DESC;
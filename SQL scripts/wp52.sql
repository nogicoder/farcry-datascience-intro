-- User-defined function
CREATE OR REPLACE FUNCTION get_killer_class (weapon_code TEXT) 
RETURNS TEXT AS $$
DECLARE class TEXT;
BEGIN
    CASE WHEN weapon_code IN ('Machete', 'Falcon', 'MP5') THEN class='Hitman';
    WHEN weapon_code IN ('SniperRifle') THEN class='Sniper';
    WHEN weapon_code IN ('AG36', 'OICW', 'P90', 'M4', 'Shotgun', 'M249') THEN class='Commando';
    WHEN weapon_code IN ('Rocket', 'VehicleRocket', 'HandGrenade', 'StickExplosive', 'Boat', 'Vehicle', 'VehicleMountedRocketMG', 'VehicleMountedAutoMG', 'MG', 'VehicleMountedMG', 'OICWGrenade', 'AG36Grenade') THEN class='Psychopath';
    ELSE class='Other';
    END CASE;
    RETURN class;
END; $$
LANGUAGE PLPGSQL;

-- Get the class of each player
SELECT match_id, killer_name as player_name, weapon_code, kill_count, get_killer_class(weapon_code) as killer_class
FROM
    (SELECT match_id, killer_name, weapon_code, COUNT(weapon_code) as kill_count, ROW_NUMBER()
OVER
(PARTITION BY match_id, killer_name
ORDER BY COUNT(weapon_code) DESC)
    FROM match_frag
    WHERE victim_name IS NOT NULL
    GROUP BY match_id, killer_name, weapon_code
    ORDER BY match_id, killer_name, kill_count DESC) AS T
WHERE row_number = 1;




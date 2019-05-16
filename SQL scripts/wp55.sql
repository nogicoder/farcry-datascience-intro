CREATE OR REPLACE FUNCTION test
(p_min_kill_count INT DEFAULT 3, p_max_time_between_kills INT DEFAULT 10)
RETURNS TABLE
(
    match_id UUID, 
    killer_name TEXT, 
    kill_count INT)
AS $$
DECLARE 
    max_count INT;
    current_count INT;
    deltatime INT;
    i_fragtime TIMESTAMPTZ(3);
    c_line1 RECORD;
    c_line2 RECORD;
BEGIN
    FOR c_line1 IN
    (SELECT DISTINCT T.match_id, T.killer_name
    FROM match_frags T
    ORDER BY T.match_id, T.killer_name)
    LOOP
        match_id := c_line1.match_id;
        killer_name := c_line1.killer_name;
        i_fragtime := to_timestamp(0);
        max_count := 0;
        current_count := 0;
        FOR c_line2 IN (SELECT T.match_id, T.frag_time, T.killer_name, T.victim_name
                        FROM match_frags T
                        WHERE (T.killer_name = c_line1.killer_name) OR (T.victim_name = c_line1.killer_name))
            LOOP
                deltatime = EXTRACT(EPOCH FROM(c_line2.frag_time - i_fragtime));
                IF (i_fragtime = to_timestamp(0) OR
                    c_line2.killer_name = killer_name AND c_line2.victim_name IS NOT NULL AND deltatime <= p_max_time_between_kills)
                THEN
                    current_count = current_count + 1;
                    i_fragtime = c_line2.frag_time;
                ELSIF ((c_line2.killer_name = killer_name AND c_line2.victim_name IS NULL) OR
                    c_line2.victim_name = killer_name OR
                    (c_line2.killer_name = killer_name AND c_line2.victim_name IS NOT NULL AND deltatime > p_max_time_between_kills))
                THEN 
                    IF (current_count >= p_min_kill_count AND current_count > max_count)
                    THEN 
                        max_count := current_count;
                    END IF;
                    current_count := 0;
                    i_fragtime := to_timestamp(0);

                END IF;
            END LOOP;

        kill_count := max_count;
        RETURN NEXT;
    END LOOP;
END; $$ 
LANGUAGE PLPGSQL;
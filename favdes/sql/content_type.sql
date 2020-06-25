-- CHAR_TO_INT
CREATE FUNCTION CHAR_TO_INT(character varying) RETURNS integer AS
$$
SELECT CASE
           WHEN length(btrim(regexp_replace($1, '[^0-9]', '', 'g'))) > 0
               THEN btrim(regexp_replace($1, '[^0-9]', '', 'g'))::integer
           ELSE 0
           END AS intval
$$
    LANGUAGE sql;

-- FETCH_CONTENT_TYPE
CREATE OR REPLACE FUNCTION FETCH_CONTENT_TYPE(name varchar) returns integer as
$$
SELECT id
FROM django_content_type
WHERE concat(app_label, '_', model) = name
$$ LANGUAGE sql;

-- GFK_QUERY
CREATE OR REPLACE FUNCTION GFK_QUERY(content_type int, object_id varchar) RETURNS SETOF json AS
$$
DECLARE
BEGIN
    CASE
        WHEN content_type = (SELECT FETCH_CONTENT_TYPE('destination_destination'))
            THEN RETURN QUERY SELECT FETCH_DESTINATION(CHAR_TO_INT(object_id)) AS data;
        WHEN content_type = (SELECT FETCH_CONTENT_TYPE('auth_user'))
            THEN RETURN QUERY SELECT FETCH_USER(CHAR_TO_INT(object_id)) AS data;
        WHEN content_type = (SELECT FETCH_CONTENT_TYPE('activity_post'))
            THEN RETURN QUERY SELECT FETCH_POST(CHAR_TO_INT(object_id)) AS data;
        WHEN content_type = (SELECT FETCH_CONTENT_TYPE('activity_activity'))
            THEN RETURN QUERY SELECT FETCH_ACTION(CHAR_TO_INT(object_id)) AS data; ELSE RETURN NEXT null;
        END case;
END;
$$ LANGUAGE PLPGSQL;

-- FETCH_ACTION
CREATE OR REPLACE FUNCTION FETCH_ACTION(i int, user_id int = null) RETURNS json AS
$$
SELECT row_to_json(t)
FROM (
         SELECT *,
                (SELECT GFK_QUERY(activity_activity.actor_content_type_id, activity_activity.actor_object_id)) AS actor,
                (SELECT GFK_QUERY(activity_activity.target_content_type_id,
                                  activity_activity.target_object_id))                                         AS target,
                (SELECT GFK_QUERY(activity_activity.action_object_content_type_id,
                                  activity_activity.action_object_object_id))                                  AS action_object,
                (
                    SELECT row_to_json(t)
                    FROM (
                             SELECT *
                             FROM activity_activity_voters
                             WHERE user_id = user_id
                               AND activity_id = activity_activity.id
                         ) t
                )                                                                                              AS is_voted,
                (
                    SELECT count(*)
                    FROM activity_activity_voters
                    WHERE activity_id = activity_activity.id
                )                                                                                              AS vote_count,
                (
                    SELECT count(*)
                    FROM activity_comment
                    WHERE activity_id = activity_activity.id
                )                                                                                              AS comment_count
         FROM activity_activity
         WHERE id = i
     ) t;

$$ LANGUAGE SQL;

-- FETCH_USER
CREATE OR REPLACE FUNCTION FETCH_USER(i int) RETURNS json AS
$$
SELECT row_to_json(t)
FROM (
         SELECT auth_user.username,
                auth_user.first_name,
                auth_user.last_name,
                (
                    SELECT row_to_json(t)
                    FROM (
                             SELECT *,
                                    (
                                        SELECT row_to_json(u)
                                        FROM (
                                                 SELECT *,
                                                        (SELECT MAKE_THUMB(md.path)) as sizes
                                                 FROM media_media md
                                                 WHERE md.id = dp.media_id
                                             ) u
                                    ) AS media
                             FROM authentication_profile dp
                             WHERE dp.user_id = auth_user.id
                         ) t
                ) AS profile

         FROM auth_user
         WHERE auth_user.id = i
     ) t
$$ LANGUAGE sql;

-- FETCH_DESTINATION
CREATE OR REPLACE FUNCTION FETCH_DESTINATION(i int) RETURNS json AS
$$
SELECT row_to_json(t)
FROM (
         SELECT destination_destination.*,
                (
                    SELECT row_to_json(u)
                    FROM (
                             SELECT destination_address.*
                             FROM destination_address
                             WHERE destination_address.id = destination_destination.address_id) u) as address,
                (
                    select array_to_json(array_agg(row_to_json(t)))
                    FROM (
                             SELECT *
                             FROM media_media
                                      JOIN destination_destination_medias ddm on media_media.id = ddm.media_id
                             LIMIT 5
                         ) t
                )                                                                                  AS medias
         FROM destination_destination
         WHERE destination_destination.id = i
     ) t;

$$ language sql;

--  FETCH_POST
CREATE OR REPLACE FUNCTION FETCH_POST(i int) RETURNS json AS
$$
SELECT row_to_json(t)
FROM (
         SELECT activity_post.*,
                (
                    SELECT array_to_json(array_agg(row_to_json(t)))
                    FROM (
                             SELECT *,
                                    (SELECT MAKE_THUMB(media_media.path)) as sizes
                             FROM media_media
                                      JOIN activity_post_medias ON media_media.id = activity_post_medias.media_id
                             WHERE activity_post_medias.post_id = activity_post.id
                         ) t
                ) AS medias
         FROM activity_post
         WHERE activity_post.id = i
     ) t;

$$ LANGUAGE sql;

-- FETCH_ACTIVITIES
CREATE OR REPLACE FUNCTION FETCH_ACTIVITIES(page_size int =null,
                                            os int = null,
                                            search varchar = null,
                                            target_content int = null,
                                            target_id varchar = null,
                                            user_id int = null) returns json as
$$
SELECT array_to_json(array_agg(row_to_json(t)))
FROM (
         SELECT *,
                (SELECT GFK_QUERY(aa.actor_content_type_id, aa.actor_object_id)) AS actor,
                (SELECT GFK_QUERY(aa.target_content_type_id,
                                  aa.target_object_id))                          AS target,
                (SELECT GFK_QUERY(aa.action_object_content_type_id,
                                  aa.action_object_object_id))                   AS action_object,
                (
                    SELECT row_to_json(t)
                    FROM (
                             SELECT *
                             FROM activity_activity_voters
                             WHERE user_id = user_id
                               AND activity_id = aa.id
                         ) t
                    LIMIT 1
                )                                                                AS is_voted,
                (
                    SELECT count(*)
                    FROM activity_activity_voters
                    WHERE activity_id = aa.id
                )                                                                AS vote_count,
                (
                    SELECT count(*)
                    FROM activity_comment
                    WHERE activity_id = aa.id
                ),
                (
                    SELECT FETCH_ADDRESS(aa.address_id) as address
                )

         FROM activity_activity aa
         WHERE (
                 (aa.target_content_type_id = target_content
                     AND aa.target_object_id = target_id) OR (target_id IS NULL AND target_content IS NULL)
             )
            OR (
                 (aa.actor_content_type_id = target_content
                     AND aa.actor_object_id = target_id) OR (target_id IS NULL AND target_content IS NULL)
             )
            OR (
                 (aa.action_object_content_type_id = target_content
                     AND aa.action_object_object_id = target_id) OR
                 (target_id IS NULL AND target_content IS NULL)
             )
         ORDER BY aa.id DESC
         LIMIT page_size
         OFFSET
         os
     ) t

$$ LANGUAGE sql;

-- FETCH_ADDRESS
CREATE OR REPLACE FUNCTION FETCH_ADDRESS(i int) RETURNS json AS
$$
SELECT row_to_json(t)
FROM (
         SELECT *
         FROM destination_address da
         WHERE da.id = i
     ) t
$$
    LANGUAGE sql;

-- COUNT_ACTIVITIES
CREATE OR REPLACE FUNCTION COUNT_ACTIVITIES(search varchar = null,
                                            target_content int = null,
                                            target_id varchar = null) RETURNS BIGINT AS
$$
SELECT COUNT(*)
FROM (
         SELECT id
         FROM activity_activity aa
         WHERE (
                 (aa.target_content_type_id = target_content
                     AND aa.target_object_id = target_id) OR (target_id IS NULL AND target_content IS NULL)
             )
            OR (
                 (aa.actor_content_type_id = target_content
                     AND aa.actor_object_id = target_id) OR (target_id IS NULL AND target_content IS NULL)
             )
            OR (
                 (aa.action_object_content_type_id = target_content
                     AND aa.action_object_object_id = target_id) OR
                 (target_id IS NULL AND target_content IS NULL)
             )
         ORDER BY aa.updated DESC
     ) t
$$ LANGUAGE sql;

-- MAKE_THUMB
CREATE OR REPLACE FUNCTION MAKE_THUMB(path varchar) RETURNS json AS
$$
SELECT row_to_json(t)
FROM (
         SELECT (SELECT concat('https://ware.sgp1.digitaloceanspaces.com/public/cache/270x270/',
                               path) AS thumb_270_270),
                (SELECT concat('https://ware.sgp1.digitaloceanspaces.com/public/cache/540x540/',
                               path) AS thumb_540_540),
                (SELECT concat('https://ware.sgp1.digitaloceanspaces.com/public/cache/540/', path) AS resize)
     ) t
$$
    LANGUAGE sql;

SELECT id,
       type_code,
       type_name,
       aliases,
       source_system,
       status
FROM dictionary_type
WHERE (
    LOWER(type_code) = LOWER(:dictionary_type)
    OR LOWER(type_name) = LOWER(:dictionary_type)
    OR EXISTS (
        SELECT 1
        FROM UNNEST(aliases) AS alias(value)
        WHERE LOWER(alias.value) = LOWER(:dictionary_type)
    )
)
AND (CAST(:source_system AS TEXT) IS NULL OR source_system = :source_system)
AND (:include_inactive OR status = 'ACTIVE')
ORDER BY source_system, type_code

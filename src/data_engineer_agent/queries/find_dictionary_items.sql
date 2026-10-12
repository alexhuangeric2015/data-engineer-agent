SELECT item.id,
       item.dictionary_type_id,
       type.type_code,
       type.type_name,
       type.source_system,
       item.item_code,
       item.item_name,
       item.aliases,
       item.description,
       item.status,
       item.sort_order
FROM dictionary_item AS item
JOIN dictionary_type AS type ON type.id = item.dictionary_type_id
WHERE (
    CAST(:dictionary_type_id AS BIGINT) IS NULL
    OR item.dictionary_type_id = :dictionary_type_id
)
AND (
    item.item_code = ANY(CAST(:item_codes AS TEXT[]))
    OR LOWER(item.item_name) = ANY(CAST(:normalized_names AS TEXT[]))
    OR EXISTS (
        SELECT 1
        FROM UNNEST(item.aliases) AS alias(value)
        WHERE LOWER(alias.value) = ANY(CAST(:normalized_names AS TEXT[]))
    )
)
AND (
    :include_inactive
    OR (
        item.status = 'ACTIVE'
        AND type.status = 'ACTIVE'
        AND (item.effective_from IS NULL OR item.effective_from <= CURRENT_TIMESTAMP)
        AND (item.effective_to IS NULL OR item.effective_to > CURRENT_TIMESTAMP)
    )
)
ORDER BY type.type_code, item.sort_order, item.id

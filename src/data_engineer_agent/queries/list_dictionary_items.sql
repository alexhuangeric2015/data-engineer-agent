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
WHERE item.dictionary_type_id = :dictionary_type_id
AND (
    CAST(:after_sort_order AS INTEGER) IS NULL
    OR (item.sort_order, item.id) > (
        CAST(:after_sort_order AS INTEGER),
        CAST(:after_id AS BIGINT)
    )
)
AND (
    :include_inactive
    OR (
        item.status = 'ACTIVE'
        AND (item.effective_from IS NULL OR item.effective_from <= CURRENT_TIMESTAMP)
        AND (item.effective_to IS NULL OR item.effective_to > CURRENT_TIMESTAMP)
    )
)
ORDER BY item.sort_order, item.id
LIMIT :limit

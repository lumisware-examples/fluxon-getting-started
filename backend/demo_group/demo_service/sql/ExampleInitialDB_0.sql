SELECT EXTRA AS extra
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = :schema_name
  AND TABLE_NAME = 'demo_products'
  AND COLUMN_NAME = 'id';

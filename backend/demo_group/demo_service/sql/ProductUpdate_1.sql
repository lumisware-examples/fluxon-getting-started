UPDATE {schema_name}.demo_products
SET category = :category, name = :name, price = :price
WHERE id = :id

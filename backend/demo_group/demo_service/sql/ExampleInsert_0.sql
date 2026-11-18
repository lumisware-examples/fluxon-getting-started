-- id를 생략하면 AUTO_INCREMENT가 값을 발급합니다.
INSERT INTO {schema_name}.demo_products (name, category, price)
VALUES (:name, :category, :price);

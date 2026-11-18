-- 오류/rollback 실습용입니다. 기본 코드에서는 실행하지 않습니다.
-- AUTO_INCREMENT에서는 id 생략이 정상이므로, 의도적으로 없는 apprice 컬럼을 사용합니다.
INSERT INTO {schema_name}.demo_products (name, category, apprice)
VALUES (:name, :category, :price);

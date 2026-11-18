-- ExampleMysqlSetup이 워커 기본 저장소의 실습 테이블만 준비합니다.
-- 이미 테이블이 있으면 기존 구조와 데이터를 유지합니다. 기존 구조를 변경하는 마이그레이션은 아닙니다.
CREATE TABLE IF NOT EXISTS {schema_name}.getting_started_example_items
(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    price INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

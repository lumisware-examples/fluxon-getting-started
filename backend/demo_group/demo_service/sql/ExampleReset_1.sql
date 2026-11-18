CREATE TABLE {schema_name}.demo_products
(
    id       INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(80) NOT NULL,
    category VARCHAR(40) NOT NULL,
    price    INT         NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

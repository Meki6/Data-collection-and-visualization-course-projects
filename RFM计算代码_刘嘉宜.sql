CREATE DATABASE tp;
USE tp;
#先将原始数据导入mysql，创建表格order
CREATE TABLE `order` (
order_ID VARCHAR(100) NOT NULL,
user_ID VARCHAR(100) NOT NULL,
sku_ID VARCHAR(100) NOT NULL,
order_date DATE,
order_time DATETIME,
quantity INT NOT NULL,
type INT NOT NULL,
promise INT,
original_unit_price DECIMAL(9,3) NOT NULL,
final_unit_price DECIMAL(9,3) NOT NULL,
direct_discount_per_unit DECIMAL(9,3) NOT NULL,
quantity_discount_per_unit DECIMAL(9,3) NOT NULL,
bundle_discount_per_unit DECIMAL(9,3) NOT NULL,
coupon_discount_per_unit DECIMAL(9,3) NOT NULL,
gift_item INT NOT NULL,
dc_ori INT NOT NULL,
dc_des INT NOT NULL)
ENGINE = innodb;

#想要导入表格，必须从local进去，或者set gloabl_infile=1
-- mysql --local-infile -u root -p
LOAD DATA LOCAL INFILE "C:/Users/maggi/Desktop/JDData/JD_order_data1.csv"
INTO TABLE `order`
FIELDS TERMINATED BY ","
LINES TERMINATED BY"\n";

#创建视图，计算用户最近一次消费的时间与月底的间隔
CREATE VIEW rfmtry AS 
SELECT user_ID, DATEDIFF('2018-03-31',MAX(order_date)) AS B FROM `order` 
GROUP BY user_ID;
#将用户和最近一次消费时间间隔导出
SELECT user_ID, B FROM rfmtry INTO OUTFILE "C:/Users/maggi/Desktop/最近一次消费时间间隔.csv" fields terminated by ',' lines terminated by '\n';

#想直接用mysql自带的百分位分割但是出不来
-- SELECT user_ID, 
-- ceiling(precent_rank() over (B)/0.2) AS R 
-- FROM rfmtry ORDER BY R DESC;

#对用户最近一次消费的时间与月底的间隔分档——R
SELECT user_ID, (CASE WHEN B BETWEEN 0 AND 9 THEN 2 
WHEN B BETWEEN 10 AND 19 THEN 1 
WHEN B BETWEEN 20 AND 31 THEN 0 
ELSE null END) AS R 
FROM rfmtry 
ORDER BY R DESC;
#导出R
SELECT user_ID, (CASE WHEN B BETWEEN 0 AND 9 THEN 2 WHEN B BETWEEN 10 AND 19 THEN 1 WHEN B BETWEEN 20 AND 31 THEN 0 ELSE null END) AS R FROM rfmtry ORDER BY R DESC INTO outfile  "C:/Users/maggi/Desktop/R.csv" fields terminated by ',' lines terminated by '\n';

#创建用于计算F的表orderf
CREATE TABLE `orderf` (
order_ID VARCHAR(100) NOT NULL,
user_ID VARCHAR(100) NOT NULL,
sku_ID VARCHAR(100) NOT NULL,
order_date DATE,
order_time DATETIME,
quantity INT NOT NULL,
type INT NOT NULL,
promise INT,
original_unit_price DECIMAL(9,3) NOT NULL,
final_unit_price DECIMAL(9,3) NOT NULL,
direct_discount_per_unit DECIMAL(9,3) NOT NULL,
quantity_discount_per_unit DECIMAL(9,3) NOT NULL,
bundle_discount_per_unit DECIMAL(9,3) NOT NULL,
coupon_discount_per_unit DECIMAL(9,3) NOT NULL,
gift_item INT NOT NULL,
dc_ori INT NOT NULL,
dc_des INT NOT NULL)
ENGINE = innodb;
#导入数据
INSERT INTO `orderf`  SELECT * FROM `order`;

#加入id作为主键
ALTER TABLE `orderf` ADD COLUMN id BIGINT(7) NOT NULL auto_increment PRIMARY KEY first;
#删除order_ID重复的记录，重复的只保留第一条（这样方便计算每个用户的订单数）
DELETE FROM `orderf` WHERE order_ID in (select * from (SELECT order_ID FROM `orderf` GROUP BY order_ID having count(user_ID) > 1) tmp) and id not in (select * from (select min(id) from `orderf` group by order_ID having count(order_ID) > 1) tmp);


#计算每个用户的订单数（orderf表中已删除重复order_ID的记录）
CREATE VIEW rfmtry_ff AS
SELECT user_ID, count( order_ID ) AS times FROM `orderf`
GROUP BY user_ID ORDER BY count( order_ID ) DESC;
#将用户和订单数导出
SELECT user_ID,times FROM rfmtry_ff INTO outfile  "C:/Users/maggi/Desktop/订单数.csv" fields terminated by ',' lines terminated by '\n';

#对用户消费的频率（订单数）分档打分——F
SELECT user_ID ,(CASE WHEN times BETWEEN 1 AND 3 THEN 0 
WHEN times BETWEEN 4 AND 9 THEN 1 
WHEN times BETWEEN 10 AND 15 THEN 2 
WHEN times BETWEEN 16 AND 50 THEN 3 
WHEN times BETWEEN 51 AND 100 THEN 4 
WHEN times >=101 THEN 5 
ELSE NULL END) AS F 
FROM rfmtry_ff ORDER BY F DESC;
#导出F
SELECT user_ID ,(CASE WHEN times =1 THEN 0 WHEN times BETWEEN 2 AND 5 THEN 1 WHEN times BETWEEN 6 AND 10 THEN 2 WHEN times BETWEEN 11 AND 50 THEN 3 WHEN times BETWEEN 51 AND 100 THEN 4 WHEN times BETWEEN 101 AND 605 THEN 5 ELSE NULL END) AS F FROM rfmtry_f ORDER BY F DESC INTO outfile  "C:/Users/maggi/Desktop/F.csv" fields terminated by ',' lines terminated by '\n';


#计算消费金额，可以用sum直接计算选出每个用户的消费总金额！
CREATE VIEW rfmtry_mmm AS 
SELECT user_ID, sum(final_unit_price) AS M FROM `order` 
GROUP BY user_ID;
#将用户和对应消费总金额导出
SELECT user_ID,M FROM rfmtry_mmm INTO outfile  "C:/Users/maggi/Desktop/消费金额.csv" fields terminated by ',' lines terminated by '\n';

#对用户的消费金额分档打分——M
SELECT user_ID ,(CASE WHEN M BETWEEN -60 AND 0 THEN 0 
WHEN M BETWEEN 0.00001 AND 50 THEN 1 
WHEN M BETWEEN 50.00001 AND 100 THEN 2 
WHEN M BETWEEN 100.00001 AND 500 THEN 3 
WHEN M BETWEEN 500.000001 AND 1000 THEN 4 
WHEN M>1000 THEN 5 
ELSE NULL END) AS MMM 
FROM rfmtry_mmm ORDER BY MMM DESC;
#导出M
SELECT user_ID ,(CASE WHEN M BETWEEN -60 AND 0 THEN 0 WHEN M BETWEEN 0.00001 AND 50 THEN 1 WHEN M BETWEEN 50.00001 AND 100 THEN 2 WHEN M BETWEEN 100.00001 AND 500 THEN 3 WHEN M BETWEEN 500.000001 AND 1000 THEN 4 WHEN M>1000 THEN 5 ELSE NULL END) AS MMM FROM rfmtry_mmm ORDER BY MMM DESC INTO outfile  "C:/Users/maggi/Desktop/M.csv" fields terminated by ',' lines terminated by '\n';



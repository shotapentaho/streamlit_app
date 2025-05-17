--contract_activity_type
truncate table TEST.PUBLIC.contract_activity_type;
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (1,'Electrical');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (2,'Painting');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (3,'Powerwashing');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (4,'Plumbing');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (5,'Gutter Cleaning');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (6,'Roofing');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (7,'Handyman');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (8,'Landscaping');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (9,'Irrigation');
INSERT INTO TEST.PUBLIC.contract_activity_type (activity_id,activity_name) values (10,'Carpentry');

--subscription
truncate table TEST.PUBLIC.subscription;
INSERT INTO TEST.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (0, 1, 1*1, current_date);
INSERT INTO TEST.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (1, 3, 4.99*3, current_date);
INSERT INTO TEST.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (2, 6, 4.99*6, current_date);
INSERT INTO TEST.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (3, 12, 4.99*12, current_date);


commit;
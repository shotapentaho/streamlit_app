--contract_activity_type
truncate table DEV.PUBLIC.contract_activity_type;
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (1,'Electrical');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (2,'Painting');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (3,'Powerwashing');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (4,'Plumbing');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (5,'Gutter Cleaning');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (6,'Roofing');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (7,'Handyman');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (8,'Landscaping');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (9,'Irrigation');
INSERT INTO DEV.PUBLIC.contract_activity_type (activity_id,activity_name) values (10,'Carpentry');

--subscription
truncate table DEV.PUBLIC.subscription;
INSERT INTO DEV.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (0, 1, 1*1, current_date);
INSERT INTO DEV.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (1, 3, 4.99*3, current_date);
INSERT INTO DEV.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (2, 6, 4.99*6, current_date);
INSERT INTO DEV.PUBLIC.subscription (subscription_id, subscription_months, subscription_amt_usd, subscription_activated_date) 
values (3, 12, 4.99*12, current_date);


commit;
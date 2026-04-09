-- Data for table `categories`
INSERT INTO categories (user_id, name, icon, parent_id, is_active, created_at, updated_at) VALUES 
(19, 'Машина', 'string', null, true, '2026-03-30 13:55:19.502 +0300', '2026-04-30 13:55:19.502 +0300'),
(19, 'Книги', 'string', null, true, '2026-03-30 13:55:19.502 +0300', '2026-04-30 13:55:19.502 +0300');


-- Data for table `accounts`
INSERT INTO accounts (user_id, name, type, currency, balance, is_active, created_at, updated_at) VALUES
(19, 'Сбербанк', 'Карта', 'RUB', '200000.00', true, '2026-03-30 13:56:19.502 +0300', '2026-04-30 13:56:19.502 +0300'),
(19, 'Наличные', 'Наличные', 'RUB', '1000.00', true, '2026-04-30 13:56:19.502 +0300', '2026-05-30 13:56:19.502 +0300');

-- Data for table `transactions`
INSERT INTO transactions (user_id, account_id, category_id, amount, type, description, transaction_date, is_active, created_at, updated_at) VALUES
(19, 8, 14, '10000.00', 'расходы', 'ТО', '2026-03-30', true, '2026-03-30 13:56:19.502 +0300', '2026-04-30 13:56:19.502 +0300'),
(19, 8, 14, '2000.00', 'расходы', 'Заправка', '2026-04-30', true, '2026-04-30 13:56:19.502 +0300', '2026-04-30 13:56:19.502 +0300');

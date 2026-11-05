-- ==============================================================================
-- NERDC Telemetry Simulator Database Reset & Seeding Script
-- Seeds Provinces, Districts, 4 Official Admin Users, Gateways, Fences,
-- 50 Sections, and 50 IoT Monitoring Devices
-- ==============================================================================

-- 1. Ensure Sri Lanka Provinces exist
INSERT INTO provinces (id, name) VALUES
    (1, 'Western'),
    (2, 'Central'),
    (3, 'Southern'),
    (4, 'Northern'),
    (5, 'Eastern'),
    (6, 'North Western'),
    (7, 'North Central'),
    (8, 'Uva'),
    (9, 'Sabaragamuwa')
ON CONFLICT (id) DO NOTHING;

-- 2. Ensure Sri Lanka Districts exist
INSERT INTO districts (id, province_id, name) VALUES
    (1, 1, 'Colombo'),
    (2, 1, 'Gampaha'),
    (3, 1, 'Kalutara'),
    (4, 2, 'Kandy'),
    (5, 2, 'Matale'),
    (6, 2, 'Nuwara Eliya'),
    (7, 3, 'Galle'),
    (8, 3, 'Matara'),
    (9, 3, 'Hambantota'),
    (10, 4, 'Jaffna'),
    (11, 4, 'Kilinochchi'),
    (12, 4, 'Mannar'),
    (13, 4, 'Vavuniya'),
    (14, 4, 'Mullaitivu'),
    (15, 5, 'Batticaloa'),
    (16, 5, 'Ampara'),
    (17, 5, 'Trincomalee'),
    (18, 6, 'Kurunegala'),
    (19, 6, 'Puttalam'),
    (20, 7, 'Anuradhapura'),
    (21, 7, 'Polonnaruwa'),
    (22, 8, 'Badulla'),
    (23, 8, 'Monaragala'),
    (24, 9, 'Ratnapura'),
    (25, 9, 'Kegalle')
ON CONFLICT (id) DO NOTHING;

-- 3. Clear Operational and Telemetry Data
DELETE FROM user_notifications;
DELETE FROM alert_events;
DELETE FROM alert_comments;
DELETE FROM alerts;
DELETE FROM telemetry_readings;
DELETE FROM audit_logs;
DELETE FROM user_sessions;

-- 4. Seed Complete Operational Workforce (Password: Admin@123456)
DELETE FROM fence_backup_maintenance_users;
DELETE FROM user_provinces;
DELETE FROM user_districts;
DELETE FROM users;

-- 4.1 Super Admin & 9 Regional Admins
INSERT INTO users (id, full_name, email, password_hash, role, enabled, password_change_required, staff_id, contact_number) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'National Super Admin',           'admin@nerdc.lk',          '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'SUPER_ADMIN', TRUE, FALSE, 'ADM-001',   '+94112223344'),
    ('a0000000-0000-0000-0000-000000000011', 'Western Regional Admin',          'admin.western@nerdc.lk',  '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-WST-01', '+94112220001'),
    ('a0000000-0000-0000-0000-000000000012', 'Central Regional Admin',          'admin.central@nerdc.lk',  '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-CEN-01', '+94112220002'),
    ('a0000000-0000-0000-0000-000000000003', 'Southern Regional Admin',         'admin.south@nerdc.lk',    '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-SOU-01', '+94112220003'),
    ('a0000000-0000-0000-0000-000000000014', 'Northern Regional Admin',         'admin.northern@nerdc.lk', '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-NOR-01', '+94112220004'),
    ('a0000000-0000-0000-0000-000000000004', 'Eastern Regional Admin',          'admin.east@nerdc.lk',     '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-EAS-01', '+94112220005'),
    ('a0000000-0000-0000-0000-000000000016', 'North Western Regional Admin',    'admin.nw@nerdc.lk',       '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-NW-01',  '+94112220006'),
    ('a0000000-0000-0000-0000-000000000002', 'North Central Regional Admin',    'admin.nc@nerdc.lk',       '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-NC-01',  '+94112220007'),
    ('a0000000-0000-0000-0000-000000000018', 'Uva Regional Admin',              'admin.uva@nerdc.lk',      '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-UVA-01', '+94112220008'),
    ('a0000000-0000-0000-0000-000000000019', 'Sabaragamuwa Regional Admin',    'admin.sab@nerdc.lk',      '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'REGIONAL_ADMIN', TRUE, FALSE, 'RA-SAB-01', '+94112220009');

-- 4.2 Field Admins (5 Active Districts)
INSERT INTO users (id, full_name, email, password_hash, role, enabled, password_change_required, staff_id, contact_number) VALUES
    ('b0000000-0000-0000-0000-000000000020', 'Anuradhapura Field Admin', 'fa.anuradhapura@dwc.gov.lk', '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'FIELD_ADMIN', TRUE, FALSE, 'FA-ANU-01', '+94771234501'),
    ('b0000000-0000-0000-0000-000000000021', 'Polonnaruwa Field Admin',  'fa.polonnaruwa@dwc.gov.lk',  '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'FIELD_ADMIN', TRUE, FALSE, 'FA-POL-01', '+94771234502'),
    ('b0000000-0000-0000-0000-000000000009', 'Hambantota Field Admin',   'fa.hambantota@dwc.gov.lk',   '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'FIELD_ADMIN', TRUE, FALSE, 'FA-HAM-01', '+94771234503'),
    ('b0000000-0000-0000-0000-000000000016', 'Ampara Field Admin',        'fa.ampara@dwc.gov.lk',       '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'FIELD_ADMIN', TRUE, FALSE, 'FA-AMP-01', '+94771234504'),
    ('b0000000-0000-0000-0000-000000000017', 'Trincomalee Field Admin',   'fa.trincomalee@dwc.gov.lk',   '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'FIELD_ADMIN', TRUE, FALSE, 'FA-TRI-01', '+94771234505');

-- 4.3 Maintenance Technicians (5 Fences)
INSERT INTO users (id, full_name, email, password_hash, role, enabled, password_change_required, staff_id, contact_number) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'Wilpattu Maintenance Officer',    'tech.wilpattu@dwc.gov.lk',    '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'MAINTENANCE', TRUE, FALSE, 'MN-WIL-01', '+94711234501'),
    ('c0000000-0000-0000-0000-000000000002', 'Minneriya Maintenance Officer',   'tech.minneriya@dwc.gov.lk',   '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'MAINTENANCE', TRUE, FALSE, 'MN-MIN-01', '+94711234502'),
    ('c0000000-0000-0000-0000-000000000003', 'Bundala Maintenance Officer',     'tech.bundala@dwc.gov.lk',     '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'MAINTENANCE', TRUE, FALSE, 'MN-BUN-01', '+94711234503'),
    ('c0000000-0000-0000-0000-000000000004', 'Gal Oya Maintenance Officer',     'tech.galoya@dwc.gov.lk',      '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'MAINTENANCE', TRUE, FALSE, 'MN-GAL-01', '+94711234504'),
    ('c0000000-0000-0000-0000-000000000005', 'Somawathiya Maintenance Officer', 'tech.somawathiya@dwc.gov.lk', '$2a$10$i4jTHUntTL5gYMeA7Fvgfurnf5nThxeYWRxFz4Js1w2WZcdnrWzfa', 'MAINTENANCE', TRUE, FALSE, 'MN-SOM-01', '+94711234505');

-- Assign Regional Admin Scopes
INSERT INTO user_provinces (user_id, province_id) VALUES
    ('a0000000-0000-0000-0000-000000000011', 1), -- Western
    ('a0000000-0000-0000-0000-000000000012', 2), -- Central
    ('a0000000-0000-0000-0000-000000000003', 3), -- Southern
    ('a0000000-0000-0000-0000-000000000014', 4), -- Northern
    ('a0000000-0000-0000-0000-000000000004', 5), -- Eastern
    ('a0000000-0000-0000-0000-000000000016', 6), -- North Western
    ('a0000000-0000-0000-0000-000000000002', 7), -- North Central
    ('a0000000-0000-0000-0000-000000000018', 8), -- Uva
    ('a0000000-0000-0000-0000-000000000019', 9)  -- Sabaragamuwa
ON CONFLICT (user_id, province_id) DO NOTHING;

-- Assign Field Admin Scopes
INSERT INTO user_provinces (user_id, province_id) VALUES
    ('b0000000-0000-0000-0000-000000000020', 7),
    ('b0000000-0000-0000-0000-000000000021', 7),
    ('b0000000-0000-0000-0000-000000000009', 3),
    ('b0000000-0000-0000-0000-000000000016', 5),
    ('b0000000-0000-0000-0000-000000000017', 5)
ON CONFLICT (user_id, province_id) DO NOTHING;

INSERT INTO user_districts (user_id, district_id) VALUES
    ('b0000000-0000-0000-0000-000000000020', 20),
    ('b0000000-0000-0000-0000-000000000021', 21),
    ('b0000000-0000-0000-0000-000000000009', 9),
    ('b0000000-0000-0000-0000-000000000016', 16),
    ('b0000000-0000-0000-0000-000000000017', 17)
ON CONFLICT (user_id, district_id) DO NOTHING;

-- Assign Maintenance Technician Scopes
INSERT INTO user_provinces (user_id, province_id) VALUES
    ('c0000000-0000-0000-0000-000000000001', 7),
    ('c0000000-0000-0000-0000-000000000002', 7),
    ('c0000000-0000-0000-0000-000000000003', 3),
    ('c0000000-0000-0000-0000-000000000004', 5),
    ('c0000000-0000-0000-0000-000000000005', 5)
ON CONFLICT (user_id, province_id) DO NOTHING;

INSERT INTO user_districts (user_id, district_id) VALUES
    ('c0000000-0000-0000-0000-000000000001', 20),
    ('c0000000-0000-0000-0000-000000000002', 21),
    ('c0000000-0000-0000-0000-000000000003', 9),
    ('c0000000-0000-0000-0000-000000000004', 16),
    ('c0000000-0000-0000-0000-000000000005', 17)
ON CONFLICT (user_id, district_id) DO NOTHING;

-- 5. Clear Topology Tables & Reset Identity Sequences
DELETE FROM gateway_fences;
DELETE FROM devices;
DELETE FROM sections;
DELETE FROM fences;
DELETE FROM gateways;

ALTER TABLE gateways ALTER COLUMN id RESTART WITH 1;
ALTER TABLE fences ALTER COLUMN id RESTART WITH 1;
ALTER TABLE sections ALTER COLUMN id RESTART WITH 1;
ALTER TABLE devices ALTER COLUMN id RESTART WITH 1;
ALTER TABLE telemetry_readings ALTER COLUMN id RESTART WITH 1;

-- Add gateway latitude and longitude columns if missing
ALTER TABLE gateways ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;
ALTER TABLE gateways ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;

-- 6. Seed 5 Regional Gateways
INSERT INTO gateways (id, name, serial, imei, status, signal, power, firmware, enabled, latitude, longitude) VALUES
    (1, 'Anuradhapura North Hub', 'GW-ANURADHAPURA-01', '864201040000001', 'online', 92, 98, 'v2.4.1', TRUE, 8.4520, 79.9820),
    (2, 'Polonnaruwa South Hub',  'GW-POLONNARUWA-02',  '864201040000002', 'online', 88, 96, 'v2.4.1', TRUE, 8.0250, 80.8850),
    (3, 'Hambantota Southern Hub', 'GW-HAMBANTOTA-03',   '864201040000003', 'online', 90, 97, 'v2.4.1', TRUE, 6.1850, 81.1950),
    (4, 'Ampara Eastern Hub',      'GW-AMPARA-04',       '864201040000004', 'online', 85, 95, 'v2.4.1', TRUE, 7.2150, 81.5250),
    (5, 'Trincomalee North-East Hub', 'GW-TRINCOMALEE-05','864201040000005', 'online', 89, 94, 'v2.4.1', TRUE, 8.1950, 81.1850);

-- 7. Seed 5 National Fences
INSERT INTO fences (id, code, name, province_id, district_id, length_km, gateway_id, average_voltage_kv, health, primary_maintenance_user_id) VALUES
    (1, 'FC-WILPATPU-01', 'Wilpattu Border Protection Fence',   7, 20, 15.50, 1, 6.80, 'HEALTHY', 'c0000000-0000-0000-0000-000000000001'),
    (2, 'FC-MINNERIYA-01','Minneriya Elephant Corridor Fence',  7, 21, 12.00, 2, 6.70, 'HEALTHY', 'c0000000-0000-0000-0000-000000000002'),
    (3, 'FC-BUNDALA-01',  'Bundala Wildlife Reserve Fence',     3, 9,  10.20, 3, 6.80, 'HEALTHY', 'c0000000-0000-0000-0000-000000000003'),
    (4, 'FC-GALOYA-01',   'Gal Oya Valley Protection Fence',    5, 16, 14.80, 4, 6.60, 'HEALTHY', 'c0000000-0000-0000-0000-000000000004'),
    (5, 'FC-SOMAWATH-01', 'Somawathiya Border Corridor Fence',  5, 17, 11.50, 5, 6.70, 'HEALTHY', 'c0000000-0000-0000-0000-000000000005');

-- Link Gateway to Fences
INSERT INTO gateway_fences (gateway_id, fence_id) VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5);

-- Link Backup Maintenance Contacts
DELETE FROM fence_backup_maintenance_users;
INSERT INTO fence_backup_maintenance_users (fence_id, user_id) VALUES
    (1, 'b0000000-0000-0000-0000-000000000020'), -- Wilpattu: Anuradhapura Field Admin
    (1, 'a0000000-0000-0000-0000-000000000001'), -- Wilpattu: Super Admin
    (2, 'b0000000-0000-0000-0000-000000000021'), -- Minneriya: Polonnaruwa Field Admin
    (2, 'a0000000-0000-0000-0000-000000000001'), -- Minneriya: Super Admin
    (3, 'b0000000-0000-0000-0000-000000000009'), -- Bundala: Hambantota Field Admin
    (3, 'a0000000-0000-0000-0000-000000000001'), -- Bundala: Super Admin
    (4, 'b0000000-0000-0000-0000-000000000016'), -- Gal Oya: Ampara Field Admin
    (4, 'a0000000-0000-0000-0000-000000000001'), -- Gal Oya: Super Admin
    (5, 'b0000000-0000-0000-0000-000000000017'), -- Somawathiya: Trincomalee Field Admin
    (5, 'a0000000-0000-0000-0000-000000000001'); -- Somawathiya: Super Admin

-- 8. Seed 50 Fence Sections (10 per Fence across 5 Fences)
INSERT INTO sections (id, fence_id, code, start_gps, end_gps, length_km, voltage_kv, battery, status, province_id, district_id) VALUES
    -- Fence 1 (Wilpattu)
    (1,  1, 'SEC-01', '8.4520,79.9820', '8.4610,79.9910', 3.10, 7.20, 95, 'HEALTHY', 7, 20),
    (2,  1, 'SEC-02', '8.4610,79.9910', '8.4720,80.0030', 3.20, 6.80, 96, 'HEALTHY', 7, 20),
    (3,  1, 'SEC-03', '8.4720,80.0030', '8.4850,80.0150', 3.00, 6.60, 94, 'HEALTHY', 7, 20),
    (4,  1, 'SEC-04', '8.4850,80.0150', '8.4980,80.0280', 3.10, 6.40, 97, 'HEALTHY', 7, 20),
    (5,  1, 'SEC-05', '8.4980,80.0280', '8.5100,80.0400', 3.10, 6.70, 95, 'HEALTHY', 7, 20),
    (6,  1, 'SEC-06', '8.5100,80.0400', '8.5210,80.0520', 3.00, 6.90, 96, 'HEALTHY', 7, 20),
    (7,  1, 'SEC-07', '8.5210,80.0520', '8.5320,80.0630', 2.80, 6.80, 93, 'HEALTHY', 7, 20),
    (8,  1, 'SEC-08', '8.5320,80.0630', '8.5440,80.0750', 3.00, 6.50, 95, 'HEALTHY', 7, 20),
    (9,  1, 'SEC-09', '8.5440,80.0750', '8.5550,80.0860', 2.90, 6.70, 97, 'HEALTHY', 7, 20),
    (10, 1, 'SEC-10', '8.5550,80.0860', '8.5660,80.0970', 3.10, 6.60, 94, 'HEALTHY', 7, 20),

    -- Fence 2 (Minneriya)
    (11, 2, 'SEC-01', '8.0250,80.8850', '8.0340,80.8960', 2.40, 7.00, 98, 'HEALTHY', 7, 21),
    (12, 2, 'SEC-02', '8.0340,80.8960', '8.0450,80.9080', 2.50, 6.70, 95, 'HEALTHY', 7, 21),
    (13, 2, 'SEC-03', '8.0450,80.9080', '8.0560,80.9200', 2.30, 6.50, 96, 'HEALTHY', 7, 21),
    (14, 2, 'SEC-04', '8.0560,80.9200', '8.0670,80.9310', 2.40, 6.80, 94, 'HEALTHY', 7, 21),
    (15, 2, 'SEC-05', '8.0670,80.9310', '8.0780,80.9420', 2.40, 6.40, 95, 'HEALTHY', 7, 21),
    (16, 2, 'SEC-06', '8.0780,80.9420', '8.0890,80.9530', 2.20, 6.90, 97, 'HEALTHY', 7, 21),
    (17, 2, 'SEC-07', '8.0890,80.9530', '8.1000,80.9650', 2.50, 6.60, 93, 'HEALTHY', 7, 21),
    (18, 2, 'SEC-08', '8.1000,80.9650', '8.1110,80.9760', 2.40, 6.70, 96, 'HEALTHY', 7, 21),
    (19, 2, 'SEC-09', '8.1110,80.9760', '8.1220,80.9870', 2.30, 6.50, 94, 'HEALTHY', 7, 21),
    (20, 2, 'SEC-10', '8.1220,80.9870', '8.1330,80.9980', 2.40, 6.80, 95, 'HEALTHY', 7, 21),

    -- Fence 3 (Bundala)
    (21, 3, 'SEC-01', '6.1850,81.1950', '6.1940,81.2060', 2.00, 7.10, 97, 'HEALTHY', 3, 9),
    (22, 3, 'SEC-02', '6.1940,81.2060', '6.2050,81.2180', 2.10, 6.80, 96, 'HEALTHY', 3, 9),
    (23, 3, 'SEC-03', '6.2050,81.2180', '6.2160,81.2300', 2.00, 6.60, 95, 'HEALTHY', 3, 9),
    (24, 3, 'SEC-04', '6.2160,81.2300', '6.2270,81.2410', 2.10, 6.50, 96, 'HEALTHY', 3, 9),
    (25, 3, 'SEC-05', '6.2270,81.2410', '6.2380,81.2520', 2.00, 6.70, 98, 'HEALTHY', 3, 9),
    (26, 3, 'SEC-06', '6.2380,81.2520', '6.2490,81.2630', 2.10, 7.00, 96, 'HEALTHY', 3, 9),
    (27, 3, 'SEC-07', '6.2490,81.2630', '6.2600,81.2740', 2.00, 6.90, 94, 'HEALTHY', 3, 9),
    (28, 3, 'SEC-08', '6.2600,81.2740', '6.2710,81.2850', 2.20, 6.70, 97, 'HEALTHY', 3, 9),
    (29, 3, 'SEC-09', '6.2710,81.2850', '6.2820,81.2960', 2.10, 6.60, 95, 'HEALTHY', 3, 9),
    (30, 3, 'SEC-10', '6.2820,81.2960', '6.2930,81.3070', 2.00, 6.80, 96, 'HEALTHY', 3, 9),

    -- Fence 4 (Gal Oya)
    (31, 4, 'SEC-01', '7.2150,81.5250', '7.2260,81.5380', 3.00, 6.90, 96, 'HEALTHY', 5, 16),
    (32, 4, 'SEC-02', '7.2260,81.5380', '7.2380,81.5510', 2.90, 6.70, 95, 'HEALTHY', 5, 16),
    (33, 4, 'SEC-03', '7.2380,81.5510', '7.2490,81.5630', 3.00, 6.50, 94, 'HEALTHY', 5, 16),
    (34, 4, 'SEC-04', '7.2490,81.5630', '7.2600,81.5750', 2.90, 6.60, 97, 'HEALTHY', 5, 16),
    (35, 4, 'SEC-05', '7.2600,81.5750', '7.2710,81.5870', 3.00, 6.30, 93, 'HEALTHY', 5, 16),
    (36, 4, 'SEC-06', '7.2710,81.5870', '7.2820,81.5990', 2.80, 6.80, 95, 'HEALTHY', 5, 16),
    (37, 4, 'SEC-07', '7.2820,81.5990', '7.2930,81.6110', 2.90, 6.70, 94, 'HEALTHY', 5, 16),
    (38, 4, 'SEC-08', '7.2930,81.6110', '7.3040,81.6230', 3.00, 6.60, 96, 'HEALTHY', 5, 16),
    (39, 4, 'SEC-09', '7.3040,81.6230', '7.3150,81.6350', 2.90, 6.50, 92, 'HEALTHY', 5, 16),
    (40, 4, 'SEC-10', '7.3150,81.6350', '7.3260,81.6470', 3.00, 6.80, 97, 'HEALTHY', 5, 16),

    -- Fence 5 (Somawathiya)
    (41, 5, 'SEC-01', '8.1950,81.1850', '8.2060,81.1980', 2.30, 7.30, 98, 'HEALTHY', 5, 17),
    (42, 5, 'SEC-02', '8.2060,81.1980', '8.2180,81.2110', 2.30, 6.80, 95, 'HEALTHY', 5, 17),
    (43, 5, 'SEC-03', '8.2180,81.2110', '8.2290,81.2230', 2.30, 6.40, 96, 'HEALTHY', 5, 17),
    (44, 5, 'SEC-04', '8.2290,81.2230', '8.2400,81.2350', 2.30, 6.60, 94, 'HEALTHY', 5, 17),
    (45, 5, 'SEC-05', '8.2400,81.2350', '8.2510,81.2470', 2.30, 6.50, 95, 'HEALTHY', 5, 17),
    (46, 5, 'SEC-06', '8.2510,81.2470', '8.2620,81.2590', 2.20, 6.90, 96, 'HEALTHY', 5, 17),
    (47, 5, 'SEC-07', '8.2620,81.2590', '8.2730,81.2710', 2.30, 6.70, 93, 'HEALTHY', 5, 17),
    (48, 5, 'SEC-08', '8.2730,81.2710', '8.2840,81.2830', 2.40, 6.60, 95, 'HEALTHY', 5, 17),
    (49, 5, 'SEC-09', '8.2840,81.2830', '8.2950,81.2950', 2.20, 6.80, 97, 'HEALTHY', 5, 17),
    (50, 5, 'SEC-10', '8.2950,81.2950', '8.3060,81.3070', 2.30, 6.70, 94, 'HEALTHY', 5, 17);

-- 9. Seed 50 IoT Voltage Monitoring Devices (10 per Gateway / Fence)
INSERT INTO devices (id, gateway_id, fence_id, section_id, name, serial, type, status, voltage, signal, battery, enabled) VALUES
    -- Gateway 1 (Wilpattu)
    (1,  1, 1, 1,  'Wilpattu Node 01', 'SN-12345',   'Voltage Monitor', 'online', 7.20, 90, 95, TRUE),
    (2,  1, 1, 2,  'Wilpattu Node 02', 'SN-E-01001', 'Voltage Monitor', 'online', 6.80, 88, 96, TRUE),
    (3,  1, 1, 3,  'Wilpattu Node 03', 'SN-E-01002', 'Voltage Monitor', 'online', 6.60, 85, 94, TRUE),
    (4,  1, 1, 4,  'Wilpattu Node 04', 'SN-E-01003', 'Voltage Monitor', 'online', 6.40, 92, 97, TRUE),
    (5,  1, 1, 5,  'Wilpattu Node 05', 'SN-E-01004', 'Voltage Monitor', 'online', 6.70, 89, 95, TRUE),
    (6,  1, 1, 6,  'Wilpattu Node 06', 'SN-E-01005', 'Voltage Monitor', 'online', 6.90, 91, 96, TRUE),
    (7,  1, 1, 7,  'Wilpattu Node 07', 'SN-E-01006', 'Voltage Monitor', 'online', 6.80, 87, 93, TRUE),
    (8,  1, 1, 8,  'Wilpattu Node 08', 'SN-E-01007', 'Voltage Monitor', 'online', 6.50, 89, 95, TRUE),
    (9,  1, 1, 9,  'Wilpattu Node 09', 'SN-E-01008', 'Voltage Monitor', 'online', 6.70, 93, 97, TRUE),
    (10, 1, 1, 10, 'Wilpattu Node 10', 'SN-E-01009', 'Voltage Monitor', 'online', 6.60, 90, 94, TRUE),

    -- Gateway 2 (Minneriya)
    (11, 2, 2, 11, 'Minneriya Node 01', 'SN-E-02001', 'Voltage Monitor', 'online', 7.00, 94, 98, TRUE),
    (12, 2, 2, 12, 'Minneriya Node 02', 'SN-E-02002', 'Voltage Monitor', 'online', 6.70, 89, 95, TRUE),
    (13, 2, 2, 13, 'Minneriya Node 03', 'SN-E-02003', 'Voltage Monitor', 'online', 6.50, 87, 96, TRUE),
    (14, 2, 2, 14, 'Minneriya Node 04', 'SN-E-02004', 'Voltage Monitor', 'online', 6.80, 91, 94, TRUE),
    (15, 2, 2, 15, 'Minneriya Node 05', 'SN-E-02005', 'Voltage Monitor', 'online', 6.40, 88, 95, TRUE),
    (16, 2, 2, 16, 'Minneriya Node 06', 'SN-E-02006', 'Voltage Monitor', 'online', 6.90, 93, 97, TRUE),
    (17, 2, 2, 17, 'Minneriya Node 07', 'SN-E-02007', 'Voltage Monitor', 'online', 6.60, 86, 93, TRUE),
    (18, 2, 2, 18, 'Minneriya Node 08', 'SN-E-02008', 'Voltage Monitor', 'online', 6.70, 90, 96, TRUE),
    (19, 2, 2, 19, 'Minneriya Node 09', 'SN-E-02009', 'Voltage Monitor', 'online', 6.50, 88, 94, TRUE),
    (20, 2, 2, 20, 'Minneriya Node 10', 'SN-E-02010', 'Voltage Monitor', 'online', 6.80, 91, 95, TRUE),

    -- Gateway 3 (Bundala)
    (21, 3, 3, 21, 'Bundala Node 01', 'SN-E-03001', 'Voltage Monitor', 'online', 7.10, 92, 97, TRUE),
    (22, 3, 3, 22, 'Bundala Node 02', 'SN-E-03002', 'Voltage Monitor', 'online', 6.80, 89, 96, TRUE),
    (23, 3, 3, 23, 'Bundala Node 03', 'SN-E-03003', 'Voltage Monitor', 'online', 6.60, 85, 95, TRUE),
    (24, 3, 3, 24, 'Bundala Node 04', 'SN-E-03004', 'Voltage Monitor', 'online', 6.50, 88, 96, TRUE),
    (25, 3, 3, 25, 'Bundala Node 05', 'SN-E-03005', 'Voltage Monitor', 'online', 6.70, 91, 98, TRUE),
    (26, 3, 3, 26, 'Bundala Node 06', 'SN-E-03006', 'Voltage Monitor', 'online', 7.00, 90, 96, TRUE),
    (27, 3, 3, 27, 'Bundala Node 07', 'SN-E-03007', 'Voltage Monitor', 'online', 6.90, 87, 94, TRUE),
    (28, 3, 3, 28, 'Bundala Node 08', 'SN-E-03008', 'Voltage Monitor', 'online', 6.70, 92, 97, TRUE),
    (29, 3, 3, 29, 'Bundala Node 09', 'SN-E-03009', 'Voltage Monitor', 'online', 6.60, 89, 95, TRUE),
    (30, 3, 3, 30, 'Bundala Node 10', 'SN-E-03010', 'Voltage Monitor', 'online', 6.80, 91, 96, TRUE),

    -- Gateway 4 (Gal Oya)
    (31, 4, 4, 31, 'Gal Oya Node 01', 'SN-E-04001', 'Voltage Monitor', 'online', 6.90, 89, 96, TRUE),
    (32, 4, 4, 32, 'Gal Oya Node 02', 'SN-E-04002', 'Voltage Monitor', 'online', 6.70, 87, 95, TRUE),
    (33, 4, 4, 33, 'Gal Oya Node 03', 'SN-E-04003', 'Voltage Monitor', 'online', 6.50, 84, 94, TRUE),
    (34, 4, 4, 34, 'Gal Oya Node 04', 'SN-E-04004', 'Voltage Monitor', 'online', 6.60, 90, 97, TRUE),
    (35, 4, 4, 35, 'Gal Oya Node 05', 'SN-E-04005', 'Voltage Monitor', 'online', 6.30, 86, 93, TRUE),
    (36, 4, 4, 36, 'Gal Oya Node 06', 'SN-E-04006', 'Voltage Monitor', 'online', 6.80, 91, 95, TRUE),
    (37, 4, 4, 37, 'Gal Oya Node 07', 'SN-E-04007', 'Voltage Monitor', 'online', 6.70, 88, 94, TRUE),
    (38, 4, 4, 38, 'Gal Oya Node 08', 'SN-E-04008', 'Voltage Monitor', 'online', 6.60, 92, 96, TRUE),
    (39, 4, 4, 39, 'Gal Oya Node 09', 'SN-E-04009', 'Voltage Monitor', 'online', 6.50, 85, 92, TRUE),
    (40, 4, 4, 40, 'Gal Oya Node 10', 'SN-E-04010', 'Voltage Monitor', 'online', 6.80, 90, 97, TRUE),

    -- Gateway 5 (Somawathiya)
    (41, 5, 5, 41, 'Somawathiya Node 01', 'SN-E-05001', 'Voltage Monitor', 'online', 7.30, 95, 98, TRUE),
    (42, 5, 5, 42, 'Somawathiya Node 02', 'SN-E-05002', 'Voltage Monitor', 'online', 6.80, 89, 95, TRUE),
    (43, 5, 5, 43, 'Somawathiya Node 03', 'SN-E-05003', 'Voltage Monitor', 'online', 6.40, 86, 96, TRUE),
    (44, 5, 5, 44, 'Somawathiya Node 04', 'SN-E-05004', 'Voltage Monitor', 'online', 6.60, 88, 94, TRUE),
    (45, 5, 5, 45, 'Somawathiya Node 05', 'SN-E-05005', 'Voltage Monitor', 'online', 6.50, 92, 95, TRUE),
    (46, 5, 5, 46, 'Somawathiya Node 06', 'SN-E-05006', 'Voltage Monitor', 'online', 6.90, 91, 96, TRUE),
    (47, 5, 5, 47, 'Somawathiya Node 07', 'SN-E-05007', 'Voltage Monitor', 'online', 6.70, 87, 93, TRUE),
    (48, 5, 5, 48, 'Somawathiya Node 08', 'SN-E-05008', 'Voltage Monitor', 'online', 6.60, 89, 95, TRUE),
    (49, 5, 5, 49, 'Somawathiya Node 09', 'SN-E-05009', 'Voltage Monitor', 'online', 6.80, 93, 97, TRUE),
    (50, 5, 5, 50, 'Somawathiya Node 10', 'SN-E-05010', 'Voltage Monitor', 'online', 6.70, 90, 94, TRUE);

-- Manual Migration SQL for Membership Card Module
-- Run this if you prefer manual SQL migration instead of Python script
-- Database: PostgreSQL

-- ==============================================
-- STEP 1: Add New Columns to Users Table
-- ==============================================

-- Add verification_token column (UUID, unique, indexed)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS verification_token UUID UNIQUE;

-- Add nomor_anggota column (unique identifier for member)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS nomor_anggota VARCHAR UNIQUE;

-- Add golongan column (member rank/level)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS golongan VARCHAR;

-- Add kwartir column (member district)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS kwartir VARCHAR;

-- Add membership_status column (active/inactive/expired/pending)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS membership_status VARCHAR DEFAULT 'active' NOT NULL;

-- Add valid_until column (expiration date)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS valid_until DATE;

-- Add foto_url column (profile photo URL)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS foto_url VARCHAR;

-- ==============================================
-- STEP 2: Create Indexes for Performance
-- ==============================================

-- Index on verification_token for fast lookup (public verification)
CREATE INDEX IF NOT EXISTS idx_users_verification_token 
ON users(verification_token);

-- Index on nomor_anggota for fast lookup
CREATE INDEX IF NOT EXISTS idx_users_nomor_anggota 
ON users(nomor_anggota);

-- ==============================================
-- STEP 3: Update Existing Users with Default Values
-- ==============================================

-- Generate verification tokens for users without one
-- Note: Replace uuid_generate_v4() with gen_random_uuid() for PostgreSQL 13+
UPDATE users 
SET verification_token = gen_random_uuid()
WHERE verification_token IS NULL;

-- Set default membership status for users without one
UPDATE users 
SET membership_status = 'active'
WHERE membership_status IS NULL;

-- Set default valid_until (1 year from now) for users without one
UPDATE users 
SET valid_until = CURRENT_DATE + INTERVAL '1 year'
WHERE valid_until IS NULL;

-- ==============================================
-- STEP 4: Update Default Admin with Sample Data (Optional)
-- ==============================================

-- Update admin user with sample membership data
UPDATE users 
SET 
    nomor_anggota = '001-ADM-2025',
    golongan = 'Pembina',
    kwartir = 'Kwarda Jawa Barat',
    membership_status = 'active',
    valid_until = CURRENT_DATE + INTERVAL '1 year'
WHERE username = 'admin' 
  AND nomor_anggota IS NULL;

-- ==============================================
-- STEP 5: Verify Migration
-- ==============================================

-- Check if all columns were added successfully
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
  AND column_name IN (
    'verification_token',
    'nomor_anggota',
    'golongan',
    'kwartir',
    'membership_status',
    'valid_until',
    'foto_url'
  )
ORDER BY column_name;

-- Check if indexes were created
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'users'
  AND indexname IN (
    'idx_users_verification_token',
    'idx_users_nomor_anggota'
  );

-- Check updated user data
SELECT 
    id,
    username,
    nama_lengkap,
    nomor_anggota,
    golongan,
    kwartir,
    membership_status,
    valid_until,
    verification_token IS NOT NULL as has_token
FROM users
LIMIT 5;

-- ==============================================
-- ROLLBACK (If needed - USE WITH CAUTION!)
-- ==============================================

-- Uncomment and run these commands ONLY if you need to rollback

/*
-- Remove indexes
DROP INDEX IF EXISTS idx_users_verification_token;
DROP INDEX IF EXISTS idx_users_nomor_anggota;

-- Remove columns
ALTER TABLE users DROP COLUMN IF EXISTS verification_token;
ALTER TABLE users DROP COLUMN IF EXISTS nomor_anggota;
ALTER TABLE users DROP COLUMN IF EXISTS golongan;
ALTER TABLE users DROP COLUMN IF EXISTS kwartir;
ALTER TABLE users DROP COLUMN IF EXISTS membership_status;
ALTER TABLE users DROP COLUMN IF EXISTS valid_until;
ALTER TABLE users DROP COLUMN IF EXISTS foto_url;

-- Verify rollback
SELECT column_name 
FROM information_schema.columns
WHERE table_name = 'users';
*/

-- ==============================================
-- NOTES
-- ==============================================

-- 1. This script is idempotent - safe to run multiple times
-- 2. Uses IF NOT EXISTS to prevent errors on re-run
-- 3. UUID generation: 
--    - PostgreSQL 13+: gen_random_uuid()
--    - PostgreSQL <13: uuid_generate_v4() (requires uuid-ossp extension)
-- 4. All changes are backward compatible
-- 5. Existing data is preserved
-- 6. Default values are set for new columns

-- ==============================================
-- TROUBLESHOOTING
-- ==============================================

-- If you get "function gen_random_uuid() does not exist":
-- Enable uuid-ossp extension and use uuid_generate_v4()
/*
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

UPDATE users 
SET verification_token = uuid_generate_v4()
WHERE verification_token IS NULL;
*/

-- If you get "column already exists":
-- The columns are already added, you can skip and continue

-- If you need to check current schema:
/*
\d+ users
*/

-- ==============================================
-- END OF MIGRATION SCRIPT
-- ==============================================

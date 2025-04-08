-- schema/init.sql

-- Drop tables for clean re-init
DROP TABLE IF EXISTS transactions_normalized, vendor_patterns, vendors, accounts, institutions CASCADE;

-- Institutions
CREATE TABLE institutions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    plaid_institution_id TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    institution_id INTEGER NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    plaid_account_id TEXT UNIQUE,
    account_number_suffix TEXT,
    type TEXT NOT NULL,
    subtype TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vendors
CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category_tier_1 TEXT NOT NULL,
    category_tier_2 TEXT NOT NULL,
    is_creditor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vendor Patterns
CREATE TABLE vendor_patterns (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    pattern TEXT NOT NULL,
    source_column TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (vendor_id, pattern)
);

-- Normalized Transactions
CREATE TABLE transactions_normalized (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    vendor_id INTEGER REFERENCES vendors(id),
    raw_description TEXT NOT NULL,
    parsed_vendor TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    posted_date DATE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('income', 'expense', 'transfer')),
    tag TEXT,
    comment TEXT,
    category_tier_1 TEXT,
    category_tier_2 TEXT,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

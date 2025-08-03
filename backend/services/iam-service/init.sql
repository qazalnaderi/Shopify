CREATE DATABASE shopify;
\c shopify;


-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 4. Websites Table
CREATE TABLE websites (
website_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
business_name VARCHAR(255) NOT NULL,
logo_url VARCHAR(255),
banner_image VARCHAR(255),
welcome_text TEXT,
faqs JSONB,
guide_page TEXT,
store_policy JSONB,
store_slogan VARCHAR(255),
about_us TEXT,
social_links JSONB,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1. Users Table (Sellers)
CREATE TABLE users (
user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
first_name VARCHAR(50) NOT NULL,
last_name VARCHAR(50) NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
password TEXT NOT NULL,
is_verified BOOLEAN NOT NULL DEFAULT FALSE,
can_reset_password BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Buyers Table (Customers)
CREATE TABLE buyers (
  buyer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password TEXT NOT NULL,
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  address TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  can_reset_password BOOLEAN DEFAULT FALSE,
  UNIQUE (website_id, email)  
);



-- 5. website Owners
CREATE TABLE website_owners (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. website Categories
CREATE TABLE website_categories (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
name VARCHAR(255) NOT NULL,
is_active BOOLEAN NOT NULL DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. website Subcategories
CREATE TABLE website_subcategories (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
parent_category_id UUID NOT NULL REFERENCES website_categories(id) ON DELETE CASCADE,
name VARCHAR(255) NOT NULL,
is_active BOOLEAN NOT NULL DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Items Table
CREATE TABLE items (
item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
category_id UUID NOT NULL REFERENCES website_categories(id) ON DELETE CASCADE,
subcategory_id UUID REFERENCES website_subcategories(id) ON DELETE SET NULL,
name VARCHAR(255) NOT NULL,
description TEXT,
price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
discount_percent INTEGER,
discount_price DECIMAL(10,2) CHECK (discount_price >= 0),
discount_active BOOLEAN DEFAULT FALSE,
discount_expires_at TIMESTAMP,
delivery_url VARCHAR(255),
post_purchase_note TEXT,
stock INTEGER CHECK (stock >= 0),
is_available BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE item_images (
    image_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    is_main BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 10. Orders
CREATE TABLE orders (
order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
buyer_id UUID NOT NULL REFERENCES buyers(buyer_id) ON DELETE CASCADE,
status VARCHAR(20) CHECK (status IN ('Pending', 'Paid', 'Canceled')) NOT NULL DEFAULT 'Pending',
total_price DECIMAL(10,2) CHECK (total_price >= 0) NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Orders Archive
CREATE TABLE orders_archive (
id UUID PRIMARY KEY,
website_id UUID REFERENCES websites(website_id) ON DELETE SET NULL,
item_id UUID REFERENCES items(item_id) ON DELETE SET NULL,
buyer_id UUID REFERENCES buyers(buyer_id) ON DELETE SET NULL,
status VARCHAR(20) CHECK (status IN ('Pending', 'Paid', 'Canceled')) NOT NULL,
total_price DECIMAL(10,2) CHECK (total_price >= 0) NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Reviews
CREATE TABLE reviews (
review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
website_id  UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
buyer_id UUID REFERENCES buyers(buyer_id) ON DELETE SET NULL,
rating INTEGER CHECK (rating >= 1 AND rating <= 5),
text TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Subscription Plans
CREATE TABLE subscription_plans (
  plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(50) UNIQUE NOT NULL,
  item_limit INTEGER NOT NULL,
  allow_discount BOOLEAN DEFAULT FALSE,
  allow_analytics BOOLEAN DEFAULT FALSE,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0)
);
insert into public.subscription_plans (name,item_limit,allow_discount,allow_analytics, price) values('Basic',100,False,False,500000);
insert into public.subscription_plans (name,item_limit,allow_discount,allow_analytics, price) values('Pro',500,True,True,1500000);
-- 14. Website plans
CREATE TABLE website_plans (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
  plan_id UUID NOT NULL REFERENCES subscription_plans(plan_id),
  activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);


CREATE TABLE website_slugs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE
);



CREATE TABLE cart_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
  buyer_id UUID NOT NULL,
  item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES items(item_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE admins (
    admin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE item_questions (
    question_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    buyer_id UUID NOT NULL REFERENCES buyers(buyer_id) ON DELETE CASCADE,
    website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    answer_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP
);

CREATE TABLE announcements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE coupons (
    coupon_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    website_id UUID NOT NULL REFERENCES websites(website_id) ON DELETE CASCADE,
    code VARCHAR(100) UNIQUE NOT NULL,
    discount_amount NUMERIC(10, 2) NOT NULL,
    expiration_date TIMESTAMP NULL,
    usage_limit INTEGER NULL,
    times_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE favorites(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
     buyer_id UUID NOT NULL REFERENCES buyers(buyer_id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION notify_new_review()
RETURNS TRIGGER AS $$
DECLARE
    _website_id UUID;
    _item_name TEXT;
BEGIN
    -- گرفتن website_id و نام محصول از جدول items
    SELECT website_id, name INTO _website_id, _item_name
    FROM items
    WHERE item_id = NEW.item_id;

    -- درج فقط نام محصول در ستون message
    INSERT INTO announcements (website_id, message)
    VALUES (
        _website_id,
        _item_name
    );

    -- فقط 5 اعلان آخر برای هر سایت نگه داشته شود
    DELETE FROM announcements
    WHERE website_id = _website_id
      AND id NOT IN (
          SELECT id FROM announcements
          WHERE website_id = _website_id
          ORDER BY created_at DESC
          LIMIT 5
      );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER trigger_notify_review
AFTER INSERT ON reviews
FOR EACH ROW
EXECUTE FUNCTION notify_new_review();

-- ✅ Indexes
CREATE UNIQUE INDEX idx_buyers_website_email ON buyers (website_id, email);
CREATE INDEX idx_buyers_email ON buyers(email);
CREATE INDEX idx_orders_website_id ON orders(website_id);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_website_owners_website_id ON website_owners(website_id);
CREATE INDEX idx_website_owners_user_id ON website_owners(user_id);

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection.
    """
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user="postgres",
        password=PASSWORD,
        host="localhost",
        port="5432",
    )


def create_tables():
    """
    A function to create the necessary tables for the project.
    """
    conn = get_connection()

    with conn:
        with conn.cursor() as cursor:
            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS languages(
                            language_id SERIAL PRIMARY KEY,
                            language_name VARCHAR(50)  
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS currencies(
                            currency_id SERIAL PRIMARY KEY,
                            currency_name VARCHAR(50)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS cities(
                            city_id SMALLSERIAL PRIMARY KEY,
                            city_name VARCHAR(75)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS listing_types(
                            listing_type_id SMALLSERIAL PRIMARY KEY,
                            type_name VARCHAR(50)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS payment_methods(
                            method_id SMALLSERIAL PRIMARY KEY,
                            method_name VARCHAR(50)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS listing_status(
                            status_id SMALLSERIAL PRIMARY KEY,
                            status_name VARCHAR(50)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS categories(
                            category_id SMALLSERIAL PRIMARY KEY,
                            category_name VARCHAR(50)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS item_conditions(
                            condition_id SMALLSERIAL PRIMARY KEY,
                            condition_name VARCHAR(50)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS shipping_options(
                            shipping_id SMALLSERIAL PRIMARY KEY,
                            shipping_name VARCHAR(50),
                            estimated_days SMALLINT CHECK (estimated_days >= 0),
                            shipping_cost DECIMAL(8,2)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS img(
                            img_id SERIAL PRIMARY KEY,
                            url VARCHAR(150)
                            )
                            """)
            )
            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS order_status(
                            status_id SMALLSERIAL PRIMARY KEY,
                            status_name VARCHAR(50)
                            )
                            """)
            )
            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users(
                            user_id SERIAL PRIMARY KEY,
                            
                            language_id INT REFERENCES languages(language_id) DEFAULT 1,
                            currency_id INT REFERENCES currencies(currency_id) DEFAULT 1,
                            profile_picture_id INT REFERENCES img(img_id),
                            city_id INT REFERENCES cities(city_id) NOT NULL,
                            
                            username VARCHAR(50) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL, 
                            email VARCHAR(75) UNIQUE NOT NULL, 
                            social_security_number CHAR(13) NOT NULL, 
                            first_name VARCHAR(50) NOT NULL, 
                            last_name VARCHAR(50) NOT NULL,
                            phone_number VARCHAR(20) UNIQUE NOT NULL,
                            address VARCHAR(100) NOT NULL,
                            postal_code VARCHAR(10) NOT NULL,
                            seller_rating DECIMAL(3, 2) DEFAULT 0 CHECK (seller_rating >= 0 AND seller_rating <=5),
                            total_reviews INT DEFAULT 0,

                            translation_on BOOLEAN DEFAULT FALSE,
                            vacation_mode BOOLEAN DEFAULT FALSE,
                            is_verified BOOLEAN DEFAULT FALSE,

                            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP 
                            )""")
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS listings(
                            listing_id SERIAL PRIMARY KEY,
                            
                            seller_id INT REFERENCES users(user_id),
                            listing_type_id INT REFERENCES listing_types(listing_type_id),
                            status_id INT REFERENCES listing_status(status_id),
                            
                            product_name VARCHAR(50) NOT NULL, 
                            title VARCHAR(20) NOT NULL,
                            description VARCHAR(500),
                            starting_price INT NOT NULL,
                            view_count INT DEFAULT 1,
                            
                            pick_up_available BOOLEAN DEFAULT FALSE,
                            
                            start_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            end_date TIMESTAMPTZ NOT NULL
                            )""")
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS orders(
                            order_id SERIAL PRIMARY KEY,
                            
                            seller_id INT REFERENCES users(user_id),
                            buyer_id INT REFERENCES users(user_id),
                            listing_id INT REFERENCES listings(listing_id),
                            shipping_option_id INT REFERENCES shipping_options(shipping_id),
                            payment_id INT REFERENCES payment_methods(method_id),
                            order_status_id INT REFERENCES order_status(status_id),
                            
                            shipping_cost DECIMAL(8,2) NOT NULL DEFAULT 0,
                            shipping_address VARCHAR(100) NOT NULL,
                            shipping_city VARCHAR(50),
                            shipping_postal_code VARCHAR(10) NOT NULL,
                            final_price DECIMAL(10,2) NOT NULL,
                            discount_amount DECIMAL(10,2) DEFAULT 0,
                            total_amount DECIMAL(10,2) NOT NULL,
                            order_number VARCHAR(50) UNIQUE NOT NULL,
                            
                            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                            )""")
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS listing_imgs(
                            img_id INT REFERENCES img(img_id),
                            listing_id INT REFERENCES listings(listing_id),
                            PRIMARY KEY (img_id, listing_id)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS watchlist(
                            user_id INT REFERENCES users(user_id),
                            listing_id INT REFERENCES listings(listing_id),
                            added_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (listing_id, user_id)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS bids(
                            bid_id BIGSERIAL PRIMARY KEY,
                            listing_id INT REFERENCES listings(listing_id),
                            user_id INT REFERENCES users(user_id),
                            bid_amount DECIMAL(8,2) NOT NULL CHECK (bid_amount > 0),
                            bidded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            is_auto BOOLEAN DEFAULT FALSE,
                            max_auto_bid DECIMAL(8,2)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS listing_payment_options(
                            listing_id INT REFERENCES listings(listing_id),
                            payment_method_id INT REFERENCES payment_methods(method_id),
                            PRIMARY KEY (listing_id, payment_method_id) 
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS listing_shipping_options(
                            listing_id INT REFERENCES listings(listing_id),
                            shipping_type_id INT REFERENCES shipping_options(shipping_id),
                            PRIMARY KEY(shipping_type_id, listing_id)
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS listing_categories(
                            listing_id INT REFERENCES listings(listing_id),
                            category_id INT REFERENCES categories(category_id),
                            PRIMARY KEY (category_id, listing_id) 
                            )
                            """)
            )

            (
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS messages(
                            message_id BIGSERIAL PRIMARY KEY,
                            sender_id INT REFERENCES users(user_id),
                            reciever_id INT REFERENCES users(user_id),
                            listing_id INT REFERENCES listings(listing_id),
                            message_text VARCHAR(250),
                            message_shown BOOLEAN DEFAULT FALSE,
                            sent_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                            )
                            """)
            )

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS reviews(
                            listing_id INT REFERENCES listings(listing_id),
                            reviewer_id INT REFERENCES users(user_id),
                            reviewee_id INT REFERENCES users(user_id),
                            is_negative BOOLEAN DEFAULT FALSE,
                            is_positive BOOLEAN DEFAULT FALSE,
                            review_text VARCHAR(500),
                            rating DECIMAL(3,2) NOT NULL,
                            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (reviewer_id, reviewee_id, listing_id) 
                            )
                            """)


if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")

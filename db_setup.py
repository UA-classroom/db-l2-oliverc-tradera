import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection
    In reality, we might use a connection pool, since
    this way we'll start a new connection each time
    someone hits one of our endpoints, which isn't great for performance
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
    cursor = conn.cursor()

    cursor.execute(""""
                    CREATE TABLE IF NOT EXISTS users(
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL, 
                    email VARCHAR(75) UNIQUE NOT NULL, 
                    social_security_number CHAR(13) NOT NULL, 
                    profile_picture_id INT REFERENCES img(img_id),
                    first_name VARCHAR(50) NOT NULL, 
                    last_name VARCHAR(50) NOT NULL,
                    phone_number VARCHAR(20) UNIQUE,
                    adress VARCHAR(100),
                    city_id INT REFERENCES cities(city_id),
                    postal_code VARCHAR(10),
                    seller_rating DECIMAL(3, 2) CHECK (seller_rating >= 0 AND seller_rating <=5),
                    total_reviews INT DEFAULT 0,
                    language_id INT REFERENCES languages(language_id),
                    currency_id INT REFERENCES currencies(currency_id),
                    translation_on BOOLEAN DEFAULT FALSE,
                    vacation_mode BOOLEAN DEFAULT FALSE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP 
                    )"""),

    cursor.execute(""""
                    CREATE TABLE IF NOT EXISTS listings(
                    listing_id SERIAL PRIMARY KEY,
                    seller_id INT REFERENCES users(user_id),
                    product_name VARCHAR(50) NOT NULL, 
                    title VARCHAR(20) NOT NULL,
                    description TEXT,
                    listing_type_id INT REFERENCES listing_types(listing_type_id),
                    starting_price INT NOT NULL,
                    start_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMPTZ NOT NULL, 
                    status_id INT REFERENCES listing_status(status_id),
                    view_count INT DEFAULT 1,
                    pick_up_available BOOLEAN DEFUALT FALSE
                    )"""),


    cursor.execute(""""
                    CREATE TABLE IF NOT EXISTS orders(
                    order_id SERIAL PRIMARY KEY,
                    seller_id INT REFERENCES users(user_id)
                    buyer_id INT REFERENCES users(user_id),
                    listing_id INT REFERENCES listings(listing_id),
                    shipping_option_id INT REFERENCES shipping_options(shipping_id),
                    payment_id INT REFERENCES payment_methods(method_id),
                    shipping_cost DECIMAL(8,2) NOT NULL DEFAULT 0,
                    shipping_address TEXT NOT NULL,
                    shipping_city VARCHAR(50),
                    shipping_postal_code VARCHAR(10) NOT NULL,
                    final_price DECIMAL(10,2) NOT NULL,
                    discount_amount DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) NOT NULL,
                    order_status_id INT REFERENCES order_status(status_id),
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )""")



if __name__ == "__main__":
    # Only reason to execute this file would be to create new tables, meaning it serves a migration file
    create_tables()
    print("Tables created successfully.")

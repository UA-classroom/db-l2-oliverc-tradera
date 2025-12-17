import psycopg2
from db_setup import get_connection as con
from psycopg2.extras import RealDictCursor

"""
This file is responsible for making database queries, which your fastapi endpoints/routes can use.
The reason we split them up is to avoid clutter in the endpoints, so that the endpoints might focus on other tasks 

- Try to return results with cursor.fetchall() or cursor.fetchone() when possible
- Make sure you always give the user response if something went right or wrong, sometimes 
you might need to use the RETURNING keyword to garantuee that something went right / wrong
e.g when making DELETE or UPDATE queries
- No need to use a class here
- Try to raise exceptions to make them more reusable and work a lot with returns
- You will need to decide which parameters each function should receive. All functions 
start with a connection parameter.
- Below, a few inspirational functions exist - feel free to completely ignore how they are structured
- E.g, if you decide to use psycopg3, you'd be able to directly use pydantic models with the cursor, these examples are however using psycopg2 and RealDictCursor
"""


def get_all_listings():
    """
    Fetches all active listings in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            get_all_listings_query = """
                SELECT *
                FROM listings 
                WHERE status_id = 1
                ORDER BY start_date DESC;
                """
            cursor.execute(get_all_listings_query)

            return cursor.fetchall()


def get_all_users():
    """
    Fetches all users in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    SELECT * 
                    FROM users
                    ORDER BY created_at DESC;
                    """
            )

            return cursor.fetchall()


def get_user_by_id(user_id: int):
    """
    Fetches a user by user_id.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT * 
                FROM users
                WHERE user_id = %s
                """,
                (user_id,),
            )

        return cursor.fetchone()


def get_listing_by_id(listing_id: int):
    """
    Fetches a listing by listing_id.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    SELECT * 
                    FROM listings
                    WHERE listing_id = %s
                    """,
                (listing_id,),
            )

            return cursor.fetchone()


def get_all_user_listings(seller_id: int):
    """
    Fetches all listings from one user.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    SELECT *
                    FROM listings
                    WHERE seller_id = %s
                    """,
                (seller_id,),
            )
            return cursor.fetchall()


def register_user(
    username: str,
    email: str,
    password: str,
    social_security_number: str,
    first_name: str,
    last_name: str,
    city_id: int,
    address: str,
    postal_code: str,
    phone_number: str,
):
    """
    Creates a new user in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    INSERT INTO users(
                    username,
                    email,
                    password_hash,
                    social_security_number,
                    first_name,
                    last_name,
                    city_id,
                    address,
                    postal_code,
                    phone_number
                    )
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING user_id, username, email, first_name, last_name, city_id, address, postal_code, phone_number, created_at
                    """,
                (
                    username,
                    email,
                    password,
                    social_security_number,
                    first_name,
                    last_name,
                    city_id,
                    address,
                    postal_code,
                    phone_number,
                ),
            )
            new_user = cursor.fetchone()
            conn.commit()
            return new_user


def add_city(city_name: str):
    """
    Creates a new city in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    INSERT INTO cities(city_name)
                    VALUES(%s)
                    RETURNING city_name
                    """,
                (city_name,),
            )
            new_city = cursor.fetchone()
            conn.commit()

            return new_city


def create_listing(
    seller_id: int,
    listing_type_id: int,
    product_name: str,
    title: str,
    description: str,
    starting_price: float,
    pick_up_available: bool,
    end_date: str,
):
    """
    Creates a new listing in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    INSERT INTO listings(
                            seller_id,
                            listing_type_id,
                            product_name,
                            title,
                            description,
                            starting_price,
                            pick_up_available,
                            end_date   
                            )
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING *
                    """,
                (
                    seller_id,
                    listing_type_id,
                    product_name,
                    title,
                    description,
                    starting_price,
                    pick_up_available,
                    end_date,
                ),
            )
            new_listing = cursor.fetchone()
            conn.commit()
            return new_listing


def create_bid(
    listing_id: int,
    user_id: int,
    bid_amount: float,
    is_auto: bool = False,
    max_auto_bid: int = None,
):
    """
    Creates a new bid in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    INSERT INTO bids(
                        listing_id,
                        user_id,
                        bid_amount,
                        is_auto,
                        max_auto_bid
                        )
                        VALUES(%s, %s, %s, %s, %s)
                        RETURNING *
                    """,
                (listing_id, user_id, bid_amount, is_auto, max_auto_bid),
            )
            new_bid = cursor.fetchone()
            conn.commit()
            return new_bid


def create_review(
    listing_id: int,
    reviewer_id: int,
    reviewee_id: int,
    review_text: str,
    rating: int,
    is_negative: bool = False,
    is_positive: bool = False,
):
    """
    Creates a new review in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    INSERT INTO reviews(
                        listing_id,
                        reviewer_id,
                        reviewee_id,
                        is_negative,
                        is_positive,
                        review_text,
                        rating
                        )
                        VALUES(%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """,
                (
                    listing_id,
                    reviewer_id,
                    reviewee_id,
                    is_negative,
                    is_positive,
                    review_text,
                    rating,
                ),
            )
            new_review = cursor.fetchone()
            conn.commit()
            return new_review


def update_listing(
    listing_type_id: int,
    product_name: str,
    title: str,
    description: str,
    starting_price: float,
    pick_up_available: bool,
    end_date: str,
    listing_id: int,
):
    """
    Updates a listing.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                            UPDATE listings
                            SET 
                                listing_type_id = %s,
                                product_name = %s, 
                                title = %s, 
                                description = %s,
                                starting_price = %s,
                                pick_up_available = %s,
                                end_date = %s
                                WHERE listing_id = %s 
                                RETURNING *
    """,
                (
                    listing_type_id,
                    product_name,
                    title,
                    description,
                    starting_price,
                    pick_up_available,
                    end_date,
                    listing_id,
                ),
            )

            updated_listing = cursor.fetchone()
            conn.commit()
            return updated_listing


def update_user(
    language_id: int,
    currency_id: int,
    profile_picture_id: int,
    city_id: int,
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    phone_number: str,
    address: str,
    postal_code: str,
    user_id: int,
):
    """
    Updates a user.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    UPDATE users
                    SET 
                    language_id = %s,
                    currency_id = %s,
                    profile_picture_id = %s,
                    city_id = %s,
                    
                    username = %s,
                    email = %s,
                    first_name = %s,
                    last_name = %s,
                    phone_number = %s,
                    address = %s,
                    postal_code = %s,
                    WHERE user_id = %s
                    RETURNING *
                    """,
                (
                    language_id,
                    currency_id,
                    profile_picture_id,
                    city_id,
                    username,
                    email,
                    first_name,
                    last_name,
                    phone_number,
                    address,
                    postal_code,
                    user_id,
                ),
            )
            updated_user = cursor.fetchone()
            conn.commit()
            return updated_user


def update_listing_status(listing_id: int, status_id: int):
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                    """
                    UPDATE listings
                    SET 
                    status_id = %s,
                    WHERE listing_id = %s
                    RETURNING *
                    """,
                (status_id, listing_id),
            )
            updated_status = cursor.fetchone()
            conn.commit()
            return updated_status


def update_password(password_hash: str, user_id: int):
    """
    Updates a users password.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    UPDATE users
                    SET 
                    password_hash = %s
                    WHERE user_id = %s
                    RETURNING user_id
                    """,
                    (password_hash, user_id),
                )
                updated_user = cursor.fetchone()
                conn.commit()
                return updated_user
        

def update_order(
    shipping_option_id: int,
    order_status_id: int,
    shipping_address: str,
    shipping_city: str,
    shipping_postal_code: str,
    final_price: float,
    discount_amount: float,
    order_id: int,
):
    """
    Updates a order.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    UPDATE orders
                    SET
                        shipping_option_id = %s
                        order_status_id = %s
                        shipping_address = %s
                        shipping_city = %s
                        shipping_postal_code = %s
                        final_price = %s
                        discount_amount = %s
                    WHERE order_id = %s 
                    RETURNING *
                    """,
                    (
                        shipping_option_id,
                        order_status_id,
                        shipping_address,
                        shipping_city,
                        shipping_postal_code,
                        final_price,
                        discount_amount,
                        order_id,
                    ),
                )
                updated_order = cursor.fetchone()
                conn.commit()
                return updated_order 
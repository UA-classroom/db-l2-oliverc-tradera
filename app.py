import os

import psycopg2
from db_setup import get_connection as con
from fastapi import FastAPI, HTTPException
from psycopg2.errors import (
    CheckViolation,
    DataError,
    ForeignKeyViolation,
    NotNullViolation,
    UniqueViolation,
)
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()
"""
ADD ENDPOINTS FOR FASTAPI HERE
Make sure to do the following:
- Use the correct HTTP method (e.g get, post, put, delete)
- Use correct STATUS CODES, e.g 200, 400, 401 etc. when returning a result to the user
- Use pydantic models whenever you receive user data and need to validate the structure and data types (VG)
This means you need some error handling that determine what should be returned to the user
Read more: https://www.geeksforgeeks.org/10-most-common-http-status-codes/
- Use correct URL paths the resource, e.g some endpoints should be located at the exact same URL, 
but will have different HTTP-verbs.
"""


# INSPIRATION FOR A LIST-ENDPOINT - Not necessary to use pydantic models, but we could to ascertain that we return the correct values
# @app.get("/items/")
# def read_items():
#     con = get_connection()
#     items = get_items(con)
#     return {"items": items}


# INSPIRATION FOR A POST-ENDPOINT, uses a pydantic model to validate
# @app.post("/validation_items/")
# def create_item_validation(item: ItemCreate):
#     con = get_connection()
#     item_id = add_item_validation(con, item)
#     return {"item_id": item_id}


@app.get("/listings")
def get_all_listings():
    """
    Fetches all active listings in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                get_all_listings_query = """
                SELECT *
                FROM listings 
                WHERE status_id = 1
                ORDER BY start_date DESC;
                """
                cursor.execute(get_all_listings_query)

                listings = cursor.fetchall()
                if not listings:
                    raise HTTPException(
                        status_code=404, detail="No active listings found."
                    )

                return listings

            except psycopg2.DatabaseError:
                raise HTTPException(status_code=500, detail="Database error occured.")
            except psycopg2.OperationalError:
                raise HTTPException(
                    status_code=503, detail="No database connection found."
                )


@app.get("/users")
def get_all_users():
    """
    Fetches all users in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    SELECT * 
                    FROM users
                    ORDER BY created_at DESC;
                    """
                )
                users = cursor.fetchall()
                return users
            except psycopg2.DatabaseError:
                raise HTTPException(status_code=500, detail="Database error occured.")
            except psycopg2.OperationalError:
                raise HTTPException(
                    status_code=503, detail="No database connection found."
                )


@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """

                                SELECT * 
                                FROM users
                                WHERE user_id = %s
                                """,
                    (user_id,),
                )

                user = cursor.fetchone()
                if user is None:
                    raise HTTPException(
                        status_code=404, detail="No user found with given 'user_id'."
                    )
                return user
            except psycopg2.DatabaseError:
                raise HTTPException(status_code=500, detail="Database error occured.")
            except psycopg2.OperationalError:
                raise HTTPException(
                    status_code=503, detail="No database connection found."
                )


@app.get("/listings/{listing_id}")
def get_listing_by_id(listing_id: int):
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """

                                SELECT * 
                                FROM listings
                                WHERE listing_id = %s
                                """,
                    (listing_id,),
                )

                listing = cursor.fetchone()
                if listing is None:
                    raise HTTPException(
                        status_code=404,
                        detail="No listing found with given 'listing_id'.",
                    )
                return listing
            except psycopg2.DatabaseError:
                raise HTTPException(status_code=500, detail="Database error occured.")
            except psycopg2.OperationalError:
                raise HTTPException(
                    status_code=503, detail="No database connection found."
                )


@app.get("/users/{user_id}/listings")
def get_all_user_listings(seller_id: int):
    """
    Fetches all listings from one user.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                            SELECT *
                            FROM listings
                            WHERE seller_id = %s
""",
                    (seller_id,),
                )
                listings = cursor.fetchall()
                if not listings:
                    raise HTTPException(
                        status_code=404,
                        detail="Provided user does not have any listings.",
                    )
                return listings
            except psycopg2.DatabaseError:
                raise HTTPException(status_code=500, detail="Database error occured.")
            except psycopg2.OperationalError:
                raise HTTPException(
                    status_code=503, detail="No database connection found."
                )


@app.post("/new_user")
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
            try:
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
                if not new_user:
                    conn.rollback()
                    raise HTTPException(
                        status_code=422,
                        detail="Failed to create new listing, data provided is invalid.",
                    )
                conn.commit()
                return new_user
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409, detail="Listing already exists with same info."
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400, detail="Invalid 'seller_id' or 'listing_type_id'"
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.post("/new_city")
def add_city(city_name: str):
    """
    Creates a new city in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
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
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(status_code=409, detail="City already exists.")


@app.post("/new_listing")
def create_listing(
    seller_id: int,
    listing_type_id: int,
    product_name: str,
    title: str,
    description: str,
    starting_price: int,
    pick_up_available: bool,
    end_date: str,
):
    """
    Creates a new listing in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
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
                if not new_listing:
                    conn.rollback()
                    raise HTTPException(
                        status_code=422,
                        detail="Failed to create new listing, data provided is invalid.",
                    )
                conn.commit()
                return new_listing
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409, detail="Listing already exists with same info."
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400, detail="Invalid 'seller_id' or 'listing_type_id'"
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.post("/bids")
def create_bid(
    listing_id: int,
    user_id: int,
    bid_amount: int,
    is_auto: bool = False,
    max_auto_bid: int = None,
):
    """
    Creates a new bid in database.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
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
                if not new_bid:
                    conn.rollback()
                    raise HTTPException(
                        status_code=422,
                        detail="Failed to create new bid, data provided is invalid.",
                    )
                conn.commit()
                return new_bid
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409, detail="Bidding already exists with same info."
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400, detail="Invalid 'listing_id' or 'user_id'"
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.post("/reviews")
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
            try:
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
                if not new_review:
                    conn.rollback()
                    raise HTTPException(
                        status_code=422,
                        detail="Failed to create review, data provided is invalid.",
                    )
                conn.commit()
                return new_review
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409, detail="Review already exists with same info."
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'listing_id', 'reviewee_id' or 'reviewer_id'.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.put("/listings/{listing_id}")
def update_listing(
    listing_id: int,
    listing_type_id: int,
    status_id: int,
    product_name: str,
    title: str,
    description: str,
    starting_price: int,
    pick_up_available: bool,
    end_date: str,
):
    """
    Updates a listing.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                            UPDATE listings
                            SET 
                                listing_type_id = %s,
                                status_id = %s,
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
                        status_id,
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
                if not updated_listing:
                    raise HTTPException(
                        status_code=404, detail="Couldn't find requested listing."
                    )
                conn.commit()

                return updated_listing
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409, detail="Listing already exists with same info."
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'listing_type_id' or 'status_id'.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.put("/users/{user_id}")
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
):
    """
    Updates a user.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
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
                    ),
                )
                updated_user = cursor.fetchone()
                if not updated_user:
                    raise HTTPException(
                        status_code=404, detail="Couldn't find requested user."
                    )
                conn.commit()
                return updated_user
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409, detail="User already exists with same info."
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'language_id', 'profile_picture_id', 'city_id' or 'currency_id'.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


# @app.put()
# @app.put()
# @app.put()

# @app.delete()
# @app.delete()
# @app.delete()
# @app.delete()
# @app.delete()

# @app.patch()

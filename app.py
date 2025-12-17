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


@app.get("/all_listings")
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


@app.get("/all_users")
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


@app.get("/user_by_id")
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


# @app.get("/")
# @app.get("/")


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


# @app.post("/")
# @app.post("/")

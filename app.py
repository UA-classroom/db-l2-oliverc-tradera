import os

import psycopg2
from db_setup import get_connection as con
from fastapi import FastAPI, HTTPException
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
    conn = con()
    cursor = conn.cursor()
    with conn:
        with cursor:
            try:
                get_all_listings_query = """
                SELECT *
                FROM listings 
                WHERE status_id = 1
                ORDER BY start_date DESC;
                """
                cursor.execute(get_all_listings_query)

                rows = cursor.fetch(get_all_listings_query)

                listings = [dict(row) for row in rows]

                return listings

            except Exception as e:
                pass


# @app.get("/")

# @app.get("/")
# @app.get("/")
# @app.get("/")


@app.post("/users")
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
        with conn.cursor() as cursor:
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


@app.post("/city")
def add_city(city_name: str):
    with con() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities(city_name)
                VALUES(%s)
                RETURNING city_name
                """,
                (city_name,),
            )
            result = cursor.fetchone()
            conn.commit()

            return result[0]


# @app.post("/")
# @app.post("/")
# @app.post("/")

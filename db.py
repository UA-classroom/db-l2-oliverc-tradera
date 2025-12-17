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

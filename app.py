import db
import psycopg2
from db_setup import get_connection as con
from fastapi import FastAPI, HTTPException
from psycopg2.errors import (
    DataError,
    ForeignKeyViolation,
    UniqueViolation,
)
from psycopg2.extras import RealDictCursor

app = FastAPI()


@app.get("/listings")
def get_all_listings():
    """
    Fetches all active listings in database.
    """
    try:
        listings = db.get_all_listings()
        if not listings:
            raise HTTPException(status_code=404, detail="No active listings found.")

        return listings

    except psycopg2.DatabaseError:
        raise HTTPException(status_code=500, detail="Database error occured.")
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="No database connection found.")


@app.get("/users")
def get_all_users():
    """
    Fetches all users in database.
    """
    try:
        users = db.get_all_users()
        return users
    except psycopg2.DatabaseError:
        raise HTTPException(status_code=500, detail="Database error occured.")
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="No database connection found.")


@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    """
    Fetches a user by user_id.
    """
    try:
        user = db.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(
                status_code=404, detail="No user found with given 'user_id'."
            )
        return user
    except psycopg2.DatabaseError:
        raise HTTPException(status_code=500, detail="Database error occured.")
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="No database connection found.")


@app.get("/listings/{listing_id}")
def get_listing_by_id(listing_id: int):
    """
    Fetches a listing by listing_id.
    """
    try:
        listing = db.get_listing_by_id(listing_id=listing_id)
        if listing is None:
            raise HTTPException(
                status_code=404,
                detail="No listing found with given 'listing_id'.",
            )
        return listing
    except psycopg2.DatabaseError:
        raise HTTPException(status_code=500, detail="Database error occured.")
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="No database connection found.")


@app.get("/users/{user_id}/listings")
def get_all_user_listings(seller_id: int):
    """
    Fetches all listings from one user.
    """
    try:
        listings = db - get_all_user_listings(seller_id=seller_id)
        if not listings:
            raise HTTPException(
                status_code=404,
                detail="Provided user does not have any listings.",
            )
        return listings
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="No database connection found.")
    except psycopg2.DatabaseError:
        raise HTTPException(status_code=500, detail="Database error occured.")


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
    try:
        new_user = db.register_user(
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
        )
        if not new_user:
            raise HTTPException(
                status_code=422,
                detail="Failed to create new listing, data provided is invalid.",
            )
        return new_user
    except UniqueViolation:
        raise HTTPException(
            status_code=409, detail="Listing already exists with same info."
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=400, detail="Invalid 'seller_id' or 'listing_type_id'"
        )
    except DataError:
        raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.post("/new_city")
def add_city(city_name: str):
    """
    Creates a new city in database.
    """
    try:
        new_city = db.add_city(city_name=city_name)
        return new_city
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="City already exists.")


@app.post("/new_listing")
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

    try:
        new_listing = db.create_listing(
            seller_id,
            listing_type_id,
            product_name,
            title,
            description,
            starting_price,
            pick_up_available,
            end_date,
        )
        if not new_listing:
            raise HTTPException(
                status_code=422,
                detail="Failed to create new listing, data provided is invalid.",
            )
        return new_listing
    except UniqueViolation:
        raise HTTPException(
            status_code=409, detail="Listing already exists with same info."
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=400, detail="Invalid 'seller_id' or 'listing_type_id'"
        )
    except DataError:
        raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.post("/bids")
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
    try:
        new_bid = db.create_bid(listing_id, user_id, bid_amount, is_auto, max_auto_bid)
        if not new_bid:
            raise HTTPException(
                status_code=422,
                detail="Failed to create new bid, data provided is invalid.",
            )

        return new_bid
    except UniqueViolation:
        raise HTTPException(
            status_code=409, detail="Bidding already exists with same info."
        )
    except ForeignKeyViolation:
        raise HTTPException(status_code=409, detail="Invalid 'listing_id' or 'user_id'")
    except DataError:
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
    try:
        new_review = db.create_review(
            listing_id,
            reviewer_id,
            reviewee_id,
            review_text,
            rating,
            is_negative,
            is_positive,
        )
        if not new_review:
            raise HTTPException(
                status_code=422,
                detail="Failed to create review, data provided is invalid.",
            )
        return new_review
    except UniqueViolation:
        raise HTTPException(
            status_code=409, detail="Review already exists with same info."
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="Invalid 'listing_id', 'reviewee_id' or 'reviewer_id'.",
        )
    except DataError:
        raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.put("/listings/{listing_id}")
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
            try:
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


@app.put("/listings/{listing_id}/status")
def update_listing_status(listing_id: int, status_id: int):
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
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
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'status_id'.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.put("/users/{user_id}/password")
def update_password(password_hash: str, user_id: int):
    """
    Updates a users password.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
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
                if not updated_user:
                    raise HTTPException(
                        status_code=404,
                        detail="Could not find requested user_id for a user.",
                    )
                conn.commit()
                return {"message: Successfully changed password.user": updated_user}
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'user_id'.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.put("/orders/{order_id}")
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
            try:
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
                if not updated_order:
                    conn.rollback()
                    raise HTTPException(
                        status_code=404,
                        detail="Could not find requested order_id for a order.",
                    )
                conn.commit()
                return updated_order
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409, detail="Order already exists with same info."
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'buyer_id', 'listing_id', 'shipping_option_id', 'shipping_option_id' or 'order_status_id'.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: int):
    """
    Updates a listings.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                            DELETE FROM listings
                            WHERE listing_id = %s
                            RETURNING listing_id, title
""",
                    (listing_id),
                )
                deleted_listing = cursor.fetchone()
                if not deleted_listing:
                    raise HTTPException(
                        status_code=404, detail="Couldn't find the requested listing."
                    )
                conn.commit()
                return deleted_listing
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete listing, has active relations.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """
    Deletes a user.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                            DELETE FROM users
                            WHERE user_id = %s
                            RETURNING user_id, username
""",
                    (user_id),
                )
                deleted_user = cursor.fetchone()
                if not deleted_user:
                    raise HTTPException(
                        status_code=404, detail="Couldn't find the requested user."
                    )
                conn.commit()
                return deleted_user
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete user, has active relations.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.delete("/messages/{message_id}")
def delete_message(message_id: int):
    """
    Deletes a message.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                            DELETE FROM messages
                            WHERE message_id = %s
                            RETURNING message_id, message_text
""",
                    (message_id),
                )
                deleted_message = cursor.fetchone()
                if not deleted_message:
                    raise HTTPException(
                        status_code=404, detail="Couldn't find the requested message."
                    )
                conn.commit()
                return deleted_message
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete message, has active relations.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.delete("/payment_methods/{method_id}")
def delete_payment_method(method_id: int):
    """
    Deletes a payment_method.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                            DELETE FROM payment_methods
                            WHERE method_id = %s
                            RETURNING method_id, method_name
""",
                    (method_id),
                )
                deleted_payment_method = cursor.fetchone()
                if not deleted_payment_method:
                    raise HTTPException(
                        status_code=404,
                        detail="Couldn't find the requested payment_method.",
                    )
                conn.commit()
                return deleted_payment_method
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    """
    Deletes a order.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                            DELETE FROM orders
                            WHERE order_id = %s
                            RETURNING order_id, order_number
""",
                    (order_id),
                )
                deleted_order = cursor.fetchone()
                if not deleted_order:
                    raise HTTPException(
                        status_code=404, detail="Couldn't find the requested order."
                    )
                conn.commit()
                return deleted_order
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete order, has active relations.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")


@app.patch("/users/{user_id}")
def partial_update_user(
    user_id: int,
    username: str = None,
    email: str = None,
    first_name: str = None,
    last_name: str = None,
    phone_number: str = None,
    address: str = None,
    postal_code: str = None,
    language_id: int = None,
    currency_id: int = None,
    city_id: int = None,
    profile_picture_id: int = None,
    translation_on: bool = None,
    vacation_mode: bool = None,
):
    """
    Partially updates a user based on the input.
    """
    with con() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            updated_values = []
            values = []

            if username:
                updated_values.append("username = %s")
                values.append(username)
            if email:
                updated_values.append("email = %s")
                values.append(email)
            if first_name:
                updated_values.append("first_name = %s")
                values.append(first_name)
            if last_name:
                updated_values.append("last_name = %s")
                values.append(last_name)
            if phone_number:
                updated_values.append("phone_number = %s")
                values.append(phone_number)
            if address:
                updated_values.append("address = %s")
                values.append(address)
            if postal_code:
                updated_values.append("postal_code = %s")
                values.append(postal_code)
            if language_id:
                updated_values.append("language_id = %s")
                values.append(language_id)
            if currency_id:
                updated_values.append("currency_id = %s")
                values.append(currency_id)
            if city_id:
                updated_values.append("city_id = %s")
                values.append(city_id)
            if profile_picture_id:
                updated_values.append("profile_picture_id = %s")
                values.append(profile_picture_id)
            if translation_on is not None:
                updated_values.append("translation_on = %s")
                values.append(translation_on)
            if vacation_mode is not None:
                updated_values.append("vacation_mode = %s")
                values.append(vacation_mode)

            if not updated_values:
                raise HTTPException(status_code=400, detail="No fields updated.")

            values.append(user_id)

            query = f"UPDATE users SET {', '.join(updated_values)} WHERE user_id = %s"
            try:
                cursor.execute(query, values)
                updated_user = cursor.fetchone()
                if not updated_user:
                    raise HTTPException(status_code=404, detail="Couldn't find user.")
                conn.commit()

                return updated_user
            except UniqueViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=409,
                    detail="username, email or phone_number already exists.",
                )
            except ForeignKeyViolation:
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'language_id', 'currency_id', 'city_id' or 'profile_picture_id'.",
                )
            except DataError:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Invalid data format/type.")

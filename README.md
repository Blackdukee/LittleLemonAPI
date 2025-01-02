# Little Lemon API

Little Lemon API is a Django REST framework-based application for managing categories, menu items, carts, orders, and user roles (managers and delivery crew) for a restaurant.

## Features

- Manage categories and menu items
- User authentication and authorization
- Manage user roles (managers and delivery crew)
- Manage carts and orders
- Rate limiting for API requests


username  |password   |gmail			        |role               |token
----------|-----------|-------------------------|-------------------|-------------------
admin	  |lemon@789! | admin@littlelemon.com	| admin             | 2d1606f17f88bfc4a34112cf4792af7d95564893
mario     |lemon@789! | mario@littlelemon.com 	| manager           | daeacb39254ceb0a30bed8e7fd50e70caaf23a25
adrian    |lemon@789! | adrian@littlelemon.com 	| delivery crew     | 4810958a5a1301ba05be41434160d28ee843bb01
user1     |lemon@789! | user1@example.com       | customer          | ea6975c596f3413849161498797b26282d9f2f70
user2     |lemon@789! | user2@example.com 	    | customer          | 4e6b9c44bb346e9391dbd46fe4e440ecbf167fa9	

Note: when make put or patch request for orders use user id to update the delivery crew and status for all user's orders 

## Dependencies

- Python 3.8+
- Django 3.2+
- Django REST framework 3.12+
- djangorestframework-simplejwt 4.7+
- psycopg2-binary 2.8+
- django-cors-headers 3.7+

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/little-lemon-api.git
    cd little-lemon-api
    ```

2. Install `pipenv` if you haven't already:

    ```bash
    pip install pipenv
    ```

3. Install the required dependencies using `pipenv`:

    ```bash
    pipenv install
    ```

4. Activate the virtual environment:

    ```bash
    pipenv shell
    ```


5. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Usage

- Access the API at `http://127.0.0.1:8000/api/`
- Access the admin panel at `http://127.0.0.1:8000/admin/`

## API Endpoints

- `/api/categories/` - Manage categories
- `/api/menu-items/` - Manage menu items
- `/api/cart/` - Manage cart items
- `/api/orders/` - Manage orders
- `/api/manager-users/` - Manage manager users
- `/api/delivery-crew-users/` - Manage delivery crew users

## Authentication

The API uses token-based authentication. Obtain a token by sending a POST request with your username and password to `/api/token/`.

## Rate Limiting

The API has rate limiting enabled to prevent abuse. Authenticated users have a higher rate limit than anonymous users.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
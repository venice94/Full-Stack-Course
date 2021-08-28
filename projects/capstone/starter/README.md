Wallet App API Document

This document serves to help clients understand and integrate to the relevant API endpoints available in the Wallet App.

1. Overview
The Wallet App allows users to view and record their daily income and expense transactions.
The available shops that each transaction can be mapped to, is available to all users.
The available users, and corresponding transactions can only be viewed by support agents and managers.
Only the managers are allowed to make any changes to an existing user, add a transaction record for a user or delete a user.

2. Development Setup
NOTE: The app is based on the database called "wallet". The database must be created before the app is run. If the database is named differently, the name should be updated in the config.py file.

a. **Download the project starter code locally**
```
git clone https://github.com/venice94/Fyurr/tree/master/projects/capstone/starter
```

b. **Create an empty repository in your Github account online. To change the remote repository path in your local repository, use the commands below:**
```
git remote -v 
git remote remove origin 
git remote add origin <https://github.com/<USERNAME>/<REPO_NAME>.git>
git branch -M master
```
Once you have finished editing your code, you can push the local repository to your Github account using the following commands.
```
git add . --all   
git commit -m "your comment"
git push -u origin master
```

c. **Initialize and activate a virtualenv using:**
```
python3 -m virtualenv env
source env/bin/activate
```
>**Note** - In Windows, the `env` does not have a `bin` directory. Therefore, you'd use the analogous command shown below:
```
source env/Scripts/activate
```

d. **Install the dependencies:**
```
pip3 install -r requirements.txt
```

e. **Run the development server:**
```
export FLASK_APP=myapp
export FLASK_ENV=development # enables debug mode
flask run
```

3. API Endpoints
a. Get all users
URL: GET "localhost:5000/users"
Permission required: "get:users"
This API returns an array of existing users in the database.
Sample response:
{
    "success": true,
    "user": [
        {
            "created_date": "Wed, 01 Jan 2020 00:00:00 GMT",
            "id": 1,
            "name": "Test User",
            "status": "Active"
        }
    ]
}

b. Get all shops
URL: GET "localhost:5000/shops"
Permission required: None
This API returns an array of existing shops in the database.
Sample response:
{
    "shop": [
        {
            "address": "123 Studious Street",
            "id": 1,
            "industry": "Retail",
            "name": "ABC Bookstore"
        }
    ],
    "success": true
}

c. Get one user
URL: GET "localhost:5000/users/<user_id>"
Permission required: "get:user"
This API returns the details of the specified user.
Sample response:
{
    "success": true,
    "user": {
        "created_date": "Wed, 01 Jan 2020 00:00:00 GMT",
        "id": 1,
        "name": "Test User",
        "status": "Active"
    }
}

d. Edit user
URL: PATCH "localhost:5000/users/<user_id>"
Permission required: "patch:user"
This API allows the client to edit the user's name and/or status. It returns the user's details after the changes.
Sample response:
{
    "success": true,
    "user": {
        "created_date": "Wed, 01 Jan 2020 00:00:00 GMT",
        "id": 1,
        "name": "Test User",
        "status": "Deleted"
    }
}

e. Get user transactions
URL: GET "localhost:5000/users/<user_id>/transactions"
Permission required: "get:user-transactions"
This API returns an array of transactions made by the specified user.
Sample response:
{
    "success": true,
    "transactions": [
        {
            "amount": 1234.12,
            "category": "Food",
            "date": "Wed, 18 Aug 2021 00:00:00 GMT",
            "description": "dinner",
            "id": 1,
            "shop_id": 1,
            "status": "Active",
            "type": "Expense",
            "user_id": 1
        }
    ],
    "user_id": "1"
}

f. Add user transaction
URL: POST "localhost:5000/users/<user_id>/transactions"
Permission required: "post:user-transactions"
This API allows the client to add a transaction record made by the specified user. It returns the transaction details added.
Sample response:
{
    "success": true,
    "transaction": {
        "amount": 1234.12,
        "category": "Food",
        "date": "Wed, 18 Aug 2021 00:00:00 GMT",
        "description": "dinner",
        "id": 1,
        "shop_id": 1,
        "status": "Active",
        "type": "Expense",
        "user_id": 1
    }
}

g. Delete user
URL: DELETE "localhost:5000/users/<user_id>"
Permission required: "delete:user"
This API allows the client to delete the specified user. It returns the details of the deleted user.
Sample response:
{
    "deleted": {
        "created_date": "Wed, 01 Jan 2020 00:00:00 GMT",
        "id": 1,
        "name": "Test User",
        "status": "Active"
    },
    "success": true
}
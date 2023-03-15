## How to install and run the API

Python3 is required for this project. Before getting into the database, the user needs to activate the virtual environment and install the required packages. Make sure you are in the path /src, and run below commands in terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requirement.txt
```

This API runs on a database called 'marathon_race', so a database and user need to be created first. To create the database, activate PostgreSQL and run the below commands in PostgreSQL:

```sql
CREATE DATABASE marathon_race;
CREATE USER admin WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE marathon_race TO admin;
```

After creating the database and user, exit PostgreSQL and run the below commands in the terminal to initiate and seed the database, and activate the API server.

```bash
flask db init
flask db seed
flask run
```

## Endpoints

------------------------------------------------------------------------------------------

### Participants

<details>
 <summary><code>POST</code> <code><b>/participants/register</b></code> <code>(to register new user and get access token)</code></summary>

#### Required data

The user needs to send below data in a JSON format.

| Name          | Data type | Format                                                  |
| ------------- | --------- | ------------------------------------------------------------ |
| first_name    | string    | must only contain alphabet letters                           |
| last_name     | string    | must only contain alphabet letters                           |
| email         | string    | must be a valid email address                                |
| mobile        | string    | must be a valid Australian mobile number starts with 04      |
| password      | string    | must be at least 8 letters long and have at least 1 uppercase letter |
| date_of_birth | string    | must be in a format of yyyy-MM-dd                            |
| gender        | string    | must be in ['male', 'female']                                |

#### Example payload

```json
{
    "first_name": "Ji",
    "last_name": "Li",
    "email": "test10@test.com",
    "mobile": "0431754134",
    "password": "12345789A",
    "date_of_birth": "2022-11-05",
    "gender": "male"
}
```

#### Responses

- Error: participant already registered. It happens when the user registers with an existing email or mobile number

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Participant already registered</p>
```

- Error: missing information

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Please provide mobile, password</p>
```

- Error: invalid format. Below is an example response when the password doesn't meet the requirement

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>The password must be at least 8 letters long and have at least 1 uppercase letter</p>
```

- Success: returns email, mobile and access token in a JSON format

```json
{
    "msg": "Registered successfully",
    "email": "test2@test.com",
    "mobile": "0431754193",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODg3MTMzNywianRpIjoiYTViNjE"
}
```

</details>

<details>
 <summary><code>POST</code> <code><b>/participants/login</b></code> <code>(for existing user to login and get access token)</code></summary>

#### Required data

The user is required to login with either email or mobile. If both are provided, the API will look for existing user with email first, if none, then it will search with mobile.

| Name          | Data type | Format                                                  |
| ------------- | --------- | ------------------------------------------------------------ |
| email         | string    | must be a valid email address                                |
| mobile        | string    | must be a valid Australian mobile number starts with 04      |
| password      | string    | must be at least 8 letters long and have at least 1 uppercase letter |

#### Example payload

```json
{
    "email": "test@test.com",
    "password": "Password12345678"
}
```
```json
{
    "mobile": "0412345678",
    "password": "Password12345678"
}
```

#### Responses

- Error: mobile and email is not provided

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Please provide email address or mobile to login</p>
```

- Error: password is not provided

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Please provide password</p>
```

- Error: user not found

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>User not found</p>
```

- Error: incorrect password

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Incorrect password</p>
```

- Success: returns email, mobile and access token in a JSON format

```json
{
    "msg": "Login successfully",
    "email": "test2@test.com",
    "mobile": "0431754193",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODg3MTMzNywianRpIjoiYTViNjE"
}
```

</details>

<details>
 <summary><code>GET</code> <code><b>/participants/{int:participant_id}</b></code> <code>(for existing user to access personal details)</code></summary>

#### Required data

JWT authentication is implemented. When the user registers or logs in, they will get a bearer token. To access their personal details, the user needs to send the bearer token with the request. Non-admin users can only access their own personal details, while admin users can access all user's details.

#### Example payload

None

#### Responses

- Error: missing authorization header

```json
{
    "msg": "Missing Authorization Header"
}
```

- Error: token expired

```json
{
    "msg": "Token has expired"
}
```

- Error: invalid token

```json
{
    "msg": "Signature verification failed"
}
```

- Error: invalid user (when a non-admin user is trying to access other user's details)

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: return customer's details

```json
{
    "id": 1,
    "first_name": "Eliud",
    "last_name": "Kipchoge",
    "email": "test@test.com",
    "mobile": "1234567890",
    "date_of_birth": "1984-11-05",
    "gender": "male"
}
```

</details>
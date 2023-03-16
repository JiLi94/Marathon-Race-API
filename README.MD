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

Below responses may apply to all routes that required JWT access token.

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

------------------------------------------------------------------------------------------

### Participants

<details>
 <summary><code>POST</code> <code><b>/participants/register</b></code> <code>(to register new user and get access token)</code></summary>

#### Required data

The user needs to send below data in a JSON format.

| Name          | Required | Data type | Description                                                          |
|---------------|----------|-----------|----------------------------------------------------------------------|
| first_name    | required | string    | must only contain alphabet letters                                   |
| last_name     | required | string    | must only contain alphabet letters                                   |
| email         | required | string    | must be a valid email address                                        |
| mobile        | required | string    | must be a valid Australian mobile number starts with 04              |
| password      | required | string    | must be at least 8 letters long and have at least 1 uppercase letter |
| date_of_birth | required | string    | must be in a format of yyyy-MM-dd                                    |
| gender        | required | string    | must be in ['male', 'female']                                        |

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
    "id": 2,
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

| Name          | Required | Data type | Description                                                          |
|---------------|----------|-----------|----------------------------------------------------------------------|
| email         | optional | string    | must be a valid email address                                        |
| mobile        | optional | string    | must be a valid Australian mobile number starts with 04              |
| password      | required | string    | must be at least 8 letters long and have at least 1 uppercase letter |

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
    "id" : 2,
    "email": "test2@test.com",
    "mobile": "0431754193",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODg3MTMzNywianRpIjoiYTViNjE"
}
```
</details>

<details>
 <summary><code>GET</code> <code><b>/participants/all</b></code> <code>(for admin to check all participants)</code></summary>

#### Required data

Admin user only. JWT authentication is implemented. When the user registers or logs in, they will get a bearer token. To access this route, the admin user needs to send the bearer token with the request. Non-admin user will be rejected.

#### Example payload

None

#### Responses

- Error: invalid user (non-admin user)

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: return all participants' details

```json
[
    {
        "id": 1,
        "first_name": "Eliud",
        "last_name": "Kipchoge",
        "email": "test@test.com",
        "mobile": "0412345678",
        "date_of_birth": "1984-11-05",
        "gender": "male"
    },
    {
        "id": 2,
        "first_name": "Ji",
        "last_name": "Li",
        "email": "test10@test.com",
        "mobile": "0431754134",
        "date_of_birth": "2022-11-05",
        "gender": "male"
    }
]
```

</details>

<details>
 <summary><code>GET</code> <code><b>/participants/{int:participant_id}</b></code> <code>(for existing user to access personal details)</code></summary>

#### Required data

JWT access token required. Non-admin users can only access their own personal details, while admin users can access all user's details.

#### Example payload

None

#### Responses

- Error: invalid user (when a non-admin user is trying to access other user's details)

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: return participant's details

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

<details>
 <summary><code>PUT</code> <code><b>/participants/{int:participant_id}</b></code> <code>(for user to update personal details)</code></summary>

#### Required data

JWT access token required. Non-admin users can only update their own personal details, while admin users can update all user's details.

To update any field of the personal details, the user needs to send the updated data in the body of the request in a JSON format.

| Name          | Required | Data type | Description                                                          |
|---------------|----------|-----------|----------------------------------------------------------------------|
| first_name    | optional | string    | must only contain alphabet letters                                   |
| last_name     | optional | string    | must only contain alphabet letters                                   |
| email         | optional | string    | must be a valid email address                                        |
| mobile        | optional | string    | must be a valid Australian mobile number starts with 04              |
| password      | optional | string    | must be at least 8 letters long and have at least 1 uppercase letter |
| date_of_birth | optional | string    | must be in a format of yyyy-MM-dd                                    |
| gender        | optional | string    | must be in ['male', 'female']                                        |


#### Example payload

```json
    {
        "first_name": "Ji",
        "email": "test10@test.com",
    }
```

#### Responses

- Error: user not found with specific id

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Participant not found</p>
```

- Error: invalid user (when a non-admin user is trying to update other user's details)

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: return successful message and updated details

```json
{
    "msg": "Updated successfully",
    "Updated": {
        "id": 2,
        "first_name": "Ji",
        "last_name": "Li",
        "email": "test10@test.com",
        "mobile": "0431754134",
        "date_of_birth": "2022-11-05",
        "gender": "male"
    }
}
```

</details>

<details>
 <summary><code>DELETE</code> <code><b>/participants/{int:participant_id}</b></code> <code>(for admin user to delete a specific participant)</code></summary>

#### Required data

Admin user only. JWT access token required.

#### Example payload

None

#### Responses

- Error: user not found with specific id

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Participant not found</p>
```

- Error: invalid user (when a non-admin user is trying to delete)

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: when there is registrations linked with the participant, need to delete the registrations first

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Please delete the registrations linked with this participant before deleting this participant</p>
```

- Success: return delete successful message

```json
{
    "msg": "Participant deleted successfully",
    "result": {
        "id": 1,
        "first_name": "Eliud",
        "last_name": "Kipchoge",
        "email": "test@test.com",
        "mobile": "0412345678",
        "date_of_birth": "1984-11-05",
        "gender": "male"
    }
}
```

</details>

<details>
 <summary><code>GET</code> <code><b>/participants/{int:participant_id}/registrations</b></code> <code>(for user to check their existing registrations)</code></summary>

#### Required data

JWT access token required. Non-admin users can only check their own registrations, while admin users can access all participants' registrations.

#### Example payload

None

#### Responses

- Error: user not found with specific id

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Participant not found</p>
```

- Error: invalid user (when a non-admin user is trying to update other user's details)

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: return all registrations under the participant

```json
{
    "participant": {
        "first_name": "Eliud",
        "last_name": "Kipchoge"
    },
    "registrations": [
        {
            "race": "Berlin Marathon",
            "age_group": {
                "min_age": 20,
                "max_age": 39
            },
            "gender_group": "male",
            "registration_date": "2022-09-25",
            "bib_number": "A1234"
        }
    ]
}
```

</details>

------------------------------------------------------------------------------------------

### Age groups

<details>
 <summary><code>GET</code> <code><b>/age_groups</b></code> <code>(to view all age groups)</code></summary>

#### Required data

None

#### Example payload

None

#### Responses

- Success: returns all age groups, example response:

```json
[
    {
        "id": 1,
        "min_age": 0,
        "max_age": 17
    },
    {
        "id": 2,
        "min_age": 18,
        "max_age": 19
    }
]
```

</details>

------------------------------------------------------------------------------------------

### Races

<details>
 <summary><code>GET</code> <code><b>/races</b></code> <code>(to view all races)</code></summary>

#### Required data

None

#### Example payload

None

#### Responses

- Success: returns all races, example response:

```json
[
    {
        "id": 1,
        "name": "Melbourne Marathon",
        "distance": "2.13",
        "date": "2022-09-25",
        "start_time": "07:00:00",
        "cut_off_time": "14:00:00",
        "field_limit": 9000,
        "start_line": "Batman Avenue (150m North of Rod Laver Arena)",
        "finish_line": "Melbourne Cricket Ground (MCG)",
        "fee": "160.01"
    }
]
```

</details>

<details>
 <summary><code>GET</code> <code><b>/races/{int:race_id}</b></code> <code>(to view a single race)</code></summary>

#### Required data

None

#### Example payload

None

#### Responses

- Success: returns single race corresponding to the race_id

```json
[
    {
        "id": 1,
        "name": "Melbourne Marathon",
        "distance": "2.13",
        "date": "2022-09-25",
        "start_time": "07:00:00",
        "cut_off_time": "14:00:00",
        "field_limit": 9000,
        "start_line": "Batman Avenue (150m North of Rod Laver Arena)",
        "finish_line": "Melbourne Cricket Ground (MCG)",
        "fee": "160.01"
    }
]
```

</details>

<details>
 <summary><code>POST</code> <code><b>/races</b></code> <code>(to add a race, admin only)</code></summary>

#### Required data

JWT access token required. Admin user only. Below is the required data.

| Name         | Required | Data type | Description                                                |
|--------------|----------|-----------|------------------------------------------------------------|
| name         | required | string    | Name of the race                                           |
| distance     | required | float     | must be a number larger than 0                             |
| date         | required | string    | must be in a format of yyyy-MM-dd                          |
| start_time   | required | string    | must be in a format of HH:MM:SS                            |
| cut_off_time | required | string    | must be in a format of HH:MM:SS and larger than start_time |
| field_limit  | required | int       | must be a int larger than 0                                |
| start_line   | required | string    | start point of the race                                    |
| finish_line  | required | string    | end point of the race                                      |
| fee          | required | float     | must be a number larger than 0                             |

#### Example payload

```json
{
    "name": "Melbourne Marathon",
    "distance": 21.1,
    "date": "2022-09-25",
    "start_time": "07:00:00",
    "cut_off_time": "12:00:00",
    "field_limit": 6000,
    "start_line": "Batman Avenue (150m North of Rod Laver Arena)",
    "finish_line": "Melbourne Cricket Ground (MCG)",
    "fee": 160.01
}
```

#### Responses

- Error: required field missing

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Please provide finish_line, fee</p>
```

- Error: incorrect format of provided field, example:

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Cut off time cannot be earlier than start time</p>
```

- Error: race already exists. The combination of name and date must be unique.

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Race already exists!</p>
```

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: returns successful message with race detail

```json
{
    "msg": "Race added successfully",
    "race": {
        "id": 10,
        "name": "Melbourne Marathon",
        "distance": 21.1,
        "date": "2022-09-25",
        "start_time": "07:00:00",
        "cut_off_time": "12:00:00",
        "field_limit": 6000,
        "start_line": "Batman Avenue (150m North of Rod Laver Arena)",
        "finish_line": "Melbourne Cricket Ground (MCG)",
        "fee": 160.01
    }
}
```

</details>

<details>
 <summary><code>PUT</code> <code><b>/races/{int:race_id}</b></code> <code>(to update a race, admin only)</code></summary>

#### Required data

JWT access token required. Admin user only. User needs to send the updated field in the body.

| Name         | Required | Data type | Description                                                |
|--------------|----------|-----------|------------------------------------------------------------|
| name         | optional | string    | Name of the race                                           |
| distance     | optional | float     | must be a number larger than 0                             |
| date         | optional | string    | must be in a format of yyyy-MM-dd                          |
| start_time   | optional | string    | must be in a format of HH:MM:SS                            |
| cut_off_time | optional | string    | must be in a format of HH:MM:SS and larger than start_time |
| field_limit  | optional | int       | must be a int larger than 0                                |
| start_line   | optional | string    | start point of the race                                    |
| finish_line  | optional | string    | end point of the race                                      |
| fee          | optional | float     | must be a number larger than 0                             |

#### Example payload

```json
{
    "name": "Melbourne Marathon",
    "distance": 21.1,
    "date": "2022-09-25",
    "start_time": "07:00:00",
    "cut_off_time": "12:00:00",
    "field_limit": 6000,
    "start_line": "Batman Avenue (150m North of Rod Laver Arena)",
    "finish_line": "Melbourne Cricket Ground (MCG)",
    "fee": 160.01
}
```

#### Responses

- Error: incorrect format of provided field, example:

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Cut off time cannot be earlier than start time</p>
```

- Error: race already exists. The combination of name and date must be unique.

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Race already exists!</p>
```

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: returns update successful message with race detail

```json
{
    "msg": "Updated successfully",
    "race": {
        "id": 10,
        "name": "Melbourne Marathon",
        "distance": 21.1,
        "date": "2022-09-25",
        "start_time": "07:00:00",
        "cut_off_time": "12:00:00",
        "field_limit": 6000,
        "start_line": "Batman Avenue (150m North of Rod Laver Arena)",
        "finish_line": "Melbourne Cricket Ground (MCG)",
        "fee": 160.01
    }
}
```

</details>

</details>

<details>
 <summary><code>DELETE</code> <code><b>/races/{int:race_id}</b></code> <code>(to delete a race, admin only)</code></summary>

#### Required data

JWT access token required. Admin user only. 

#### Example payload

None

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: race not found with specific id

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Race not found</p>
```
- Error:  when there are registrations linked with the race, need to delete the registrations first
```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Please delete the registrations linked with this race before deleting this race</p>
```

- Success: returns delete successful message with race detail

```json
{
    "msg": "Race deleted successfully",
    "race": {
        "id": 1,
        "name": "Berlin Marathon",
        "distance": "2.13",
        "date": "2022-09-25",
        "start_time": "07:00:00",
        "cut_off_time": "09:00:00",
        "field_limit": 9000,
        "start_line": "Batman Avenue (150m North of Rod Laver Arena)",
        "finish_line": "Melbourne Cricket Ground (MCG)",
        "fee": "160.01"
    }
}
```

</details>

------------------------------------------------------------------------------------------

### Registrations

<details>
 <summary><code>GET</code> <code><b>/registrations</b></code> <code>(to view all registrations, admin only)</code></summary>

#### Required data

JWT access token required. Admin user only.

#### Example payload

None

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Success: returns all existing registrations

```json
[
    {
        "participant": {
            "first_name": "Eliud",
            "last_name": "Kipchoge"
        },
        "race": "Berlin Marathon",
        "age_group": {
            "min_age": 20,
            "max_age": 39
        },
        "gender_group": "male",
        "registration_date": "2022-09-25",
        "bib_number": "A1234"
    }
]
```

</details>

<details>
 <summary><code>POST</code> <code><b>/registrations</b></code> <code>(to add a registration, admin only)</code></summary>

#### Required data

JWT access token required. Admin user only. User needs to input all required fields below. The age group will be determined by the program automatically based on participant's date_of_birth, so it shouldn't be passed here.

| Name             | Required | Data type | Description                                                |
|------------------|----------|-----------|------------------------------------------------------------|
| participant_id   | required | int       | must be the id of an existing participant                  |
| race_id          | required | int       | must be the id of an existing race                         |
| registration_date| required | string    | must be in a format of yyyy-MM-dd                          |
| bib_number       | required | string    | unique combination of alphabet letters and numbers for each registration|

#### Example payload

```json
{
    "participant_id": 1,
    "race_id": 1,
    "registration_date": "2022-09-25",
    "bib_number": "A12345"
}
```

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: participant already registered

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Participant already registered this race</p>
```

- Error: bib number exists
```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Bib number already exists under this race</p>
```

- Error: participant not found
```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Participant not found</p>
```

- Error: race not found
```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Race not found</p>
```

- Success: returns successful message and registration details

```json
{
    "msg": "Registration added successfully",
    "registration": {
        "id": 8,
        "participant": {
            "first_name": "Ji",
            "last_name": "Li",
            "gender": "male"
        },
        "race": "Berlin Marathon",
        "age_group": {
            "min_age": 0,
            "max_age": 17
        },
        "registration_date": "2022-09-25",
        "bib_number": "A123456"
    }
}
```

</details>

<details>
 <summary><code>PUT</code> <code><b>/registrations/{int:registration_id}</b></code> <code>(to update a registration, admin only)</code></summary>

#### Required data

JWT access token required. Admin user only. User can pass any updated fields in the body.

| Name             | Required | Data type | Description                                                |
|------------------|----------|-----------|------------------------------------------------------------|
| participant_id   | optional | int       | must be the id of an existing participant                  |
| race_id          | optional | int       | must be the id of an existing race                         |
| registration_date| optional | string    | must be in a format of yyyy-MM-dd                          |
| bib_number       | optional | string    | unique combination of alphabet letters and numbers for each registration|

#### Example payload

```json
{
    "participant_id": 1,
    "race_id": 1,
    "registration_date": "2022-09-25",
    "bib_number": "A12345"
}
```

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: participant already registered

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Participant already registered this race</p>
```

- Error: bib number exists
```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Bib number already exists under this race</p>
```

- Error: participant not found
```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Participant not found</p>
```

- Error: race not found
```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Race not found</p>
```

- Success: returns successful message and registration details

```json
{
    "msg": "Updated successfully",
    "registration": {
        "id": 8,
        "participant": {
            "first_name": "Ji",
            "last_name": "Li",
            "gender": "male"
        },
        "race": "Berlin Marathon",
        "age_group": {
            "min_age": 0,
            "max_age": 17
        },
        "registration_date": "2022-09-25",
        "bib_number": "A12346"
    }
}
```

</details>

<details>
 <summary><code>DELETE</code> <code><b>/registrations/{int:registration_id}</b></code> <code>(to delete a registration, admin only)</code></summary>

#### Required data

JWT access token required. Admin user only.

#### Example payload

None

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: registration not found

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Registration not found</p>
```

- Error: when there is a result linked with the registration, need to delete the result first
```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Please delete the result linked with this registration before deleting this registration</p>
```

- Success: returns successful message and registration details

```json
{
    "msg": "Registration deleted successfully",
    "result": {
        "id": 1,
        "participant": {
            "first_name": "Eliud",
            "last_name": "Kipchoge",
            "gender": "male"
        },
        "race": "Berlin Marathon",
        "age_group": {
            "min_age": 20,
            "max_age": 39
        },
        "registration_date": "2022-09-25",
        "bib_number": "A1234"
    }
}
```

</details>

------------------------------------------------------------------------------------------

### Results

<details>
 <summary><code>GET</code> <code><b>/results</b></code> <code>(to view results based on race, age group and gender)</code></summary>

#### Required data

Query parameters are utilised in this route. User can pass race_id, age_group_id and gender to view results based on these criteria. If any of these parameters are not passed, it will be considered to view all results under the category,

| Name             | Required | Data type | Description                                                |
|------------------|----------|-----------|------------------------------------------------------------|
| race_id          | optional | int       | must be the id of an existing race                         |
| age_group_id     | optional | int       | must be the id of an existing age_group                    |
| gender           | optional | string    | must be in ['male', 'female']                              |

For example, the query strings can be like: [/results/?race_id=1&age_group_id=1&gender=male](/results/?race_id=1&age_group_id=1&gender=male)

#### Example payload

None

#### Responses

- Error: race/age_group not found

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Race not found</p>
```

- Success: returns all existing results in a ascending order of finish_time

```json
{
    "race": "Berlin Marathon",
    "age_group": {
        "min_age": "All",
        "max_age": "All"
    },
    "gender": "male",
    "results": [
        {
            "place": 1,
            "first_name": "Eliud",
            "last_name": "Kipchoge",
            "finished": true,
            "start_at": "07:00:00",
            "finish_at": "09:00:00",
            "finish_time": "02:00:00",
            "pace": "00:02:50"
        },
        {
            "place": 2,
            "first_name": "Ji",
            "last_name": "Li",
            "finished": true,
            "start_at": "07:00:00",
            "finish_at": "11:00:00",
            "finish_time": "04:00:00",
            "pace": "00:05:41"
        }
    ]
}
```

</details>

<details>
 <summary><code>POST</code> <code><b>/results</b></code> <code>(to add a result, admin only)</code></summary>

#### Required data

JWT access token required, and admin user only. Users are required to pass the below data in the request body. The finish time and pace will be calculated automatically by the program, so they are not required.

| Name             | Required | Data type | Description                                                |
|------------------|----------|-----------|------------------------------------------------------------|
| registration_id  | required | int       | must be the id of an existing registration                 |
| finished         | required | boolean   | must be either true or false                               |
| start_at         | required | string    | must be in the format of '%H:%M:%S                         |
| finish_at        | required | string    | must be in the format of '%H:%M:%S                         |

#### Example payload

```json
{
    "registration_id": 9,
    "finished": true,
    "start_at": "07:00:00",
    "finish_at": "9:00:00"
}
```

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: registration not found

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Registration not found</p>
```

- Error: registration already has a result

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Result with same registration id already exists</p>
```

- Success: returns successful message and result details

```json
{
    "description": "Added successfully",
    "result": {
        "participant": {
            "first_name": "Eliud",
            "last_name": "Kipchoge"
        },
        "id": 13,
        "registration_id": 9,
        "finished": true,
        "start_at": "07:00:00",
        "finish_at": "09:00:00",
        "finish_time": "02:00:00",
        "pace": "00:02:50"
    }
}
```

</details>

<details>
 <summary><code>PUT</code> <code><b>/results/{int:result_id}</b></code> <code>(to update a result, admin only)</code></summary>

#### Required data

JWT access token required, and admin user only. Users can pass any updated fields in the request body.

| Name             | Required | Data type | Description                                                |
|------------------|----------|-----------|------------------------------------------------------------|
| registration_id  | optional | int       | must be the id of an existing registration                 |
| finished         | optional | boolean   | must be either true or false                               |
| start_at         | optional | string    | must be in the format of '%H:%M:%S                         |
| finish_at        | optional | string    | must be in the format of '%H:%M:%S                         |

#### Example payload

```json
{
    "registration_id": 9,
    "finished": true,
    "start_at": "07:00:00",
    "finish_at": "9:00:00"
}
```

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: registration not found

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Registration not found</p>
```

- Error: registration already has a result

```html
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Result with same registration id already exists</p>
```

- Success: returns successful message and result details

```json
{
    "msg": "Updated successfully",
    "result": {
        "participant": {
            "first_name": "Eliud",
            "last_name": "Kipchoge"
        },
        "id": 10,
        "registration_id": 9,
        "finished": true,
        "start_at": "07:00:00",
        "finish_at": "10:00:00",
        "finish_time": "3:00:00",
        "pace": "00:04:15"
    }
}
```

</details>


<details>
 <summary><code>DELETE</code> <code><b>/results/{int:result_id}</b></code> <code>(to delete a result, admin only)</code></summary>

#### Required data

JWT access token required, and admin user only.

#### Example payload

None

#### Responses

- Error: non-admin user

```html
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Invalid User</p>
```

- Error: result not found

```html
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>Result not found</p>
```

- Success: returns successful message and result details

```json
{
    "msg": "Result deleted successfully",
    "result": {
        "participant": {
            "first_name": "Eliud",
            "last_name": "Kipchoge"
        },
        "id": 13,
        "registration_id": 9,
        "finished": true,
        "start_at": "07:00:00",
        "finish_at": "09:00:00",
        "finish_time": "02:00:00",
        "pace": "00:02:50"
    }
}
```

</details>
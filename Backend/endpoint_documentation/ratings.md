# Ratings API


This document covers the v1 backend task ratings endpoints for ClubIQ.


## Base URL


```text

/api/v1/ratings

```


## Auth


All endpoints require a valid Clerk session token.


```http

Authorization: Bearer <Clerk session token>

Content-Type: application/json

```


The backend verifies the Clerk token and loads the synced local user.


If the Clerk user is authenticated but not synced in the local DB, the request fails with `403`.


## v1 Notes


Ratings remain exposed in v1.


Unlike activities and members, ratings still use task and user identifiers directly:


```text

/api/v1/ratings/<task_id>/

/api/v1/ratings/<rating_id>

/api/v1/ratings/user/<user_id>/

```


## Roles


| Role           | Access                                |

| -------------- | ------------------------------------- |

| `admin`        | Full access                           |

| `super_user`   | Full access                           |

| `club_manager` | Can list ratings for a task           |

| regular user   | Can fetch their own user ratings only |


## Endpoints at a Glance


| # | Method | Endpoint                          | Description                          | Roles                                 |

| - | ------ | --------------------------------- | ------------------------------------ | ------------------------------------- |

| 1 | GET    | `/api/v1/ratings/<task_id>/`      | List ratings for a task              | `admin`, `super_user`, `club_manager` |

| 2 | POST   | `/api/v1/ratings/<task_id>/`      | Create a rating for a completed task | `admin`, `super_user`                 |

| 3 | GET    | `/api/v1/ratings/user/<user_id>/` | List ratings received by a user      | `admin`, `super_user`, or same user   |

| 4 | DELETE | `/api/v1/ratings/<rating_id>`     | Delete a rating                      | `admin`, `super_user`                 |


## Query Params


List endpoints support pagination and date filtering.


| Query Param | Type         | Required | Notes                                            |

| ----------- | ------------ | -------- | ------------------------------------------------ |

| `limit`     | integer      | No       | Page size. Default `10`, max `100`.              |

| `page`      | integer      | No       | 1-based page number. Default `1`.                |

| `from`      | ISO datetime | No       | Include ratings created at or after this value.  |

| `to`        | ISO datetime | No       | Include ratings created at or before this value. |


Invalid pagination values fall back to defaults.


Invalid date filters are ignored.


## 1. List Ratings for a Task


```http

GET /api/v1/ratings/<task_id>/

```


### Purpose


Returns ratings attached to a specific task.


### Request Headers


```http

Authorization: Bearer <Clerk session token>

```


### Roles


```text

admin

super_user

club_manager

```


### Example Request


```http

GET /api/v1/ratings/0f4c90f7-4d6f-46d6-8df7-6b0a8d1a5e14/?page=1&limit=10

Authorization: Bearer <token>

```


### Success Response


Status:


```text

200 OK

```


Body:


```json

{

  "success": true,

  "data": [

    {

      "id": "87c6b7ef-d6bc-4d07-8b5d-2078170c4c9a",

      "task_id": "0f4c90f7-4d6f-46d6-8df7-6b0a8d1a5e14",

      "rated_user": 5,

      "rated_by": 1,

      "score": 4,

      "comments": "Well done",

      "created_at": "2026-01-01T12:00:00"

    }

  ],

  "average_score": 4.0,

  "pagination": {

    "page": 1,

    "limit": 10,

    "total": 1

  }

}

```


### Common Errors


| Status | Meaning                                    |

| ------ | ------------------------------------------ |

| 401    | Authorization token missing or invalid     |

| 403    | User is not synced or role is insufficient |

| 404    | Task id is invalid or task was not found   |

| 500    | Unexpected server error                    |


## 2. Create Rating for a Task


```http

POST /api/v1/ratings/<task_id>/

```


### Purpose


Creates a rating for a completed task.


### Request Headers


```http

Authorization: Bearer <Clerk session token>

Content-Type: application/json

```


### Roles


```text

admin

super_user

```


### Request Body


```json

{

  "score": 5,

  "rated_user": 5,

  "comments": "Great execution"

}

```


### Required Fields


| Field        | Type    | Required | Notes                                     |

| ------------ | ------- | -------- | ----------------------------------------- |

| `score`      | integer | Yes      | Rating score                              |

| `rated_user` | integer | Yes      | Local synced user id receiving the rating |

| `comments`   | string  | No       | Optional rating comments                  |


### Important Rules


* `task_id` must be a valid UUID for an existing task.

* The task must be completed.

* `rated_user` must exist.

* A rater can rate a task only once.

* Duplicate rating attempts return `400`.


### Success Response


Status:


```text

201 Created

```


Body:


```json

{

  "success": true,

  "message": "Rating created successfully",

  "data": {

    "rating_id": "5c2fd7ef-4b82-4e77-a2dd-dfd606c640fd",

    "task_id": "0f4c90f7-4d6f-46d6-8df7-6b0a8d1a5e14",

    "rated_user": 5,

    "score": 5

  }

}

```


### Common Errors


| Status | Meaning                                                               |

| ------ | --------------------------------------------------------------------- |

| 400    | Invalid task id, missing fields, incomplete task, or duplicate rating |

| 401    | Authorization token missing or invalid                                |

| 403    | User is not synced or role is insufficient                            |

| 404    | Task or rated user was not found                                      |

| 409    | Database constraint issue                                             |

| 500    | Unexpected server error                                               |


## 3. List Ratings for a User


```http

GET /api/v1/ratings/user/<user_id>/

```


### Purpose


Returns ratings received by a specific user.


### Request Headers


```http

Authorization: Bearer <Clerk session token>

```


### Roles


Allowed callers:


```text

- admin

- super_user

- the same user as <user_id>

```


### Example Request


```http

GET /api/v1/ratings/user/5/?page=1&limit=20

Authorization: Bearer <token>

```


### Success Response


Status:


```text

200 OK

```


Body:


```json

{

  "success": true,

  "data": [

    {

      "id": "87c6b7ef-d6bc-4d07-8b5d-2078170c4c9a",

      "task_id": "0f4c90f7-4d6f-46d6-8df7-6b0a8d1a5e14",

      "score": 4,

      "comments": "Well done",

      "rated_by": 1,

      "created_at": "2026-01-01T12:00:00"

    }

  ],

  "average_score": 4.0,

  "pagination": {

    "page": 1,

    "limit": 20,

    "total": 1

  }

}

```


### Common Errors


| Status | Meaning                                                      |

| ------ | ------------------------------------------------------------ |

| 401    | Authorization token missing or invalid                       |

| 403    | User is not synced or caller cannot view this user's ratings |

| 500    | Unexpected server error                                      |


## 4. Delete Rating


```http

DELETE /api/v1/ratings/<rating_id>

```


### Purpose


Deletes a rating.


### Request Headers


```http

Authorization: Bearer <Clerk session token>

```


### Roles


```text

admin

super_user

```


### Success Response


Status:


```text

200 OK

```


Body:


```json

{

  "success": true,

  "message": "Rating deleted successfully"

}

```


### Common Errors


| Status | Meaning                                      |

| ------ | -------------------------------------------- |

| 401    | Authorization token missing or invalid       |

| 403    | User is not synced or role is insufficient   |

| 404    | Rating id is invalid or rating was not found |

| 409    | Database constraint issue                    |

| 500    | Unexpected server error                      |


## Frontend Example: List Task Ratings


```typescript

const token = await getToken();


const response = await fetch(

  "http://127.0.0.1:5000/api/v1/ratings/0f4c90f7-4d6f-46d6-8df7-6b0a8d1a5e14/?page=1&limit=10",

  {

    method: "GET",

    headers: {

      Authorization: `Bearer ${token}`,

      "Content-Type": "application/json",

    },

  },

);


const data = await response.json();

console.log(data);

```


## Status Codes Quick Reference


| Status | Meaning                                              |

| ------ | ---------------------------------------------------- |

| 200    | Ratings returned or rating deleted                   |

| 201    | Rating created successfully                          |

| 400    | Bad request body or invalid task state               |

| 401    | Missing or invalid auth token                        |

| 403    | Authenticated but not synced or role is insufficient |

| 404    | Task, user, or rating not found                      |

| 409    | Database constraint issue                            |

| 500    | Server error                                         |

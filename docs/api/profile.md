# profile
### GET */auth/v1/profile/*
get profile
#### access - *authorized*
[response](../models/user.md#user)

### PUT/PATCH */auth/v1/profile/*
update profile
#### access - *authorized*
request type can be application/json or multipart/form (to upload photo)
[request fields](../models/user.md#editable-fields)  
[response](../models/user.md#user)

### GET */auth/v1/profile/categories/*
Get user favorite categories
#### access - *authorized*
[response model](../models/category.md#list-of-categories)


### POST */auth/v1/profile/categories/*
Add a category to user favorite
#### access - *authorized*
#### request body:
```json5
{
  categories: [1, 2, 3] // List of category ids
}
```
response status code 200

### DELETE */user/v1/profile/*
delete profile
#### access - *authorized*
response status code 204

### POST */auth/v1/profile/password/*
update password
#### access - *authorized*
request
```json5
{
	"old_password": "str",
	"new_password": "str"
}
```
response status code 200

### POST */auth/v1/profile/recovery/*
update password
#### access - *public*
request
```json5
{
	"token": "str", // firebase token
	"password": "str"
}
```
response
```json5
{
  "access": "str",
  "refresh": "str",
  "user": "user"
}
```
[user](../models/user.md#user)


### GET */auth/v1/users/1/*
get user info by id
#### access - **public**
response
[user](../models/user.md#public-user)
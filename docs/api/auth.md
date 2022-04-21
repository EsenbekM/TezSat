# auth
### POST */auth/v1/signup/*
signup with firebase phone/email
#### access - *public*
request
```json5
{
  "token": "str",      // required, firebase access token
  "password": "str",   // required
  "name": "str"        // required
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
### POST */auth/v1/login/*
login with email/phone and password
#### access - *public*
request
```json5
{
  "login": "str",     // required, email or phone
  "password": "str"   // required
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

### POST */auth/v1/social_login/*
login with google
#### access - *public*
request
```json5
{
  "token": "str",      // required, firebase access token
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
### POST */auth/v1/refresh/*
refresh access token
#### access - **public**
```json5
{
  "refresh": "str",   // required
}
```
response
```json5
{
  "access": "str"
}
```

### POST */auth/v1/login_availability/*
check existence of phone or email
#### access - **public**
request
```json5
{
	"login": "str"  // phone or email
}
```
response if login available status code 200 otherwise 400


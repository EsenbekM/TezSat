# Business API

### GET */business/v1/businesses/*
list of businesses
#### access - *public*
filters:
* ?category=1    

you can request multiple ordering fields:
* ?ordering=(-)rating
* ?ordering=(-)creation_date

search by name and description:
* ?search=q

paginated [response model](../models/business.md#short-business)

### GET */business/v1/businesses/{id}*
Retrieve business by id
#### access - *public*
[response model](../models/business.md#business)


### GET */business/v1/profile/*
Retrieve own business account
#### access - *authorized - business*
[response model](../models/business.md#business)

### PATCH/PUT */business/v1/profile/*
update business account
#### access - *authorized - business*
request
```json5
{
	"contacts": [
		{
			"type": "str", // phone, email, website, facebook, instagram, whatsapp, telegram, address
			"value": "str"
		}
	],
	"schedule": [
		{
			"weekday": "str", // monday, tuesday, wednesday, thursday, friday, saturday, sunday
			"time": "str"
		}
	],
	"name": "str",
	"description": "str",
	"category": "int",
    "banner": "bytes", // you can upload banner using content-type: multipart/form-data
}
```
[response model](../models/business.md#business)

## Branches
### access - *authorized - business*

### POST */business/v1/profile/branches/*
Create branch

body: 
```json5
[
  {
    "lat": "str", // Latitude
    "lng": "str", // Longitude
    "address": "str" // Address of the branch
  }
]
```
### DELETE */business/v1/profile/branches/{id}/*
Delete branch

### PATCH/PUT */business/v1/profile/branches/{id}/*
Update branch

body: 
```json5
{
  "lat": "str", // Latitude
  "lng": "str", // Longitude
  "address": "str" // Address of the branch
}
```

## Contacts
### access - *authorized - business*

### POST */business/v1/profile/contacts/*
Create contact

body: 
```json5
[ 
  {
    "type": "str", // One of predefined values
    "value": "str" 
  }
]
```
### DELETE */business/v1/profile/contacts/{id}/*
Delete contact

### PATCH/PUT */business/v1/profile/contacts/{id}/*
Update branch

body: 
```json5
{
  "type": "str", // One of predefined values
  "value ": "str" 
}
```

## Schedule
### access - *authorized - business*

### POST */business/v1/profile/schedule/*
Create schedule

body: 
```json5
[
  {
    "weekday": "str", // One of predefined values
    "time": "str" // Time can be specified  with - or what ever used desires
  },
]
```
### DELETE */business/v1/profile/schedule/{id}/*
Delete schedule

### PATCH/PUT */business/v1/profile/schedule/{id}/*
Update schedule

body: 
```json5
{
  "weekday": "str", // One of predefined values
  "time": "str" // Time can be specified  with - or what ever used desires
}
```

### POST */business/v1/profile/deactivate/*
deactivate business account
#### access - *authorized - business*
request
```json5
{
  "message": "str"
}
```
response status code 204

### POST */business/v1/requests/*
request a business account
### access - *authorized*
request
```json5
{
  "name": "str",
  "message": "str",
  "category": "int"
}
```
response
```json5
{
  "id": "int",
  "name": "str",
  "message": "str",
  "category": "int"
}
```




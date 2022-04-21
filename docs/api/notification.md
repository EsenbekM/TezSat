### GET */notification/v1/notifications/*
list of user's notifications
#### access - *authorized*

[response](#notification)

### GET */notification/v1/notifications/unread_count/*
count of unread notifications
#### access - *authorized*
response
```json5
{
  "unread_count": "int"
}
```
### POST */notification/v1/notifications/read_all/*
read all notifications
#### access - *authorized*


### PATCH */notification/v1/notifications/{id}*
read notification
#### access - *authorized*
request 
```json5
{
	"is_read": "bool"
}
```
[response](#notification)


#### notification
```json5
{
  "id": "id",
  "sender": "user",   // nullable
  "receiver": "user",
  "action": "str",    // stared or activated
  "product": {
        "id": "int",
        "user": "int",
        "title": "str",
        "price_kgs": "str",
        "price_usd": "str",
        "show_count": "int",
        "view_count": "int",
        "state": "str",
        "favorite_count": "int",
        "photos": []
  },
  "creation_date": "str",
  "is_read": "bool"
}
```
[user](../models/user.md#public-user)


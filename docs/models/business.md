## short business
```json5
{
  "id": "int",
  "user": "user",
  "name": "str",
  "description": "str", // nullable
  "creation_date": "str", // timestamp
  "banner": "str",  // url, nullable
  "category": "int",
  "rating": "int", // nullable
  "product_count": "int"
}
```
[user](user.md#public-user)

## business
```json5
{
  "id": "int",
  "user": "user",
  "name": "str",
  "description": "str",
  "creation_date": "str", // timestamp
  "banner": "str", // url
  "category": "int",
  "contacts": [
    {
      "id": "int",
      "business": "int",
      "type": "str", // phone, email, website, facebook, instagram, whatsapp, telegram
      "value": "str"
    }
  ],
  "schedule": [
    {
      "id": "int",
      "business": "int",
      "weekday": "str", // monday, tuesday, wednesday, thursday, friday, saturday, sunday
      "time": "str"
    }
  ],
  "rating": "int", // nullable
  "product_count": "int",
  "product_limit": "int", // nullable
}
```
[user](user.md#public-user)
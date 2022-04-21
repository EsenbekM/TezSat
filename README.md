# TezSat docs 

Latest update presented in [changelog.md](./changelog.md)

## Authorization
You will be given access and refresh tokens  
You have to submit access token from [login](docs/api/auth.md#post-authv1login) or registration in headers of request   
```Authorization: Bearer <access token>```   
access token lives short time, but can be refreshed by refresh token   
to refresh access token use [this api](docs/api/auth.md#post-authv1refresh)

## Pagination
to control pagination use query params
```
?limit=100&offset=400
```
paginated response will look like
```json5
{
  "count": "int",            // count of all elements
  "next": "str or null",     // url for next "page"   
  "previous": "str or null", // url for previous "page"   
  "results":[]               // data
}
```

## Deep Link
Authorization with email
```
https://tezsat.kg/link/mail_auth?
```
Share product
```
https://tezsat.kg/link/share?product_id=1
```

## Push notification data
```json5
{
  "data": {
    "title": "str",
    "message": "str",
    "buyer": "str", // user id, field available only in chat notification
    "seller": "str", // user id, field available only in chat notification
    "product": "str", // product id, field available only in chat notification
  },
  "token": "str", // fcm_id
  "notification": {
    "title": "str",
    "message": "str",
  },
  "apns": {
    "payload": {
      "apns": {
        "sound": "default"
      }   
    }
  }
}
```
## API
- [auth api](docs/api/auth.md)   
- [profile api](docs/api/profile.md)
- [location api](docs/api/location.md)
- [category api](docs/api/category.md)
- [product api](docs/api/product.md)
- [chat api](docs/api/chat.md)
- [notification api](docs/api/notification.md)
- [business api](docs/api/business.md)
- [review api](docs/api/review.md)
- [info api](docs/api/info.md)

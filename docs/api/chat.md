### POST */chat/v1/send_message/*
send message to product's user
#### access - *authorized*
request
```json5
{
  "user": "int",
  "product": "int",
  "message": "str"
}
```
response status code 200

### POST */chat/v1/upload_photo/*
upload photo to chat
#### access - *authorized*
request   
Content-Type - multipart/form-data
```json5
{
  "user": "int",
  "product": "int",
  "photo": "bytes"
}
```
response
```json5
{
  "id": "int",
  "chat": "int",
  "photo": "str" // full url
}
```

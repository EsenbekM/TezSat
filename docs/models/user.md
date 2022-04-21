## user
```json5
{
  "id": "int",            
  "name": "str",        // nullable  
  "phone": "str",       // nullable
  "email": "str",       // nullable
  "photo": "str",       // nullable, url
  "date_joined": "str", // timestamp
  "last_active": "str", // nullable, timestamp
  "location": "int",    // nullable, id of location
  "firebase_uid": "str", // nullable
  "fcm_id": "str",      // nullable
  "language": "str",    // nullable, ru or ky | default ky
  "is_business": "bool",
  "business": "int",  // nullable, business id
}
```
## public user
```json5
{
  "id": "int",
  "name": "str",        // nullable
  "phone": "str",       // nullable
  "email": "str",       // nullable
  "photo": "str",       // nullable, url
  "date_joined": "str", // timestamp
  "last_active": "str", // nullable, timestamp
  "language": "str",    // nullable, ru or ky | default ky
  "is_business": "bool",
  "business": "int",  // nullable, business id
}
```
## editable fields
```json5
{           
  "name": "str",      // nullable  
  "phone": "str",     // nullable, firebase access token
  "email": "str",     // nullable, firebase access token
  "photo": "bytes",   // nullable
  "location": "int",  // nullable, id of location
  "fcm_id": "str",      // nullable
  "language": "str",    // nullable, ru or ky | default ky
}
```
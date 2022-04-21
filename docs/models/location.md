## Child location
```json5
{
    "id": "int",
    "title_ru": "str",
    "title_ky": "str",
    "type": "str", // nullable, [country, region, city, district, pgt, aimak]
    "type_ru": "str", // nullable, show in settings screen ex: Страна
    "type_ky": "str", // nullable,show in settings screen ex: Страна
    "request_ru": "str",
    "request_ky": "str",
    "parent": "int", // parent location id
    "is_end": "bool",
    "lat": "decimal", // nullable
    "lng": "decimal", // nullable
}
```
## Single location
```json5
{
  "id": "int",
  "title_ru": "str",
  "title_ky": "str",
  "type": "str", // nullable, [country, region, city, district, pgt, aimak]
  "type_ru": "str", // nullable, show in settings screen ex: Страна
  "type_ky": "str", // nullable,show in settings screen ex: Страна
  "request_ru": "str", // nullable, show in top bar, ex: Выберите город
  "request_ky": "str", // nullable, show in top bar, ex: Выберите город
  "is_end": "bool", // if true means the location don't have children locations
  "lat": "decimal", // nullable
  "lng": "decimal", // nullable
  "children": [
    "child location"
  ]
}
```

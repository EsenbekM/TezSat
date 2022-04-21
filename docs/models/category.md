## List of categories
```json5
[
  {
    "id": "int",
    "title_ru": "str",
    "title_ky": "str",
    "icon": "str",      // nullable, url
    "is_end": "bool", // if true means the category don't have children categories
    "product_count": "int",
    "parent": "int",
    "business_count": "int"
  }
]
```

## Single category
```json5
{
  "id": "int",
  "title_ru": "str",
  "title_ky": "str",
  "icon": "str",      // nullable, url
  "parent": "int",
  "children": [
    {
        "id": "int",
        "title_ru": "str",
        "title_ky": "str",
        "icon": "str",      // nullable, url
        "is_end": "bool", // if true means the category don't have children categories
        "product_count": "int",
        "parent": "int",
        "business_count": "int"
    },
  ]
}
```

## List of categories v2
```json5
[
  {
    "id": "int",
    "title_ru": "str",
    "title_ky": "str",
    "icon": "str",      // nullable, url
    "parent": "int",
    "children": [
        {
            "id": "int",
            "title_ru": "str",
            "title_ky": "str",
            "icon": "str",      // nullable, url
            "is_end": "bool", // if true means the category don't have children categories
            "parent": "int",
        },
    ]
  }
]
```
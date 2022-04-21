# Category API

### GET */category/v1/categories/*
List of categories
#### access - *public* 
[response model](../models/category.md#list-of-categories)

### GET */category/v1/categories/{id}/*
Retrieve location by id
#### access - *public*
[response model](../models/category.md#single-category)


### GET */category/v1/categories/{id}/parameters/*
Retrieve options for given category
#### access - *public*
response
```json5
[
  {
    "id": "int",
    "title_ru": "str",
    "title_ky":"str", 
    "category": "int",  // category id
    "optional": "bool", // if false then required on product creation api,
    "type": "str", // enter or select | if enter -> options is empty array
    "options": [
      {
        "id": "int",
        "title_ru": "str",
        "title_ky": "str",
        "parameter": "int"  // parameter id
      }
    ]
  }
]
```

### GET */category/v2/categories/*
List of categories FOR WEB
#### access - *public* 
[response model](../models/category.md#list-of-categories-v2)
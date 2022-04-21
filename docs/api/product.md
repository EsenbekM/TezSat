# Product API

To create a product with images first you need to upload an image with [api](#post-productv1personalphoto-upload) and
paste the given filename to [creation api](#post-productv1personalproducts)

## API V1
### GET */product/v1/products/*
List of all active products
#### access - *public*
gte = greater than or equal   
lte = lower than or equal   
you can request multiple filters:
* ?location=1,2,3,...
* ?category=1,2,3,...
* ?price__gte=1&currency=KGS/USD
* ?price__lte=1&currency=KGS/USD
* ?price__range=100,200&currency=KGS/USD
* ?options=1,2 // parameters are not needed
* ?user=1
* ?is_business=true/false

you can request multiple ordering fields:
* ?ordering=(-)price&currency=KGS/USD
* ?ordering=(-)show_count
* ?ordering=(-)view_count
* ?ordering=(-)upvote_date

search:
* ?search=q

paginated
[response](#short-product)

### GET */product/v1/products/max_price/*
get max price of products
#### access - *public*
request
```
?currency=KGS/USD
```
response
```json5
{
  "price": "decimal"
}
```
### GET */product/v1/products/{id}/*
detail of product
#### access - *public*
[response](#full-product)


### POST */product/v1/products/{id}/claim/*
create claim for product
#### access - *authorized*
request 
```json5
{
	"message": "str" 
}
```
response 
```json5
{
  "id": "int",
  "product": "int",
  "user": "int",
  "message": "str"
}
```

### POST */product/v1/products/{id}/call/*
request for call statistics   
before dialing a number use this api
#### access - *public*
response status code 204

### POST */product/v1/personal/photo-upload/*
upload image
#### access - *authorized*
request
```
{
  "photo": "bytes"
}
```
response
```json5
{
  "filename": "str"
}
```
### GET */product/v1/personal/products/*
list of user products
#### access - *authorized*
paginated
[response](#short-product)

### GET */product/v1/personal/products/{id}/*
product details
#### access - *authorized*
[response](#full-product)


### POST */product/v1/personal/products/*
create product
#### access - *authorized*
request
```json5
{
	"description": "str",
	"location": "int",
	"currency": "str",      // USD or KGS
	"price": "decimal",
	"category": "int",
	"contacts": [
		{
			"phone": "str"
		}
	],
	"parameters": [
		{
			"parameter": "int",
			"option": "int",  // if parameter type == select
            "response": "str", // if parameter type == enter
		}
	],
	"photos": [
	    {
	        "filename": "str"
	    }
	],
  "rating_disabled": "bool" // available only for business accounts
}
```
[response](#full-product)

### PATCH/PUT */product/v1/personal/products/{id}/*
change state of product
#### access - *authorized*
request
```json5
{
	"description": "str",
	"location": "int",
	"currency": "str",      // USD or KGS
	"price": "decimal",
	"category": "int",
	"contacts": [
		{
			"phone": "str"
		}
	],
	"parameters": [
		{
			"parameter": "int",
			"option": "int",  // if parameter type == select
            "response": "str", // if parameter type == enter
		}
	],
	"photos": [
	    {
	        "filename": "str"
	    }
	]
}
```
[response](#full-product)
### DELETE */product/v1/personal/products/{id}/*
delete product
#### access - *authorized*
response 204 status code

### POST */product/v1/personal/products/{id}/upvote/*
upvote the product
#### access - *authorized*
response status code 200

### GET */product/v1/personal/products/{id}/stats/*
get statistic of product
#### access - *authorized - business*
response 
```json5
{
  "id": "int",
  "show_count": "int", 
  "view_count": "int",
  "call_count": "int",
  "message_count": "int",
  "rating": "int",
  "rating_disabled": "bool",
  "favorite_count": "int",
  "review_count": "int",
  "like_count": "int",
  "coverage": "int"
}
```

### GET */product/v1/personal/favorites/*
list of favorite products
#### access - *authorized*
paginated
[response](#short-product)

### POST */product/v1/personal/favorites/*
add product to favorite
#### access - *authorized*
request
```json5
{
	"product": "int"
}
```
response status code 201

### POST */product/v1/personal/favorites/clear/*
remove all favorites
#### access - *authorized*
response status code 204

### DELETE */product/v1/personal/favorites/{product_id}/*
remove product from favorite
#### access - *authorized*
response status code 204


### GET */product/v1/personal/likes/*
list of like products
#### access - *authorized*
paginated
[response](#short-product)

### POST */product/v1/personal/likes/*
like a product
#### access - *authorized*
request
```json5
{
	"product": "int"
}
```
response status code 201

### POST */product/v1/personal/likes/clear/*
remove all likes
#### access - *authorized*
response status code 204

### DELETE */product/v1/personal/likes/{product_id}/*
remove like from product
#### access - *authorized*
response status code 204


#### short product
```json5
{
  "id": "int",
  "user": "public user",
  "title": "str",
  "currency": "str",
  "initial_price": "str",
  "price_kgs": "str",
  "price_usd": "str",
  "show_count": "int",
  "view_count": "int",
  "photos": [
    {
      "id": "int",
      "photo": "str", // url
      "medium_thumbnail": "str", // url
      "small_thumbnail": "str", // url
    }
  ],
  "state": "str",   //active
  "favorite_count": "int",
  "rating": "int", // null, 0 - 5
}
```
[public user](../models/user.md#public-user)
#### full product
```json5
{
  "id": "int",
  "user": "public user",
  "title": "str",
  "description": "str",
  "location": "location",
  "currency": "str",        // USD or KGS
  "initial_price": "str",
  "price_kgs": "str",
  "price_usd": "str",
  "category": "int",
  "state": "str",             // active, inactive, on_review
  "creation_date": "str",
  "upvote_date": "str",
  "show_count": "int",
  "view_count": "int",
  "contacts": [
    {
      "id": "int",
      "phone": "str"
    }
  ],
  "photos": [
    {
      "id": "int",
      "photo": "str" // url
    }
  ],
  "parameters": [
    {
      "id": "int",
      "response":  "str",
      "parameter": {
        "id": "int",
        "title_ru": "str",
        "title_ky": "str",
        "category": "int",
        "type": "str",
      },
      "option": {
        "id": "int",
        "title_ru": "str",
        "title_ky": "str",
        "parameter": "int"
      }
    }
  ],
  "favorite_count": "int",
  "rating": "int", // null, 0 - 5
  "rating_disabled": "bool", // True - a review cannot be created
  "like_count": "int",
  "dislike_count": "int"
}
```
[public user](../models/user.md#public-user)
[location](../models/location.md#child-location)

## API V2 (Development)
Second version of API that needs to be used for listing and retrieving purpose of products.
Other actions like create, update, and delete of them need to be done through [API V1](#api-v1) 
### GET */product/v2/products/*
List of all active products
#### access - *public*
gte = greater than or equal   
lte = lower than or equal   
you can request multiple filters:
* ?location=1,2,3,...
* ?category=1,2,3,...
* ?price__gte=1&currency=KGS/USD
* ?price__lte=1&currency=KGS/USD
* ?price__range=100,200&currency=KGS/USD
* ?options=1,2  // parameters are not needed
* ?user=1
* ?is_business=true/false

search:
* ?search=q

[response](#short-product)

#### Pagination
To get the new page of result use key parameter   

```json5
{
  "key": "1611736371028+48788",
  "results": [
    ...
  ]
}
```

```json5
GET product/v2/products/?key=1611736371028+48788 // Next page of results 
```

### GET */product/v2/products/{id}/*
Detailed information about product
#### access - *public*
[response](#full-product)

### GET */product/v2/suggestions*
Search as you type functionality for products. Get product or category name and 
id that match specific search query.

#### access - *public*

#### query parameters:
* ?query=text

#### response:

```json5
{
  "id": "int",
  "is_category": "boolean", // is this object is category of products or product itself
  "name": "str",
  "icon": "str" // link to the category icon or null
}
```

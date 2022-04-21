# Product Review API

### GET */product/v1/products/{product_id}/reviews/*
list of reviews of product
#### access - *public*
paginated [response](../models/review.md#review)


### POST */product/v1/products/{product_id}/reviews/*
create reviews of product
#### access - *authorized*
request
```json5
{
  "rating": "int", // 1, 2, 3, 4, 5 allowed
  "review": "str"
}
```
[response](../models/review.md#review)

### GET */product/v1/products/{product_id}/reviews/{id}/*
detail review of product
#### access - *public*
[response](../models/review.md#review)

### DELETE */product/v1/products/{product_id}/reviews/{id}/*
delete a review owned by you
#### access - *authorized*
response status code 204

### PATCH/PUT */product/v1/products/{product_id}/reviews/{id}/*
update review of product owned by you
#### access - *authorized*
request
```json5
{
  "rating": "int", // 1, 2, 3, 4, 5 allowed
  "review": "str"
}
```
[response](../models/review.md#review)


### POST */product/v1/products/{product_id}/reviews/{id}/response/*
response to review, can be made only by product owner   
request
```json5
{
  "response": "str"
}
```
[response](../models/review.md#review)

### POST */product/v1/products/{product_id}/reviews/{id}/claim/*
claim on review, can be made only by product owner   
request
```json5
{
  "message": "str"
}
```
[response](../models/review.md#review)
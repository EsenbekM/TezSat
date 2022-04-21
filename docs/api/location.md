# Location API

### GET */location/v1/locations/*
root location with children
#### access - *public*
[response model](../models/location.md#single-location)

### GET */location/v1/locations/{id}*
Retrieve location by id
#### access - *public*
[response model](../models/location.md#single-location)



### GET */location/v1/locations/non_structured/*
List of all locations in one level
#### access - *public*
response
```json5
[
  "location"
]
```
[location](../models/location.md#child-locations)
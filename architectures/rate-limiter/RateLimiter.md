# Rate Limiter Per Endpoint
---


# Reverse Proxy / layer before API Rate limiter 
---




## Per IP - 10/1s ~ 9000/15mins




---
---
# Process Rate limiter 

## Auth endpoints (10 endpoints)

----------------------------------------------------------------------------------
  Method             Endpoint                          Per IP
------------------ --------------------------------- -----------------------------
  POST               /login-via-token                  5/15mins
  POST               /login                            5/15mins
  POST               /signup                           3/15mins
  POST               /signup/verify                    3/15mins
  POST               /request-access-token             3/15mins
  POST               /provider/<provider>              3/15mins
  POST               /provider/complete-signup         3/15mins
  POST               /reset-password                   5/15mins
  POST               /reset-password/verify            5/15mins
  POST               /reset-password/reset             5/15mins


## Trip endpoints (9 endpoints)

----------------------------------------------------------------------------------
  Method             Endpoint                          Per IP
------------------ --------------------------------- -----------------------------
  POST              /new-trip                         15/15mins
  POST              /trip-cover-upload-verification   15/15mins
  POST              /end-trip                         15/15mins 
  POST              /modify-trip-data                 45/15mins
  DELETE            /trip                             45/15mins
  GET               /all-trips/full                   300/15mins
  GET               /current-trip-id                  300/15mins
  GET               /trip/<trip_id>                   450/15mins
  GET               /trip-by-token/<token>            450/15mins


## Trip Contents endpoints (5 endpoints)

----------------------------------------------------------------------------------
  Method             Endpoint                          Per IP
------------------ --------------------------------- -----------------------------
  POST              /sync                             450/15mins
  POST              /request-presign-urls             450/15mins
  GET               /trip-contents-hash/<trip_id>     500/15mins 
  GET               /trip-contents-metadata/<trip_id> 500/15mins
  GET               /all-contents                     500/15mins



## User endpoints (3 endpoints)

----------------------------------------------------------------------------------
  Method             Endpoint                          Per IP
------------------ --------------------------------- -----------------------------
  GET               /update-avatar-presign-url         45/15mins
  POST              /complete-update-avatar            45/15mins
  GET               /user-data                         300/15mins


## Trip View endpoints (3 endpoints)

----------------------------------------------------------------------------------
  Method             Endpoint                          Per IP
------------------ --------------------------------- -----------------------------
  POST              /generate-trip-view-link          75/15mins
  GET               /<token>                          300/15mins
  GET               /<token>/contents                 300/15mins


## User Setting endpoints (2 endpoints)

----------------------------------------------------------------------------------
  Method             Endpoint                          Per IP
------------------ --------------------------------- -----------------------------
  PATCH             /user-settings                    45/15mins 
  GET               /user-settings                    300/15mins


## FriendShips endpoints (5 endpoints)
----------------------------------------------------------------------------------
  Method             Endpoint                          Per IP
------------------ --------------------------------- -----------------------------
  GET               /friends                          300/15mins 
  GET               /incoming-friend-list             300/15mins
  GET               /outcoming-friend-list            300/15mins
  UPDATE            /accept-friend-request            300/15mins
  POST              /request-friend                   300/15mins

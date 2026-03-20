## Sign Up 
Server take username, password, email, displayname
server then will check fro duplicate email and username 
server then will transfer to verify service

## Sign Up Flow
```
User -> request signup
        |
        |_check for inputs validation -> return if not valid
        |
        |_check for duplicate email and username -> return if duplicate
        |
        |_generate hash password
        |
        |_generate object including email, display_name, username, password  -> pass  
        | it to verify service -> return 
```




## Verification
User send code, then server pick up from cache, verify then pass it to process user service

## Verification Flow
```
User -> verify code
        |
        |_Check code
            |_not match -> return 
            |_match -> process user service
```




## Process New User (Internal Service)
Process user from data get from cache

## Process New User Flow
```
Verification success -> Process userdata from cache
                            |
                            |_ put into postgres
```




## Login
Server will take username and password then validate with postgres
Return refresh and access token if login success fully

## Login Flow
```
User -> request login
            |
            |_ password, username validation
            |   |_invalid -> return 
            |
            |_ get userdata from postgres using username
                |_not found -> return 
                |
                |_found -> hash user given password and compare with stored hash    
                | password
                    |
                    |_password not match -> return
                |
                |_ generate tokens
                   |
                   |_store refresh token
                |
                |_return data and tokens
```



## Login Via Token 
Using access token to login 

## Login Via Token Flow 
```
User -> access token -> verify
                        |
                        |_ expired or invalid ->return None -> user then can decide 
                        | to request new access token then retry
                        |
                        |_success -> return userdata

```



## Request New Access Token
Using refresh token to request new access token 

## Request New Access Token Flow
```
User -> refresh token -> verify 
                            |
                            |_Check for expiration, invalid, revoke status 
                                |_ return None if one of condition true
                                |_ genrate new access token -> return new access token
```         





## Note
refresh token are set to valid for 30 days
access token are set to valid for 15 minutes
## userdata only contain {} of user_id and role, All any other related data are in dirrerent end points

Input validation are in InputValidation.md
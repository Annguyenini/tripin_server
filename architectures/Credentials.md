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


## Login / Signup with provider
User -> request provider -> send id_token to server -> server send request to provider -> get data 

provider respond->
                |
                |_ invalid token -> return code 404
                |
                |_ valid token -> get data from provider (provider name, sub(provider_id)(a unique id that belong to user from the provider),email) ->
                ->perform checking -> 
                |
                |_user exists with the same provider_id, and email -> return 200, app will decide to request signin
                |
                |_email belong to user, but provider_id not, return 404 (user will able to linked with provider later on)
                |
                |-> return 500, server failed
                |
                |_new user, email, provider_id doesn't exist -> return 200, pending_token (this token contain email, provider,provider_id )
                                                            |
                                                            |_user than complete setup account, including (username, password, displayname) 
                                                            -> Server checking for inputs validation, exists username,email, email-> success -> return 200
                                                                                                                      |
                                                                                                                      |-> fail -> return 404
                                                            

## Reset Password/ Change Password
3 end points
User -> request with email 
                          |-> input validation fail -> return 404
                          |
                          |-> checking for exists email
                                                      |-> not exists return 404
                                                      |
                                                      |-> return 500, server failed
                                                      |
                                                      |-> send code via email ,201

User -> send token, code -> server verify code and token -> return 200, verified token
                                                          |
                                                          |-> return 500, server failed
                                                          |
                                                          |-> invalid token return 404

User -> send new_password -> server -> input validation -> hased-> update db -> return 200
                                                                            |
                                                                            |->return 500 if failed



                                                      
## Note
refresh token are set to valid for 30 days
access token are set to valid for 15 minutes
## userdata only contain {} of user_id and role, All any other related data are in dirrerent end points

Input validation are in InputValidation.md


## Upload Media 
reciept the media data from user, including coordinate data (longitude,latitude), time stamp, and media_id
then process to add information into database (postgres)
then upload into cloud (s3)
## Upload Media flow 
```
User request -> Server
                 |
                 |_return if no media 
                 |_return if no permission
                 |_insert into database (postgres)
                 |_upload to cloud (s3)
                 |_return success with media hash

```



## Note 
Media Hash is string that encode for user to see if there version of media match, then come to the sync decision 

if upload to cloud failed make sure to roll back the insert postgres
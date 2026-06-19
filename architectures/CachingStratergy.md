# Cache System (Cache Aside + TTL)

## Read Flow

1. request / get  
2. check cache  
3. cache miss  
4. get from database  
5. put to cache (with TTL)

---

## Write Flow

1. request / update / write  
2. write to database  
3. invalidate cache

# Login
    POST <ENDPOINT>/login
Ratelimited `5/sec per Remote Address`


## Parameters
### URI Parameters
None
### Body Parameters
Field | Required | Description
--- | --- | ---
username | Y | Username for your account
password | Y | Password for your account

## Example
### Request

    POST https://requip.azurewebsites.net/login

#### Request Headers
```json
{"Content-Type":"application/json"}
```
#### Request Body    
```json
{
    "username": "abhishek0220",
    "password":<PASSWORD>
}
```

### Response   
```json
{
    "message": "Logging in User abhishek0220",
    "name": "Abhishek",
    "image": "abhishek0220/d91c887f-8ac2-4620-be15-cb4ad4f0e237.jpg",
    "username":"abhishek0220",
    "access_token":<JWT_ACCESS_TOKEN>,
    "refresh_token": <JWT_REFRESH_TOKEN>
}
```
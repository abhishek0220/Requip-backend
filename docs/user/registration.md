# Registration
    POST <ENDPOINT>/registration

## Parameters
### URI Parameters
None
### Body Parameters
Field | Required | Description
--- | --- | ---
username | Y | Unique account name
name | Y | Your Name
email | Y | IIT Jammu Email ID
phone_number | Y | Your phone number
password | Y | Password for your account

## Example
### Request

    POST https://requip.azurewebsites.net/registration

#### Request Headers
```json
{"Content-Type":"application/json"}
```
#### Request Body    
```json
{
    "username": "abhishek0220",
    "name":"Abhishek",
    "email":"2018ucs0087@iitjammu.ac.in",
    "phone":<MOBILE>,
    "password":<PASSWORD>
}
```

### Response   
```json
{
    "message": "User abhishek0220 is created",
    "username" : "abhishek0220"
}
```
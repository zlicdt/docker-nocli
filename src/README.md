# API
The backend of `docker-nocli`

## How the frontend get auth
Send `POST /auth/token` with `{"username":"…","password":"…"}`,
if the username and password was right,
return a string `{"token":"<token>"}`.

Construct HTTP request with `Authorization: Bearer <token>`,
otherwise it will 401 when access to non-public things.
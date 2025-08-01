
Login Kit for Web
This guide details how to enable authentication from your web app to TikTok. After successfully completing authentication with TikTok, developers can obtain an access_token for the TikTok user.

Prerequisites
Register your app
Register your app following these steps. Then obtain a client key and secret from the developer portal on https://developers.tiktok.com under Manage apps.

Configure redirect URI
Redirect URI is required for web apps. After the user completes authorization with Login Kit on the web, they will be redirected to a URI provided by you. This redirect URI must be registered in the Login Kit product configuration for your app.

The following are restrictions for registering redirect URIs.

A maximum of 10 URIs is supported.
The length of each URI must be less than 512 characters.
URIs must be absolute and begin with https. For example:
Correct: https://dev.example.com/auth/callback/
Incorrect: dev.example.com/auth/callback/
URIs must be static. Parameters will be denied. For example:
Correct: https://dev.example.com/auth/callback/
Incorrect: https://dev.example.com/auth/callback/?id=1
URIs cannot include a fragment, or hash character (#):
Correct: https://dev.example.com/auth/callback/
Incorrect: https://dev.example.com/auth/callback/#100
Integration Guide
Implement the front-end code
Get started by connecting your front-end login button to the server endpoint. The following is an example in HTML:

<a href='{SERVER_ENDPOINT_OAUTH}'>Continue with TikTok</a>
Implement the server code to handle authorization grant flow
The server code must be responsible for the following:

Ensuring that the client secret and refresh token are stored securely.
Ensuring that the security for each user is protected by preventing request forgery attacks.
Handling the refresh flow before access token expiry.
Managing the access token request flow for each user.
Redirect request to TikTok's authorization server
Create an anti-forgery state token
You must prevent request forgery attacks to protect the security of your users. The first step before making the redirect request to TikTok's authorization server is to create a unique session token to maintain the state between the request and callback.

You will later match this unique session token with the authentication response to verify that the user is making the request and not a malicious attacker.

One of the simple approaches to a state token is a randomly generated alphanumeric string constructed using a random-number generator. For example:

let array = new Uint8Array(30); 
const csrfState = window.crypto.getRandomValues(array);
Initial redirect to TikTok's authorization page
To make the initial redirect request to TikTok's authorization server, the following query parameters below must be added to the Authorization Page URL using the application/x-www-form-urlencoded format.

For example, you can use an online URL encoder to encode parameters. Select UTF-8 as the destination character set.

Parameter

Type

Description

client_key

String

The unique identification key provisioned to the partner.

scope

String


A comma (,) separated string of authorization scope(s). These scope(s) are assigned to your application on the TikTok for Developers website. They handle what content your application can and cannot access. If a scope is toggleable, the user can deny access to one scope while granting access to others.

redirect_uri

String

The redirect URI that you requested for your application. It must match one of the redirect URIs you registered for the app.

state

String

The state is used to maintain the state of your request and callback. This value will be included when redirecting the user back to the client. Check if the state returned in the callback matches what you sent earlier to prevent cross-site request forgery.

The state can also include customized parameters that you want TikTok service to return.

response_type

String

This value should always be set to code.

disable_auto_auth

int

Controls whether the authorization page is automatically presented to users. When set to 0, skips the authorization page for valid sessions. When set to 1, always displays the authorization page.

Redirect your users to the authorization page URL and supply the necessary query parameters. Note that the page can only be accessed through HTTPS.

Type

Description

URL

https://www.tiktok.com/v2/auth/authorize/

Query parameters


client_key=<client_key>&response_type=code&scope=<scope>&redirect_uri=<redirect_uri>&state=<state>

Note: If you are an existing client and use https://www.tiktok.com/auth/authorize/ as the authorization page URL, please register a redirect URI for your app and migrate to the new URL mentioned above.

The following is an example using Node, Express, and JavaScript:

const express = require('express');
const app = express();
const fetch = require('node-fetch');
const cookieParser = require('cookie-parser');
const cors = require('cors');

app.use(cookieParser());
app.use(cors());
app.listen(process.env.PORT || 5000).

const CLIENT_KEY = 'your_client_key' // this value can be found in app's developer portal

app.get('/oauth', (req, res) => {
    const csrfState = Math.random().toString(36).substring(2);
    res.cookie('csrfState', csrfState, { maxAge: 60000 });

    let url = 'https://www.tiktok.com/v2/auth/authorize/';

    // the following params need to be in `application/x-www-form-urlencoded` format.
    url += '?client_key={CLIENT_KEY}';
    url += '&scope=user.info.basic';
    url += '&response_type=code';
    url += '&redirect_uri={SERVER_ENDPOINT_REDIRECT}';
    url += '&state=' + csrfState;

    res.redirect(url);
})
TikTok prompts a users to log in or sign up
The authorization page takes the user to the TikTok website if the user is not logged in. They are then prompted to log in or sign up for TikTok.

TikTok prompts a user for consent
After logging in or signing up, an authorization page asks the user for consent to allow your application to access your requested permissions.

Manage authorization response
If the user authorizes access, they will be redirected to redirect_uri with the following query parameters appended using application/x-www-form-urlencoded format:

Parameter

Type

Description

code


String

Authorization code that is used in getting an access token.

scopes


String

A comma-separated (,) string of authorization scope(s), which the user has granted.

state


String


A unique, non-guessable string when making the initial authorization request. This value allows you to prevent CSRF attacks by confirming that the value coming from the response matches the one you sent.

error


String


If this field is set, it means that the current user is not eligible for using third-party login or authorization. The partner is responsible for handling the error gracefully.

error_description


String

If this field is set, it will be a human-readable description about the error.

Manage access token
Using the code appended to your redirect_uri, you can obtain access_token for the user, which completes the flow for logging in with TikTok.

See Manage User Access Tokens for related endpoints.







Endpoints
1. Fetch an access token using an authorization code
Once the authorization code callback is handled, you can use the code to retrieve the user's access token.

Endpoint
POST https://open.tiktokapis.com/v2/oauth/token/

Headers
Key

Value

Content-Type

application/x-www-form-urlencoded

Request body parameters
Key

Type

Description

client_key

string

The unique identification key provisioned to the partner.

client_secret

string

The unique identification secret provisioned to the partner.

code


string


The authorization code from the web, iOS, Android or desktop authorization callback. The value should be URL decoded.

grant_type

string

Its value should always be set as authorization_code.

redirect_uri


string

Its value must be the same as the redirect_uri used for requesting code.

code_verifier

string

Required for mobile and desktop app only. Code verifier is used to generate code challenge in PKCE authorization flow.

Response struct
Key

Type

Description

open_id

string

The TikTok user's unique identifier.

scope

string

A comma-separated list (,) of the scopes the user has agreed to authorize.

access_token

string

The access token for future calls on behalf of the user.

expires_in


int64

The expiration of access_token in seconds. It is valid for 24 hours after initial issuance.

refresh_token

string

The token to refresh access_token. It is valid for 365 days after the initial issuance.

refresh_expires_in


int64

The expiration of refresh_token in seconds.

token_type

string

The value should be Bearer.

Make sure to store these values on your back end as they are needed to persist access.

Example
curl --location --request POST 'https://open.tiktokapis.com/v2/oauth/token/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Cache-Control: no-cache' \
--data-urlencode 'client_key=CLIENT_KEY' \
--data-urlencode 'client_secret=CLIENT_SECRET' \
--data-urlencode 'code=CODE' \
--data-urlencode 'grant_type=authorization_code' \
--data-urlencode 'redirect_uri=REDIRECT_URI'
If the request is successful, the response will look like the following.

{
    "access_token": "act.example12345Example12345Example",
    "expires_in": 86400,
    "open_id": "afd97af1-b87b-48b9-ac98-410aghda5344",
    "refresh_expires_in": 31536000,
    "refresh_token": "rft.example12345Example12345Example",
    "scope": "user.info.basic,video.list",
    "token_type": "Bearer"
}
If the request is not successful, an error response body will be returned in the response, like the following.

{
    "error": "invalid_request",
    "error_description": "Redirect_uri is not matched with the uri when requesting code.",
    "log_id": "202206221854370101130062072500FFA2"
}
2. Refresh an access token using a refresh token
Although the fetched access_token expires within 24 hours, it can be refreshed without user consent. The developer's back-end server can schedule background jobs to keep tokens up to date.

Endpoint
POST https://open.tiktokapis.com/v2/oauth/token/

Headers
Key

Value

Content-Type

application/x-www-form-urlencoded

Request body parameters
Key

Type

Description

client_key

string

The unique identification key provisioned to the partner.

client_secret

string

The unique identification secret provisioned to the partner.

grant_type

string

Its value should always be set as refresh_token.

refresh_token

string

The user's refresh token.

Response struct
Key

Type

Description

open_id

string

The partner-facing user ID.

scope


string

A comma-separated list (,) of the scopes the user has agreed to authorize.

access_token


string

The new token for future calls on behalf of the user.

expires_in

int64

The expiration of the access token in seconds.

refresh_token


string

The token to refresh a user's access_token.

Note: The returned refresh_token may be different than the one passed in the payload. You must use the newly-returned token if the value is different than the previous one.

refresh_expires_in


int64

The expiration for refresh_token in seconds.

token_type

string

The value should be Bearer.

Make sure to store these values on your back end as they are needed to persist access.

Example
curl --location --request POST 'https://open.tiktokapis.com/v2/oauth/token/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Cache-Control: no-cache' \
--data-urlencode 'client_key=CLIENT_KEY' \
--data-urlencode 'client_secret=CLIENT_SECRET' \
--data-urlencode 'grant_type=refresh_token' \
--data-urlencode 'refresh_token=REFRESH_TOKEN'
If the request is successful, the response will look like the following.

{
    "access_token": "act.example12345Example12345Example",
    "expires_in": 86400,
    "open_id": "asdf-12345c-1a2s3d-ac98-asdf123as12as34",
    "refresh_expires_in": 31536000,
    "refresh_token": "rft.example12345Example12345Example",
    "scope": "user.info.basic,video.list",
    "token_type": "Bearer"
}
If the request is not successful, an error response body will be returned in the response, like the following.

{
    "error": "invalid_request",
    "error_description": "The request parameters are malformed.",
    "log_id": "202206221854370101130062072500FFA2"
}
3. Revoke access
When a user wants to disconnect your application from TikTok, you can revoke their tokens so the user will no longer see your application on the Manage app permissions page of the TikTok for Developers website.

Endpoint
POST https://open.tiktokapis.com/v2/oauth/revoke/

Headers
Key

Value

Content-Type

application/x-www-form-urlencoded

Request body parameters
Key

Type

Description

client_key


string

The unique identification key provisioned to the partner.

client_secret

string

The unique identification secret provisioned to the partner.

token

string

The access_token that bears the authorization of the TikTok user.

Response struct
If the request is successful, the response struct will be empty.

Example
curl --location --request POST 'https://open.tiktokapis.com/v2/oauth/revoke/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Cache-Control: no-cache' \
--data-urlencode 'client_key=CLIENT_KEY' \
--data-urlencode 'client_secret=CLIENT_SECRET' \
--data-urlencode 'token=ACCESS_TOKEN'
If the request is not successful, an error response body will be returned in the response, like the following.

{
    "error": "invalid_request",
    "error_description": "The request parameters are malformed.",
    "log_id": "202206221854370101130062072500FFA2"
}



Error Handling
In the new generation of the TikTok Login Kit, OAuth error responses include an error code represented as readable strings with a detailed error message and log ID. When contacting the TikTok support team, these details must be provided.

Error struct
Key

Type

Description

error

String

The error category in string.

error_description


String

The detailed error description.


log_id

String

The unique ID associated with every request for debugging purposes.

Error categories
The error property can be one of the following values:

Error

Description

access_denied

The resource owner or authorization server denied the request.

invalid_client


Client authentication failed (for example, unknown client, no client authentication included, or unsupported authentication method).

invalid_grant


The provided authorization grant (for example, authorization code or resource owner credentials) or refresh token is invalid, expired, revoked, does not match the redirection URI used in the authorization request, or was issued to another client.

invalid_request

The request misses a required parameter or is otherwise malformed.

invalid_scope


The requested scope is invalid, unknown, or malformed.

unauthorized_client


The client is not authorized to request an authorization code using this method.

unsupported_grant_type

The authorization grant type is not supported by the authorization server.

unsupported_response_type

The authorization server does not support obtaining an authorization code using this method.

server_error

Other internal server errors.

temporarily_unavailable

Service is temporarily unavailable.
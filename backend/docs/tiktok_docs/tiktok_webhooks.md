TikTok Webhooks
Overview
Webhook is a subscription that notifies your application via a callback URL when an event happens in TikTok. Rather than requiring you to pull information via API, you can use webhooks to get information on events that occur. Notifications are delivered via HTTPS POST in JSON format to the callback url configured for your app in the Developer Portal. This information can be used to update your system or to trigger business processes.

Requirements and Limitations
In order to receive a webhook message, callback URL should be registered in the client application on TikTok Developer Portal. This callback url can be configured either during the initial application or after the client key has been provisioned by updating the application.

The callback URL must do the following:

Immediately respond with a 200 HTTP status code to acknowledge the receipt of the event notification.
The callback URL endpoint must require HTTPS.
If a 200 HTTP status code is not returned, TikTok assumes that the delivery was unsuccessful. TikTok retries the delivery of event notification for up to 72 hours using exponential backoff. After 72 hours, the notification is discarded and not sent again.

TikTok makes a best effort for "at least once delivery" of webhooks. Webhook endpoints might receive the same event more than once. There should be a guard against duplicated event receipts by making your event processing idempotent.

Webhook Events
Webhooks let you subscribe to events and receive notice when an event occurs. For more information about how to set up a webhook subscription, see Webhooks Overview.

By default, you are subscribed to all events when a callback URL is configured in the TikTok Developer Portal.

Webhook Structure
Request Body
Key

Type

Description

client_key

string

The unique identification key provisioned to the partner.

event

string

Event name.

create_time

int64

The time in which the event occurred. UTC epoch time is in seconds.

user_openid

string

The TikTok user's unique identifier; obtained through /oauth/access_token/.

content

string

A serialized JSON string of event information.


Event types
authorization.removed
Fired when the user's account deauthorized from your application.

The access_token for the user will have been already revoked when you receive the disconnect callback message. Developers can persist this information for clean-up purposes.

Key

Type

Description

reason

int

0 = Unknown

1 = User disconnects from TikTok app

2 = User's account got deleted

3 = User's age changed

4 = User's account got banned

5 = Developer revoke authorization


Example payload
{
    "client_key": "bwo2m45353a6k85",
    "event": "authorization.removed",
    "create_time": 1615338610,
    "user_openid": "act.example12345Example12345Example",
    "content": "{\"reason\": 1 }"
}
video.upload.failed
Fired when the video uploaded from Video Kit fails to upload in TikTok.

Example payload
{
    "client_key": "bwo2m45353a6k85",
    "event": "video.upload.failed",
    "create_time": 1615338610,
    "user_openid": "act.example12345Example12345Example",
    "content":"{\"share_id\":\"video.6974245311675353080.VDCxrcMJ\"}"
}
video.publish.completed
Fired when the video uploaded from Video Kit has been published by the user in TikTok.

Example payload
{
    "client_key": "bwo2m45353a6k85",
    "event": "video.publish.completed",
    "create_time": 1615338610,
    "user_openid": "act.example12345Example12345Example",
    "content":"{\"share_id\":\"video.6974245311675353080.VDCxrcMJ\"}"
}
portability.download.ready
Fired when data requested via from the Data Portability API is in the downloading state.

Example payload:

{
    "client_key": "developer_client_key",
    "event": "portability.download.ready",
    "create_time": 1615338610,
    "content":"{\"request_id\":123123123123123}"
}
Note: content is a JSON object marshalled as a string

{
    "request_id": 123123123123123
}
Payload content
Key

Type

Description

Example

request_id

int64

The unique ID generated to track the download data request. This value can be obtained from the Add Data Request API

123123123123

Check the signature
TikTok webhooks are sent with a signature the destination server can use to verify that the event came from TikTok and not a third party or malicious system. It is strongly recommended that webhook consumers verify these signatures before processing each webhook event.

Verify Message Signature
To protect your app against man-in-the-middle and replay attacks, you should verify the signature of messages sent to your application. Since this timestamp is part of the signed payload, an attacker cannot change the timestamp without invalidating the signature. If the signature is valid but the timestamp is too old, you can have your application reject the payload.

The signature is included as TikTok-Signature in the header.

Example of TikTok-Signature
"Tiktok-Signature": "t=1633174587,s=18494715036ac4416a1d0a673871a2edbcfc94d94bd88ccd2c5ec9b3425afe66"
Signature Verification
Step 1: Extract the timestamp and signatures from the header
Split the header, using the , character as the separator, to get a list of elements. Next, split each element, using the = character as the separator, to get a prefix and value pair.

The value for the prefix t corresponds to the timestamp, and s corresponds to the signature.

Step 2: Signature Generation
signed_payload can be created by concatenating:

The timestamp as a string
The character .
The actual JSON payload (request body)
An HMAC with the SHA256 hash function is computed with your client_secret as the key and your signed_payload string as the message.

Step 3: Signature Generation
Compare the signature in the header to the generated signature. In the case they are equal, compute the difference between the current timestamp and the received timestamp in the header. Use this to decide whether the difference is tolerable.

# Direct Post
Get Started
This guide demonstrates how to use the Content Posting API to post content directly to TikTok.

Prerequisites
To successfully complete this tutorial, you will need the following:

A valid video if you want to post videos:
Ensure you have a video file in one of the supported formats, such as MP4 + H.264, stored on your local machine.
Alternatively, you can provide the URL of a video from your verified domain or URL prefix. Learn how to verify your domain or URL prefix.
Learn more about video restrictions.
A valid photo if you want to post photos:
You must provide a URL of a photo from your verified domain or URL prefix. Learn how to verify your domain or URL prefix.
Learn more about photo restrictions.
A registered app on the TikTok for Developers website.
Add the Content Posting API product to your app as shown below.

To enable the direct posting of content on authorized users' profiles, you need to enable the Direct Post configuration for the Content Posting API in your app, as shown below.

Get approval and authorization of the video.publish scope. Learn more about scopes.
Your app must be approved for the video.publish scope.
The target TikTok user must have authorized your app for the video.publish scope.
The access token and open ID of the TikTok user who authorized your app. Learn how to obtain the access token and open ID.
Note: All content posted by unaudited clients will be restricted to private viewing mode. Once you have successfully tested your integration, to lift the restrictions on content visibility, your API client must undergo an audit to verify compliance with our Terms of Service.

Post directly to TikTok
This section demonstrates how to successfully post a video or photo to a creator's TikTok account.

Query Creator Info
To initiate a direct post to a creator's account, you must first use the Query Creator Info endpoint to get the target creator's latest information. For more information about why creator information is necessary, refer to these UX guidelines.

Request:

curl --location --request POST 'https://open.tiktokapis.com/v2/post/publish/creator_info/query/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json; charset=UTF-8'
Response:

200 OK

{
   "data":{
      "creator_avatar_url": "https://lf16-tt4d.tiktokcdn.com/obj/tiktok-open-platform/8d5740ac3844be417beeacd0df75aef1",
      "creator_username": "tiktok",
      "creator_nickname": "TikTok Official",
      "privacy_level_options": ["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"] 
      "comment_disabled": false,
      "duet_disabled": false,
      "stitch_disabled": true,
      "max_video_post_duration_sec": 300
   },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F3"
     }
Post a video
To initiate video upload on TikTok's server, you must invoke the Direct Post Video endpoint. You have the following two options:

If you have the video file locally, set the source parameter to FILE_UPLOAD in your request.
If the video is hosted on a URL, set the source parameter to PULL_FROM_URL.
Example
Example using source=FILE_UPLOAD:

Request:

curl --location 'https://open.tiktokapis.com/v2/post/publish/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json; charset=UTF-8' \
--data-raw '{
  "post_info": {
    "title": "this will be a funny #cat video on your @tiktok #fyp",
    "privacy_level": "MUTUAL_FOLLOW_FRIENDS",
    "disable_duet": false,
    "disable_comment": true,
    "disable_stitch": false,
    "video_cover_timestamp_ms": 1000
  },
  "source_info": {
      "source": "FILE_UPLOAD",
      "video_size": 50000123,
      "chunk_size":  10000000,
      "total_chunk_count": 5
  }
}'
Response:

200 OK

{
    "data": {
        "publish_id": "v_pub_file~v2-1.123456789",
        "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=67890&upload_token=Xza123"    
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F3"
     }
}


Example using source=PULL_FROM_URL:

Request:

curl --location 'https://open.tiktokapis.com/v2/post/publish/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json; charset=UTF-8' \
--data-raw '{
  "post_info": {
    "title": "this will be a funny #cat video on your @tiktok #fyp",
    "privacy_level": "MUTUAL_FOLLOW_FRIENDS",
    "disable_duet": false,
    "disable_comment": true,
    "disable_stitch": false,
    "video_cover_timestamp_ms": 1000
  },
  "source_info": {
      "source": "PULL_FROM_URL",
      "video_url": "https://example.verified.domain.com/example_video.mp4"
  }
}'
Response:

200 OK

{
    "data": {
        "publish_id": "v_pub_url~v2.123456789"  
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F4"
     }
}
If you are using source=FILE_UPLOAD

Extract the upload_url and publish_id from the response data.
Send the video from your local filesystem to the extracted upload_url using a PUT request. The video processing will occur asynchronously once the upload is complete.
curl --location --request PUT 'https://open-upload.tiktokapis.com/video/?upload_id=67890&upload_token=Xza123' \
--header 'Content-Range: bytes 0-30567099/30567100' \
--header 'Content-Type: video/mp4' \
--data '@/path/to/file/example.mp4'
With the publish_id returned earlier, check for status updates using the Get Post Status endpoint.

curl --location 'https://open.tiktokapis.com/v2/post/publish/status/fetch/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json; charset=UTF-8' \
--data '{
    "publish_id": "v_pub_url~v2.123456789"
}'
Post photos
To initiate photo upload on TikTok's server, you must invoke the Content Posting API endpoint.

Note:

There are differences between the photo post endpoint and the existing video post endpoint.

Use /v2/post/publish/content/init/ to upload photos instead of /v2/post/publish/inbox/video/init/
The post_mode and media_type is required in request.body
Example
Request:

curl --location 'https://open.tiktokapis.com/v2/post/publish/content/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json' \
--data-raw '{
    "post_info": {
        "title": "funny cat",
        "description": "this will be a #funny photo on your @tiktok #fyp",
        "disable_comment": true,
        "privacy_level": "PUBLIC_TO_EVERYONE",
        "auto_add_music": true
    },
    "source_info": {
        "source": "PULL_FROM_URL",
        "photo_cover_index": 1,
        "photo_images": [
            "https://tiktokcdn.com/obj/example-image-01.webp",
            "https://tiktokcdn.com/obj/example-image-02.webp"
        ]
    },
    "post_mode": "DIRECT_POST",
    "media_type": "PHOTO"
}'
Response:

200 OK

{
    "data": {
        "publish_id": "p_pub_url~v2.123456789"
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F3"
     }
}


Direct Post
Overview
To directly post a video to users' TikTok accounts, you must invoke the Content Posting API - Direct Post endpoint to perform the following actions:

Query creator information to render the UI elements to be displayed on the Export page of your app.
Learn more about the UX guidelines here.
Learn more about the creator_info/query API here.
Initialize the post request.
Export the video to TikTok servers.
This guide contains comprehensive information about the API, including the endpoint, request schema, and response schema.

Note: All content posted by unaudited clients will be restricted to private viewing mode. Once you have successfully tested your integration, to lift the restriction on content visibility, your API client must undergo an audit to verify compliance with our Terms of Service.

Initialize the posting request
Once you have requested creator info, and users have provided the necessary metadata for their posts and given explicit consent to send their video to TikTok, the next step is to initialize the posting request.

HTTP URL

/v2/post/publish/video/init/

HTTP Method

POST

Scope

video.publish

Request
Note: Each user access_token is limited to 6 requests per minute.

Header
Field Name

Description

Value

Required

Authorization

The token that bears the authorization of the TikTok user, which is obtained through /oauth/access_token/.

Bearer {$UserAccessToken}

true

Content-Type

The content format of the body of this HTTP request.

application/json; charset=UTF-8

true

Body
Field Name

Nested Field Name

Type

Description

Required









































post_info



privacy_level



string

Enum of:

PUBLIC_TO_EVERYONE

MUTUAL_FOLLOW_FRIENDS

FOLLOWER_OF_CREATOR

SELF_ONLY



The provided value must match one of the privacy_level_options returned in the /creator_info/query/ API.







true



title



string

The video caption. Hashtags (#) and mentions (@) will be matched, or deliminated by spaces or new lines.



The maximum length is 2200 in UTF-16 runes.

If not specified, the ticket post will not have any captions.

























false



disable_duet

bool

If set to true, other TikTok users will not be allowed to make Duets using this post.



The TikTok server disables Duets for private accounts and those who set the Duet permission to "No one" in their privacy setting.

disable_stitch



bool

If set to true, other TikTok users will not be allowed to make Stitches using this post.



The TikTok server disables Stitches for private accounts and those who set the Stitch permission to "No one" in their privacy setting.

disable_comment



bool



If set to true, other TikTok users will not be allowed to make comments on this post.



The TikTok server disables comments for users who set the Comments permission to "No one" in their privacy setting.

video_cover_timestamp_ms

int32

Specifies which frame (measured in milli-seconds) will be used as the video cover.



If not set, or the specified value is invalid, the cover is set to the first frame of the uploaded video.

brand_content_toggle

bool

Set to true if the video is a paid partnership to promote a third-party business.

true

brand_organic_toggle

bool

Set to true if this video is promoting the creator's own business.

is_aigc

bool

Set to true if the video is AI generated content.



If set, the video will be labelled with Creator labeled as AI-generated tag in video's description.



false

source_info

source



string

Choose from:

PULL_FROM_URL

FILE_UPLOAD

Learn about the limitations for these file transmission methods.





true



video_url

string

A public-accessible URL from which the TikTok server will pull to retrieve the video resource.

true for PULL_FROM_URL

video_size

int64

The size of the to-be-uploaded video file in bytes.



true forFILE_UPLOAD



chunk_size

int64

The size of the chunk in bytes.

total_chunk_count

int64

The total number of chunks.

Example
curl --location 'https://open.tiktokapis.com/v2/post/publish/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json; charset=UTF-8' \
--data-raw '{
  "post_info": {
    "title": "this will be a funny #cat video on your @tiktok #fyp",
    "privacy_level": "MUTUAL_FOLLOW_FRIENDS",
    "disable_duet": false,
    "disable_comment": true,
    "disable_stitch": false,
    "video_cover_timestamp_ms": 1000
  },
  "source_info": {
      "source": "FILE_UPLOAD",
      "video_size": 50000123,
      "chunk_size":  10000000,
      "total_chunk_count": 5
  }
}'
Response
Field Name

Nested Field

Type

Description

data



publish_id



string



An identifier to track the posting action, which you can use to check the status.

The maximum length of this field is 64.

upload_url



string



The URL provided by TikTok where the video file can be uploaded. The maximum length of this field is 256.

This field is only for source=FILE_UPLOAD.

error

code

string

You can decide whether the request is successful based on the error code. Any code other than ok indicates the request did not succeed. Learn more about error codes.

message

string

A human readable description of the error.

logid

string

A unique identifier for the execution of this request.

Note: The upload_url is valid for one hour after issuance. The upload must be completed in this time range.

Example
200 OK
{
    "data": {
        "publish_id": "v_pub_file~v2-1.123456789",
        "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=67890&upload_token=Xza123"    
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F3"
     }
}
Error codes
HTTP Status

error.code

Description

400

invalid_param

Check error message for details.

403



spam_risk_too_many_posts

The daily post cap from the API is reached for the current user.

spam_risk_user_banned_from_posting

The user is banned from making new posts.



reached_active_user_cap

The daily quota for active publishing users from your client is reached.

unaudited_client_can_only_post_to_private_accounts

Unaudited clients can only post to a private account. The publish attempt will be blocked when calling /publish/video/init/.

url_ownership_unverified



To use PULL_FROM_URL as the video transfer method, the developer must verify the ownership of the URL prefix or domain. Refer to this doc for more details.

privacy_level_option_mismatch

privacy_level is not specified or not among the options from the privacy_level_options returned in /publish/creator_info/query/ API.



All clients are required to correctly display the creator account's privacy level options and honor the users' choice. Occurances of this error for product-use applications suggest violations to TikTok's product-use guidance.

401

access_token_invalid

The access_token is invalid or has expired.

scope_not_authorized

The access_token does not bear user's grant on video.publish scope

429

rate_limit_exceeded

Your request is blocked due to exceeding the API rate limit.

5xx



TikTok server or network error. Try again later.



Send Video to TikTok Servers
Note: If you used the source=PULL_FROM_URL to initialize the video export, you can skip this part. The TikTok server will handle the video uploading process for you.

Once you have initialized the video export and received an upload_url, you must send the video file to TikTok for processing. We support many video formats and provide chunking for larger files. Learn more about media transmission.

HTTP URL

Returned in upload_url

HTTP Method

PUT

Note: Use the entire URL returned as the upload_url , including the returned query parameters.

Request
Note: This document provides schemas for the API request and response. Learn more about media upload formats and advanced capabilities.

Header
Field Name

Description

Value

Required

Content-Type

The content format of the body of this HTTP request.

Select from:

video/mp4
video/quicktime
video/webm
true



Content-Length

Byte size of this chunk.

{BYTE_SIZE_OF_THIS_CHUNK}

true



Content-Range

The metadata describing the portion of the overall file contained in this chunk.

bytes {FIRST_BYTE}-{LAST_BYTE}/{TOTAL_BYTE_LENGTH}

true

Body
The binary file data.

Example
curl --location --request PUT 'https://open-upload.tiktokapis.com/upload/?upload_id=67890&upload_token=Xza123' \
--header 'Content-Range: bytes 0-30567099/30567100' \
--header 'Content-Length: 30567100'\
--header 'Content-Type: video/mp4' \
--data '@/path/to/file/example.mp4'
# UPLOAD
Get Started
This guide shows you how to use the Content Posting API to upload content to TikTok.

Prerequisites
To successfully complete this tutorial, you will need the following:

A valid video if you want to upload videos:
Ensure you have a video file in one of the supported formats, such as MP4 + H.264, stored on your local machine.
Alternatively, you can provide a URL of a video from your verified domain or URL prefix. Learn how to verify your domain or URL prefix.
Learn more about video restrictions.
A valid photo if you want to upload photos:
You need to provide a URL of a photo from your verified domain or URL prefix. Learn how to verify your domain or URL prefix.
Learn more about photo restrictions.
A registered app on the TikTok for Developers website.
Add the content posting API product to your app as shown below.

Get approval and authorization of the video.upload scope. Learn more about scopes.
Your app must be approved for the video.upload scope.
The target TikTok user must have authorized your app for the video.upload scope.
The access token and open ID of the TikTok user who authorized your app. Learn how to obtain the access token and open ID.


Upload draft to TikTok
This section demonstrates how to successfully upload videos or photos to TikTok for the user to review and post.

You should inform users that they must click on inbox notifications to continue the editing flow in TikTok and complete the post.


User notified of video upload


User reviews and posts video

Upload a video
To initiate video upload on TikTok's servers, you must invoke the Content Posting API - Video Upload endpoint. You have the following two options:

If you have the video file locally, set the source parameter to FILE_UPLOAD in your request.
if the video is hosted on a URL, set the source parameter to PULL_FROM_URL.
Example
Example using source=FILE_UPLOAD:

Request:

curl --location 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json' \
--data '{
    "source_info": {
        "source": "FILE_UPLOAD",
        "video_size": exampleVideoSize,
        "chunk_size" : exampleVideoSize,
        "total_chunk_count": 1
    }
}'
Response:

200 OK

{
    "data": {
        "publish_id": "v_inbox_file~v2.123456789",
        "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=67890&upload_token=Xza123"    
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F3"
     }
}


Example using source=PULL_FROM_URL:

Request:

curl --location 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json' \
--data '{
    "source_info": {
        "source": "PULL_FROM_URL",
        "video_url": "https://example.verified.domain.com/example_video.mp4",
    }
}'
Response:

200 OK

{
    "data": {
        "publish_id": "v_inbox_url~v2.123456789"
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F4"
     }
}
If you are using source=FILE_UPLOAD:

Extract the upload_url and publish_id from the response data.
Send the video from your local filesystem to the extracted upload_url using a PUT request. The video processing will occur asynchronously once the upload is complete.
curl --location --request PUT 'https://open-upload.tiktokapis.com/video/?upload_id=67890&upload_token=Xza123' \
--header 'Content-Range: bytes 0-30567099/30567100' \
--header 'Content-Type: video/mp4' \
--data '@/path/to/file/example.mp4'
With the publish_id returned earlier, check for status updates using the Get Post Status endpoint.

curl --location 'https://open.tiktokapis.com/v2/post/publish/status/fetch/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json; charset=UTF-8' \
--data '{
    "publish_id": "v_inbox_file~v2.123456789"
}'
Upload photos
To initiate photo upload on TikTok's server, you must invoke the Content Posting API endpoint.

Note:

There are differences between the photo post endpoint and the existing video post endpoint.

Use /v2/post/publish/content/init/ to upload photos instead of /v2/post/publish/inbox/video/init/
The post_mode and media_type are required parameters in request.body
There are additional parameters supported, such as title and description.
Example
Request:

curl --location 'https://open.tiktokapis.com/v2/post/publish/content/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json' \
--data-raw '{
    "post_info": {
        "title": "funny cat",
        "description": "this will be a #funny photo on your @tiktok #fyp"
    },
    "source_info": {
        "source": "PULL_FROM_URL",
        "photo_cover_index": 1,
        "photo_images": [
            "https://tiktokcdn.com/obj/example-image-01.webp",
            "https://tiktokcdn.com/obj/example-image-02.webp"
        ]
    },
    "post_mode": "MEDIA_UPLOAD",
    "media_type": "PHOTO"
}'
Response:

200 OK

{
    "data": {
        "publish_id": "p_pub_url~v2.123456789"
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F3"
     }
}

Upload
Overview
To upload a video without posting it, you must invoke the Content Posting API to do the following:

Initialize the video upload.
Send the video to TikTok servers (not needed if transfer method is PULL_FROM_URL).
This guide provides the API details including the endpoint, request, and response schema.

You should inform users that they must click on inbox notifications to continue the editing flow in TikTok and complete the post.

Initialize Video Upload
To upload a video to a TikTok user's account, the first step is to initialize the upload.

HTTP URL

/v2/post/publish/inbox/video/init/

HTTP Method

POST

Scope

video.upload

Request
Restriction: Each user access_token is limited to 6 requests per minute.

Header
Field Name

Description

Value

Required

Authorization

The token that bears the authorization of the TikTok user, which is obtained through /oauth/access_token/.

Bearer {$UserAccessToken}

true

Content-Type

The content format of the body of this HTTP request.

application/json; charset=UTF-8

true

Body
Field Name

Nested Field

Type

Description

Required

source_info

source


string

The mechanism by which you will provide the video. You can choose from FILE_UPLOAD and PULL_FROM_URL.

true


video_size

int64

The size of the video to be uploaded in bytes.

true for FILE_UPLOAD

chunk_size

int64

The size of the chunk in bytes.

true for FILE_UPLOAD

total_chunk_count

int64

The total number of chunks.

true for FILE_UPLOAD

video_url


string

The URL of the video to be uploaded. The domain or URL prefix of the video_url should already be verified. Learn more about verifying the URL prefix.

true for PULL_FROM_URL


Examples
Example with source=FILE_UPLOAD:

curl --location 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json; charset=UTF-8'
--data '{
    "source_info": {
        "source": "FILE_UPLOAD",
        "video_size": exampleVideoSize,
        "chunk_size" : exampleChunkSize,
        "total_chunk_count": exampleTotalChunkCount
    }
}'
Example withsource=PULL_FROM_URL:

curl --location 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json' \
--data '{
    "source_info": {
        "source": "PULL_FROM_URL",
        "video_url": "https://example.verified.domain.com/example_video.mp4"
    }
}'
Response
Field Name

Nested Field

Type

Description

data

publish_id


string


An identifier to track the posting action, which you can use to check the status.

The maximum length of this field is 64.

upload_url


string


The URL provided by TikTok where the video file can be uploaded.

The maximum length of this field is 256. This field is only for source=FILE_UPLOAD.

error

code

string

You can decide whether the request is successful based on the error code. Any code other than ok indicates the request did not succeed. Learn more about error codes.

message

string

A human readable description of the error.

logid

string

A unique identifier for the execution of this request.

Note: The upload_url is valid for one hour after issuance. The upload must be completed in this time range.

Example
200 OK
{
    "data": {
        "publish_id": "v_inbox_file~v2.123456789",
        "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=12345&upload_token=Xza123"    
    },
    "error": {
         "code": "ok",
         "message": "",
         "log_id": "202210112248442CB9319E1FB30C1073F3"
     }
}
Error codes
HTTP status code

Error code

Descrption


400

invalid_param

Check error message for details.

403


spam_risk_too_many_pending_share


The daily upload cap from the API is reached for the current user.

To reduce spamming, TikTok limits the number of videos that can be uploaded via API that are not pending approval and posting by the creator. There may be at most 5 pending shares within any 24-hour period.

spam_risk_user_banned_from_posting

The user is banned from making new posts.

url_ownership_unverified


To use PULL_FROM_URL as the video transfer method, the developer must verify the ownership of the URL prefix or domain. Refer to this doc for more details.

401

access_token_invalid

The access_token for the TikTok user is invalid or has expired.

scope_not_authorized

The access_token does not bear user's grant on video.upload scope.

429

rate_limit_exceeded

Your request is blocked due to exceeding the API rate limit.

5xx

TikTok server or network error. Try again later.

Send Video to TikTok Servers
Note: If you used the source=PULL_FROM_URL to initialize the video upload, you can skip this part. The TikTok server will handle the video uploading process for you.

Once you have initialized the video upload and received an upload_url, you must send the video file to TikTok for processing. Many video formats are supported and chunking is provided for larger files. Learn more about media transmission.

HTTP URL

Returned in upload_url

HTTP Method

PUT

Important: Use the entire URL returned as the upload_url including the returned query parameters.

Request
Header
Field Name

Description

Value

Required

Content-Type

The content format of the body of this HTTP request.


Select from:

video/mp4
video/quicktime
video/webm
true

Content-Length

Byte size of this chunk.

{BYTE_SIZE_OF_THIS_CHUNK}

true


Content-Range

Metadata describing the portion of the overall file contained in this chunk.

bytes {FIRST_BYTE}-{LAST_BYTE}/{TOTAL_BYTE_LENGTH}

true

Body
The binary file data.

Example
curl --location --request PUT 'https://open-upload.tiktokapis.com/video/?upload_id=67890&upload_token=Xza123' \
--header 'Content-Range: bytes 0-30567099/30567100' \
--header 'Content-Length: 30567100'\
--header 'Content-Type: video/mp4' \
--data '@/path/to/file/example.mp4'
Edit Images
The image edits endpoint lets you:

Edit existing images
Generate new images using other images as a reference
Edit parts of an image by uploading an image and mask indicating which areas should be replaced (a process known as inpainting)
Create a new image using image references
You can use one or more images as a reference to generate a new image.

In this example, we'll use 4 input images to generate a new image of a gift basket containing the items in the reference images.

import base64
from openai import OpenAI
client = OpenAI()

prompt = """
Generate a photorealistic image of a gift basket on a white background 
labeled 'Relax & Unwind' with a ribbon and handwriting-like font, 
containing all the items in the reference pictures.
"""

result = client.images.edit(
    model="gpt-image-1",
    image=[
        open("body-lotion.png", "rb"),
        open("bath-bomb.png", "rb"),
        open("incense-kit.png", "rb"),
        open("soap.png", "rb"),
    ],
    prompt=prompt
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("gift-basket.png", "wb") as f:
    f.write(image_bytes)



###

Customize Image Output
You can configure the following output options:

Size: Image dimensions (e.g., 1024x1024, 1024x1536)
Quality: Rendering quality (e.g. low, medium, high)
Format: File output format
Compression: Compression level (0-100%) for JPEG and WebP formats
Background: Transparent or opaque
size, quality, and background support the auto option, where the model will automatically select the best option based on the prompt.

Size and quality options
Square images with standard quality are the fastest to generate. The default size is 1024x1024 pixels.

Available sizes	
1024x1024 (square)
1536x1024 (landscape)
1024x1536 (portrait)
auto (default)
Quality options	
low
medium
high
auto (default)
Output format
The Image API returns base64-encoded image data. The default format is png, but you can also request jpeg or webp.

If using jpeg or webp, you can also specify the output_compression parameter to control the compression level (0-100%). For example, output_compression=50 will compress the image by 50%.

Using jpeg is faster than png, so you should prioritize this format if latency is a concern.

Transparency
The gpt-image-1 model supports transparent backgrounds. To enable transparency, set the background parameter to transparent.

It is only supported with the png and webp output formats.

Transparency works best when setting the quality to medium or high.


import openai
import base64

response = openai.responses.create(
    model="gpt-4.1-mini",
    input="Draw a 2D pixel art style sprite sheet of a tabby gray cat",
    tools=[
        {
            "type": "image_generation",
            "background": "transparent",
            "quality": "high",
        }
    ],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]

    with open("sprite.png", "wb") as f:
        f.write(base64.b64decode(image_base64))




##Analyze Images 

Analyze images
Vision is the ability for a model to "see" and understand images. If there is text in an image, the model can also understand the text. It can understand most visual elements, including objects, shapes, colors, and textures, even if there are some limitations.

Giving a model images as input
You can provide images as input to generation requests either by providing a fully qualified URL to an image file, or providing an image as a Base64-encoded data URL.

You can provide multiple images as input in a single request by including multiple images in the content array, but keep in mind that images count as tokens and will be billed accordingly.

import base64
from openai import OpenAI

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "path_to_your_image.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)

completion = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "user",
            "content": [
                { "type": "text", "text": "what's in this image?" },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ],
)

print(completion.choices[0].message.content)

Specify image input detail level
The detail parameter tells the model what level of detail to use when processing and understanding the image (low, high, or auto to let the model decide). If you skip the parameter, the model will use auto.

"image_url": {
    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
    "detail": "high"
},

You can save tokens and speed up responses by using "detail": "low". This lets the model process the image with a budget of 85 tokens. The model receives a low-resolution 512px x 512px version of the image. This is fine if your use case doesn't require the model to see with high-resolution detail (for example, if you're asking about the dominant shape or color in the image).

On the other hand, you can use "detail": "high" if you want the model to have a better understanding of the image.
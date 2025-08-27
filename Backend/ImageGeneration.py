import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import dotenv_values
import os
from time import sleep

# ------------------------
# Load API Key from .env
# ------------------------
env = dotenv_values(".env")
HUGGINGFACE_API_KEY = env.get("HuggingFaceAPIKey")

if not HUGGINGFACE_API_KEY:
    print("Hugging Face API key not found in .env")
    exit(1)

# ------------------------
# Function to display images
# ------------------------
def open_images(prompt):
    folder_path = r"Data"  # Folder where images are stored
    prompt_clean = prompt.replace(" ", "_")
    Files = [f"{prompt_clean}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

# ------------------------
# Hugging Face API details
# ------------------------
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# ------------------------
# Async request to Hugging Face
# ------------------------
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload, timeout=60)
        if response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            return None
        return response.content
    except Exception as e:
        print(f"Request error: {e}")
        return None

# ------------------------
# Generate images async
# ------------------------
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
            "options": {"wait_for_model": True}
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    # Save images
    prompt_clean = prompt.replace(" ", "_")
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join("Data", f"{prompt_clean}{i+1}.jpg")
            try:
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Saved image: {file_path}")
            except Exception as e:
                print(f"Error saving image {file_path}: {e}")

# ------------------------
# Wrapper function
# ------------------------
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# ------------------------
# Main loop
# ------------------------
while True:
    try:
        with open(r"Frontend/Files/ImageGenration.data", "r") as f:
            Data: str = f.read().strip()

        if not Data:
            sleep(1)
            continue

        Prompt, Status = Data.split(",")

        if Status.strip() == "True":
            print("Generating Images ...")
            GenerateImages(prompt=Prompt.strip())

            # Reset the status after generation
            with open(r"Frontend/Files/ImageGenration.data", "w") as f:
                f.write("False,False")
            break  # Exit after one request

        else:
            sleep(1)

    except Exception as e:
        print(f"Error in main loop: {e}")
        sleep(1)

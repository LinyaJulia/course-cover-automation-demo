import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
from openai import OpenAI
import requests


# Generate Image Function
# Generates an image based on an EPA Description
def generate_img_with_overlay(epa_desc):
    img = None
    return img

# Get App Overlay
# Based on the value of the app chosen,
# returns the overlay template to use.
# returns the proper link
def get_app_overlay(app):
    if app == "None":
        return None
    elif app == "Canva":
        link = "overlay-template-db/chatgpt.png"
    elif app == "ChatGPT":
        link = "overlay-template-db/chatgpt.png"
    
    return link
    
# Overlay Images
# Takes a GPT generated image and takes an image overlay template
# Puts overlay template on top of the GPT generated image
def overlay_img(base_img_link, overlay_link):

    # Open images
    base_img = Image.open(base_img_link)
    overlay = Image.open(overlay_link)

    # Ensure im2 has an alpha channel
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    # Create a new blank image with the desired dimensions (1792x1024) and the same mode as im2
    final_img = Image.new(mode='RGBA', size=(1792, 1024))

    # Calculate the position to paste im1 so that it appears on the right side
    # Since im1 is square, its width is equal to the height
    im1_width = base_img.height  # Assuming im1 is square
    paste_position = (1792 - im1_width, 0)  # This will place im1 on the right side

    # Paste im1 onto final_img at the calculated position
    final_img.paste(base_img, paste_position)

    # Paste im2 on top of final_img (and thus on top of im1), using its alpha channel as a mask
    final_img.paste(overlay, (0, 0), overlay)

    return final_img


# Generate Image (with Overlay)
# Generates an image based on an epa description
# Returns the image link
def generate_img_with_overlay(epa_desc, with_overlay):

    if with_overlay:
        size_option = "1024x1024"
    else:
        size_option = "1792x1024"

    response = st.session_state.openai_client.images.generate(
    model="dall-e-3",
    prompt="""
        # CONTEXT
        Before you create an image, refer to this as context. 
        Your task is to create the most ideal background image for a course given a description using this specific prompt template: 
        Create a simple and straightforward stock-photo-like image of [TARGET ACTION OF THE IMAGE]. Do not use holographs. Blur the background. The subject should be on the right third of the composition. The image should be in the style of: 30 — megapixel. Settings: n: 1 size: 1024x1024 quality:hd style: illustrative
        You need to fill in the variable [TARGET ACTION OF THE IMAGE] to complete the prompt. To do this, create a simple NON FUTURISTIC NO HOLOGRAPHS image target based on a description of the course. If the description is related to AI, you can MAKE THE PERSON USE A COMPUTER AND SHOW THE FRONT OF THE COMPUTER SCREEN. The variable must be simple and straightforward. The variable must be focused on the task or action that is stated in the description. Here are some examples of a good image target: The back view of a person wearing business casual clothing showing a computer to calculate excel formulas. A woman from client support happily talking to someone on the phone to answer a question. Two office workers having a conversation to discuss the findings of a meeting. 
        Now, here's an example of a filled out template:
        Create a simple and straightforward stock-photo-like image of The back view of a person wearing business casual clothing showing a computer to calculate excel formulas. Do not use holographs. Blur the background. The subject should be on the right third of the composition. The image should be in the style of: 30 — megapixel  Settings: n: 1 size: 1024x1024 quality:hd style: illustrative
        # INSTRUCTIONS
        Now you are ready. Do this step-by-step:
        1) read the epa description:
        """ + epa_desc + """ 
        2) Create the image target variable. 
        3) Then, create the image based on the prompt and image target variable.
        Make sure the final image is a square image
        """,
    size=size_option,
    quality="standard",
    n=1,
    )
    # URL of the image
    image_url = response.data[0].url

    # Send a GET request to the image URL
    response = requests.get(image_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open a file in binary write mode
        with open("generated_image.jpg", "wb") as file:
            # Write the content of the response to the file
            file.write(response.content)
    return "generated_image.jpg"


# Uses ai to detect what app is being used based on the epa description
def detect_app(epa_desc):
    response = st.session_state.openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "Your task is to identify what software is being used based on a description. You are only allowed to return the name of the software. If no software is used, reply None. If multiple software are used, choose the main option. \n\nLastly, make sure to only choose between these options:\n\nChatGPT\nCanva\nNone"
    },
    {
      "role": "user",
      "content": "This EPA focuses on utilizing the capabilities of the custom GPT 'Using the custom GPT \"Meeting summarizer\" to summarize meetings for Hubspot' for specific organizational tasks and objectives, ensuring effective implementation and usage."
    },
    {
      "role": "assistant",
      "content": "ChatGPT"
    },
    {
      "role": "user",
      "content": "This EPA focuses on how to run a daily huddle by following the specific format for daily huddles."
    },
    {
      "role": "assistant",
      "content": "None"
    },
    {
      "role": "user",
      "content": epa_desc
    }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    return response.choices[0].message.content  



def main():
    st.header("Course Cover Automation Demo")
    st.markdown("""To use the demo, first choose between two tabs. The first tab 'Manual App Input' requires you to input an EPA Description
                and choose from a drop-down of software that is being used based on the software description. The second tab 'Automatic App Detection'
                shows how AI is also capable of identifying the software being used based on the EPA Description. However, this method may not be
                the most reliable method. """)

    # Setting OpenAI Keys and Clients
    if "api_key" not in st.session_state:
        st.session_state.api_key = None
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = None
    with st.sidebar:
        openai_key = st.text_input(
                "OpenAI API Key", 
                key="Open AI Api Key", 
                help="To use this app, you will need to have an OpenAI API Key. Access it from this link: https://platform.openai.com/account/api-keys")
        st.write("To use this app, you will need to have an OpenAI API Key. Access it from this link: https://platform.openai.com/account/api-keys")

        if openai_key:
            st.session_state.api_key = openai_key
            st.session_state.openai_client = OpenAI(api_key=st.session_state.api_key)

    # Two tabs: One of w/out AI, One w AI
    tab1, tab2 = st.tabs(["Manual App Input", "Automatic App Detection"])

    with tab1: 
        # text input for epa description
        epa_desc_manual = st.text_input("Input EPA Description", key=0)
        app = st.selectbox("Choose an app. If none is used, choose None.", 
            ("None", "Canva", "ChatGPT"))
        run_btn_manual = st.button("Generate Image", key='btn_0')
        if run_btn_manual: 
            with st.spinner():
                # Generate Image
                overlay_image = get_app_overlay(app)
                if overlay_image:
                    base_image = generate_img_with_overlay(epa_desc_manual, True)
                    final_image = overlay_img(base_image, overlay_image)
                    final_image.save("final_img.png")
                    st.image(final_image)
                else:
                    base_image = generate_img_with_overlay(epa_desc_manual, False)
                    st.image(base_image)

    with tab2:
        epa_desc_auto = st.text_input("Input EPA Description", key=1)
        run_btn_auto = st.button("Generate Image", key='btn_1')

        if run_btn_auto: 
            with st.spinner():
                chosen_app = detect_app(epa_desc_auto)
                overlay_image = get_app_overlay(chosen_app)
                if overlay_image:
                    base_image = generate_img_with_overlay(epa_desc_auto, True)
                    final_image = overlay_img(base_image, overlay_image)
                    final_image.save("final_img.png")
                    st.image(final_image)
                else:
                    base_image = generate_img_with_overlay(epa_desc_auto, False)
                    st.image(base_image)


if __name__ == '__main__':
    main()
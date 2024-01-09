import base64
import requests
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

# Clarifai Food Recognition Model
def get_food_info(image):
    PAT = '11d78xxxxxxxxxxxxx'  # Your Clarifai Personal Access Token
    USER_ID = 'clarifai'
    APP_ID = 'main'
    MODEL_ID = 'food-item-v1-recognition'
    MODEL_VERSION_ID = 'ftyxxxxxxxxxxxxx'

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=image  # Pass the image content as bytes
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)
    
    food_info = [concept.name for concept in post_model_outputs_response.outputs[0].data.concepts]
    return food_info



# Llama-2 Recipe Generation
def generate_food_suggestion(food_info):
    USER_ID = 'hackathon-hubert'  # Your user ID
    PAT = '10d7dcxxxxxxxxxxxxxxx'  # Your Clarifai Personal Access Token
    USER_ID = 'hackathon-hubert'
    APP_ID = 'Llama-2'  # Your app ID
    MODEL_ID = 'llama2-70b-chat'  # Your model ID
    MODEL_VERSION_ID = '6c27e86364ba4xxxxxxxxxxxxxxx'  # Your model version ID

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)
    
    i_prompt = f"Generate food suggestions using these ingredients: {', '.join(food_info)}"
    output_prompt = f"{i_prompt} Assistant: "

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        text=resources_pb2.Text(raw=output_prompt)
                    )
                )
            ]
        ),
        metadata=metadata
    )

    # Process the response and extract the generated suggestion
    generated_recipes = ""
    if post_model_outputs_response.status.code == status_code_pb2.SUCCESS:
        for idx, output in enumerate(post_model_outputs_response.outputs):
            if idx > 0:
                generated_recipes += "\n"
            recipe_lines = output.data.text.raw.strip().split('\n')
            formatted_recipe = '\n'.join(['\n'.join(recipe_lines[i:i+2]) for i in range(0, len(recipe_lines), 2)])
            generated_recipes += f"Generated Suggestion:\n{formatted_recipe}\n"
    else:
        generated_recipes = f"Failed to generate suggestion. Status: {post_model_outputs_response.status.description}"
    
    return generated_recipes






# Streamlit UI
import streamlit as st

def main():
    st.set_page_config(page_title="Your Food Waste Expert", layout="centered")
    st.title("Food-GPT")

    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        food_info = get_food_info(uploaded_file.read())
        
        if st.button("Generate recipes"):
            generated_recipes = generate_food_suggestion(food_info)
            st.subheader("This is how you should deal with the food:")
            st.write(generated_recipes)

if __name__ == "__main__":
    main()
import streamlit as st
import boto3
import json
from botocore.exceptions import NoCredentialsError
from io import BytesIO
from PIL import Image

def main():
    st.title("AIID (beta) MOM")
    
    if "image_key" not in st.session_state:
        st.session_state.image_key = ""

    getS3FileListDisplay()

# AWS S3 configuration
#aws_access_key_id = 'AKIARDQRY2X7MPP6WADQ'
#aws_secret_access_key = '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'
#bucket_name = 'ogp-hack-test'
#json_folder_path = 'json/'
#image_folder_path = 'image/'
aws_access_key_id = st.secrets["aws_access_key_id"]
aws_secret_access_key = st.secrets["aws_secret_access_key"]
bucket_name = st.secrets["bucket_name"]
json_folder_path = 'JSON/'
image_folder_path = 'IMAGES/'
#file_key = 'json/ogphack_json_sample.txt'  # Replace with the key of your S3 file
#image_key = 'image/leg_scratch.png'

def getS3Image():
    # Connect to S3
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    st.subheader("IMAGE OF INJURY (Attachment)")
    if st.session_state.image_key:
        try:
            # Download image from S3
            response = s3.get_object(Bucket=bucket_name, Key=st.session_state.image_key)
            image_data = response['Body'].read()

            # Display the image using PIL
            image = Image.open(BytesIO(image_data))
            st.image(image, caption="Image", use_column_width=True)

        except NoCredentialsError:
            st.error("AWS credentials not available or incorrect. Please set your AWS access key and secret key.")
        except Exception as e:
            st.error("No available attachment")
    else:
        st.text("No available attachment")


def getS3FileList():
    # Connect to S3
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        # List objects in the bucket
        response = s3.list_objects(Bucket=bucket_name, Prefix=json_folder_path)

        # Extract file names from the response
        file_names = [obj['Key'] for obj in response.get('Contents', [])]
        st.write(file_names)
        if file_names:
            st.write("List of Reported Incidents:")
            for file_name in file_names:
                st.write(file_name)
        else:
            st.info("No files found in the S3 bucket.")

    except Exception as e:
        st.error(f"Error listing files in S3 bucket: {str(e)}")

def getS3FileListDisplay():
    # Connect to S3
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Streamlit app
    #st.title(f"List of Files in S3 Folder: {json_folder_path}")
    st.subheader("List of Reported Incidents:")

    try:
        # List objects in the folder
        #response1 = s3.list_objects(Bucket=bucket_name)
        #st.write(response1)
                                   
        response = s3.list_objects(Bucket=bucket_name, Prefix=json_folder_path)

        # Extract file names from the response
        file_names = [obj['Key'] for obj in response.get('Contents', [])]

        if file_names:
            # Display file list in a dropdown
            selected_file = st.selectbox("", file_names)

            if st.button("View Incident Details"):
                # Display the selected file content on another page
                #st.write(f"Selected File: {selected_file}")
                file_content = s3.get_object(Bucket=bucket_name, Key=selected_file)['Body'].read().decode('utf-8')
                #st.code(file_content, language='json')  # Adjust language parameter based on file type
                dispay_personal_particulars_bot(str(file_content))
                getS3Image()

        else:
            st.info(f"No files found in the folder '{json_folder_path}'.")

    except Exception as e:
        st.error(f"Error listing files in S3 folder: {str(e)}")


def read_json(json_text):
    try:
        json_data = json.loads(json_text)
        return json_data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None

def dispay_personal_particulars_bot(txt):
    
    start_index = txt.find("{")
    end_index = txt.rfind("}")
    json_part = txt[start_index:end_index+1]
    
    #st.write(json_part)
    json_data = read_json(json_part)
    if json_data:
        for key, value in json_data.items():
            st.subheader(f"{key.upper()}:")
            if isinstance(value, dict):
                # Display nested key-value pairs
                for sub_key, sub_value in value.items():
                    st.markdown(f"**{sub_key}:**")
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{sub_value}")
                    if sub_key == "Image of injury":
                        st.session_state.image_key = sub_value
            elif isinstance(value, list):
                # Display list elements
                for item in value:
                    if isinstance(item, dict):
                        # Display nested key-value pairs within the list
                        for sub_key, sub_value in item.items():
                            st.markdown(f"**{sub_key}:**")
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{sub_value}")
                    else:
                        st.text(f"{item}")
            else:
                # Display regular key-value pairs
                st.text(f"{value}")
    else:
        st.warning("No valid JSON data to display.")

if __name__ == "__main__":
    main()

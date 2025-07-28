import requests
import json
import re

def stream_chat_completion(access_token, user_message, api_url=None):
    """
    Call the streaming chat completion API

    Parameters:
        access_token (str): Authentication token
        user_message (str): User message content
        api_url (str, optional): API URL, defaults to GeoGPT service

    Returns:
        list: List containing all response chunks
    """
    # Set default API URL
    if api_url is None:
        api_url = "https://geogpt.zero2x.org.cn/be-api/service/api/model/v1/chat/completions"

    # Prepare request headers and data
    headers = {
        "authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": True
    }

    responses = []  # Store all response chunks

    try:
        # Send POST request (enable streaming response)
        with requests.post(api_url, headers=headers, json=payload, stream=True) as response:
            # Check response status
            response.raise_for_status()

            print(f"Response status code: {response.status_code}")
            print("Starting to receive streaming response...")

            # Process streamed responses
            for chunk in response.iter_lines():
                # Filter out keep-alive new lines
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')

                    try:
                        # Handle possible Server-Sent Events (SSE) format
                        if decoded_chunk.startswith("data:"):
                            json_str = decoded_chunk[5:]
                        else:
                            json_str = decoded_chunk

                        # Check for message event tag
                        if json_str == 'event:message':
                            continue
                        # Check for end flag
                        if json_str.strip() == "[DONE]":
                            print("\nReceived end flag [DONE]")
                            break
                            
                        # Unescape handling:
                        # 1. Replace \" with "
                        # 2. Replace \\ with \
                        unescaped_str = json_str.replace('\\"', '"').replace('\\\\', '\\')

                        if unescaped_str.startswith('"') and unescaped_str.endswith('"'):
                            # Remove outer quotes
                            unescaped_str = unescaped_str[1:-1]

                        # Parse JSON
                        data = json.loads(unescaped_str)
                        responses.append(data)  # Save response

                        # Extract and print content
                        if 'choices' in data and data['choices']:
                            choice = data['choices'][0]
                            # Check if delta field exists
                            if 'delta' in choice:
                                content = choice['delta'].get('content', '')
                                if content:
                                    print(content, end='', flush=True)

                    except json.JSONDecodeError as e:
                        print(f"\nFailed to parse JSON: {decoded_chunk}")
                        print(f"Error details: {str(e)}")
                    except Exception as e:
                        print(f"\nProcessing error: {str(e)}")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {str(e)}")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

    return responses


if __name__ == "__main__":
    """Main function demonstrating API call"""
    # Configuration parameters
    access_token = "sk-E9ZjEK01SiYTG78KDDUF"  # Replace with actual access token
    user_message = "你好，请介绍一下中国的长江"

    print(f"Sending message: {user_message}")
    print("Waiting for AI reply...\n")

    # Call API
    responses = stream_chat_completion(access_token, user_message)

    # Print response summary
    print("\n\n===== Response Summary =====")
    print(f"Received {len(responses)} response chunks")

    # Extract full reply content
    full_content = ""
    for response in responses:
        if 'choices' in response and response['choices']:
            #content = response['choices'][0].get('delta', {}).get('content', '')
            content = response['choices'][0]['delta']['content']
            full_content += content

    print("\nFull reply content:")
    print(full_content)
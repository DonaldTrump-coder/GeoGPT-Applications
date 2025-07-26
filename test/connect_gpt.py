import requests

access_token="sk-E9ZjEK01SiYTG78KDDUF"
url="https://geogpt.zero2x.org.cn/be-api/service/api/geoChat/generate"

def create_session():
    headers={
        "Authorization": f"Bearer {access_token}"
    }
    try:
        response=requests.get(url,headers=headers,timeout=10)

        # Attempt to parse JSON response, fallback to text on failure
        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text
                
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response_data
        }
    
    except requests.exceptions.RequestException as e:
        # Encapsulate error details
        error_info = {
            'error_type': type(e).__name__,
            'error_message': str(e)
        }
        if isinstance(e, requests.exceptions.Timeout):
            error_info['timeout'] = 10
        raise requests.exceptions.RequestException(f"请求失败: {error_info}") from e

if __name__=="__main__":
    try:
        result=create_session()
        print(f"Response status code: {result['status_code']}")
        print(f"Response data: {result['data']}")
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
import requests
import sys

def test_api():
    # create dummy file
    with open("dummy.mp3", "wb") as f:
        f.write(b"dummy audio content")
    
    files = {'file': ('dummy.mp3', open("dummy.mp3", "rb"))}
    data = {'user_id': "test"}
    try:
        res = requests.post("http://127.0.0.1/api/voice", files=files, data=data, timeout=10)
        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test_api()

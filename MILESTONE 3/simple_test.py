import requests

# Simple test
base_url = "http://localhost:5000"

# Step 1: Create a chat
print("1. Creating chat...")
create_response = requests.post(
    f"{base_url}/api/chat/new",
    headers={"Content-Type": "application/json"},
    json={}
)
if create_response.status_code == 200:
    result = create_response.json()
    chat_id = result.get('chat_id') or result.get('id')
    print(f"✅ Chat created with ID: {chat_id}")
    print(f"Response: {result}")
else:
    print(f"❌ Failed to create chat: {create_response.text}")
    exit(1)

# Step 2: Create test file
print("\n2. Creating test document...")
with open("simple_test.txt", "w") as f:
    f.write("This is a simple test document about quantum computing.")
print("✅ Test file created")

# Step 3: Upload
print("\n3. Uploading document...")
try:
    with open("simple_test.txt", "rb") as f:
        files = {"file": ("simple_test.txt", f, "text/plain")}
        response = requests.post(f"{base_url}/api/chat/{chat_id}/upload", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("\n✅ UPLOAD SUCCESSFUL!")
        print(f"\nDocument ID: {result['document']['id']}")
        print(f"Summary: {result['document']['summary']}")
        print(f"Genuineness Score: {result['document']['genuineness_score']}/10")
        print(f"Is Genuine: {result['document']['is_genuine']}")
    else:
        print(f"❌ Upload failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

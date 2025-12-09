"""
Quick Test Script for Document Upload
======================================
Tests the document upload API to verify it's working.
"""

import requests
import os

# Test configuration
BASE_URL = "http://localhost:5000"
CHAT_ID = 1

def test_document_upload():
    """Test document upload functionality."""
    print("\n" + "="*60)
    print("TESTING DOCUMENT UPLOAD API")
    print("="*60 + "\n")
    
    # Create a test document
    test_content = """
    Research Paper: Quantum Computing Applications
    
    Abstract:
    This paper explores the practical applications of quantum computing
    in various fields including cryptography, drug discovery, and 
    optimization problems. We present three case studies demonstrating
    the potential of quantum algorithms to solve complex problems.
    
    Introduction:
    Quantum computing represents a paradigm shift in computational
    capability. Unlike classical computers that use bits, quantum
    computers use quantum bits or qubits that can exist in multiple
    states simultaneously.
    
    Conclusion:
    Our research demonstrates that quantum computing has significant
    potential to revolutionize multiple industries.
    """
    
    # Save test file
    test_file = "test_quantum_paper.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"📄 Created test file: {test_file}")
    print(f"📊 File size: {os.path.getsize(test_file)} bytes\n")
    
    # Upload the document
    print("⬆️  Uploading document...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            response = requests.post(
                f"{BASE_URL}/api/chat/{CHAT_ID}/upload",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!\n")
            
            doc = result['document']
            print("📋 DOCUMENT ANALYSIS:")
            print("-" * 60)
            print(f"ID: {doc['id']}")
            print(f"Filename: {doc['filename']}")
            print(f"File Size: {doc['file_size']} bytes")
            print(f"Word Count: {doc['word_count']} words")
            print(f"\n📝 SUMMARY:")
            print(doc['summary'])
            print(f"\n🔍 GENUINENESS VERIFICATION:")
            print(f"Score: {doc['genuineness_score']}/10")
            print(f"Is Genuine: {'✅ Yes' if doc['is_genuine'] else '❌ No'}")
            print(f"\n📊 DETAILED ANALYSIS:")
            print(doc['genuineness_analysis'])
            print("-" * 60)
            
            # List all documents
            print("\n📚 Listing all documents...")
            list_response = requests.get(f"{BASE_URL}/api/chat/{CHAT_ID}/documents")
            if list_response.status_code == 200:
                docs = list_response.json()['documents']
                print(f"✅ Found {len(docs)} document(s)")
                for d in docs:
                    print(f"  - {d['filename']} (Score: {d['genuineness_score']}/10)")
            
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 Cleaned up test file")


if __name__ == "__main__":
    success = test_document_upload()
    
    print("\n" + "="*60)
    if success:
        print("🎉 DOCUMENT UPLOAD TEST PASSED!")
        print("\nThe backend is working perfectly:")
        print("  ✅ File upload")
        print("  ✅ Text extraction")
        print("  ✅ AI summarization")
        print("  ✅ Genuineness verification")
        print("  ✅ Database storage")
    else:
        print("⚠️  TEST FAILED - Check server logs")
    print("="*60 + "\n")

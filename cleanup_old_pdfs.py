"""
Clean up old PDF uploads from Pinecone
"""
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX', 'shop-catalog'))

print("🧹 Cleaning up old PDF documents from Pinecone...\n")

# Delete both old uploads
old_docs = [
    'doc_20260214_201655',
    'doc_20260214_204307',
    'doc_20260215_193744'
]

for doc_id in old_docs:
    print(f"   Deleting {doc_id}...")
    try:
        # Delete all chunks for this document
        index.delete(filter={'document_id': doc_id})
        print(f"   ✅ Deleted\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

print("✅ Cleanup complete!")
print("\nNow upload your PDF again through the admin interface.")

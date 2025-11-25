from tavily import TavilyClient
import textwrap

print("\n Tavily Research Assistant")
print("------------------------------------------------------------")

query = input("Enter your research query: ").strip()

if not query:
    print("\n A research query is required.")
    exit()

print("\n⏳ Collecting relevant information from the web...\n")

# Add Your API Key Here
client = TavilyClient(api_key="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")

# Fetch results
response = client.search(query=query, max_results=8)

# --- REMOVE DUPLICATES (important) -
unique_items = []
seen_titles = set()

for item in response["results"]:
    title = item.get("title", "").strip()

    # skip empty title results
    if not title:
        continue

    # skip if duplicate
    if title in seen_titles:
        continue

    seen_titles.add(title)
    unique_items.append(item)

# Keep only top 3 clean results
unique_items = unique_items[:3]

# ---------------------------------------------------------

print("                    📘 RESEARCH SUMMARY")
print(f"\n Query: {response.get('query', query)}")
print("------------------------------------------------------------\n")

print("Top Clean Sources Retrieved:\n")

if not unique_items:
    print("No valid, unique sources found.")
else:
    for idx, item in enumerate(unique_items, start=1):

        print(f"----------------------  SOURCE {idx}  ----------------------")

        title = item.get("title", "Untitled Source")
        url = item.get("url", "No URL Available")
        content = item.get("content", "No content available")

        print(f"Title: {title}")
        print(f"URL: {url}\n")

        print("Content Preview:")
        print(textwrap.fill(content[:600] + "...", width=90))
        print("------------------------------------------------------------\n")

print("Research Completed Successfully")
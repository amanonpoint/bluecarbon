# main.py
import asyncio
from helper.core import RagOrchestrator
from helper.prep_citation import create_section_html_from_chunk  # optional, already default


async def main():
    orch = RagOrchestrator(
        # agar env me GROQ_API_KEY set hai to api_key pass karna optional hai
        prep_citations_func=create_section_html_from_chunk,
    )

    session_id = "demo_session"
    user_id = "user_1"

    print("🤖 RAG CLI (type 'exit' or empty line to quit)")
    print("💡 Tip: Use /clear to reset session | /status for debug info")
    
    while True:
        try:
            query = input("\n👤 User: ").strip()
            if not query or query.lower() == 'exit':
                print("👋 Thanks for using RAG CLI!")
                break

            if query.lower() == '/clear':
                print("🧹 Session cleared!")
                continue
                
            if query.lower() == '/status':
                print(f"📊 Session: {session_id} | User: {user_id}")
                print("✅ Ready for queries!")
                continue

            print("🤔 Processing...")
            resp = await orch.process_query(query, session_id=session_id, user_id=user_id)

            print("\n" + "═" * 80)
            print("🤖 Answer")
            print("═" * 80)
            print(resp["answer"])

            print("\n📚 Citations (" + str(len(resp["citations"])) + ")")
            print("─" * 50)
            if not resp["citations"]:
                print("❌ No citations found")
            else:
                for i, c in enumerate(resp["citations"], 1):
                    page = c.get('page', 'N/A')
                    header = c.get('header', 'No header')
                    file_id = c['file_id']
                    chunk_id = c['chunk_id']
                    path = c.get('citation_path', 'N/A')
                    
                    print(f"{i}. 📄 Page {page} | {header}")
                    print(f"   📁 file_id={file_id}, chunk_id={chunk_id}")
                    if path != 'N/A':
                        print(f"   🔗 {path}")

            print("\n🔍 Debug Stats")
            print("─" * 30)
            print(f"Chunks retrieved: {resp.get('chunks_retrieved', 0)}")
            print(f"Citations: {len(resp['citations'])} / {resp.get('citation_limit', 0)}")
            print(f"Intent: {resp.get('intent', 'auto')}")
            print(f"Response time: ~{resp.get('processing_time', 'N/A')}s")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("🔄 Try again or type 'exit' to quit")


if __name__ == "__main__":
    # Fixed: Use asyncio.run() for proper async execution [web:11]
    asyncio.run(main())

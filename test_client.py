import httpx
import json


def main():
    url = "http://127.0.0.1:8001/chat"

    # You can change the query message here!
    payload = {
        "message": "What is the weather in Visakhatpatnam, and give me a summary of US news?",
    }

    print(f"Sending request: {payload['message']}\n")

    try:
        with httpx.stream("POST", url, json=payload, timeout=60.0) as response:
            if response.status_code != 200:
                print(
                    f"Error: Server responded with status code {response.status_code}"
                )
                print(response.read().decode())
                return

            for line in response.iter_lines():
                if not line:
                    continue
                # Server Sent Events output looks like "data: {...}"
                if line.startswith("data:"):
                    raw_data = line[5:].strip()
                    try:
                        event_data = json.loads(raw_data)
                        event_type = event_data.get("event")

                        if event_type == "token":
                            print(event_data.get("content"), end="", flush=True)
                        elif event_type == "tool_start":
                            print(
                                f"\n[🔧 Calling Tool: {event_data.get('tool')}]\n",
                                flush=True,
                            )
                        elif event_type == "tool_end":
                            print(
                                f"\n[✅ Tool {event_data.get('tool')} Finished]\n",
                                flush=True,
                            )
                        elif event_type == "done":
                            print("\n\n[🎉 Response Complete]")
                        elif event_type == "error":
                            print(
                                f"\n❌ Error: {event_data.get('type')} - {event_data.get('detail')}"
                            )
                    except json.JSONDecodeError:
                        pass
    except httpx.ConnectError:
        print(
            "Error: Could not connect to the FastAPI chat server. Make sure `python main.py` is running on port 8001."
        )
    except KeyboardInterrupt:
        print("\nAborted.")


if __name__ == "__main__":
    main()

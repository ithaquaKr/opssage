#!/usr/bin/env python3
"""Test script to verify Telegram HTML link formatting."""

import asyncio
import os
import sys

import httpx


async def test_telegram_html_link():
    """Send a test message with HTML link to Telegram."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("❌ Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        print(f"   BOT_TOKEN set: {bool(bot_token)}")
        print(f"   CHAT_ID set: {bool(chat_id)}")
        sys.exit(1)

    print(f"✓ Bot token: {bot_token[:20]}...")
    print(f"✓ Chat ID: {chat_id}")

    # Test URL
    test_url = "http://localhost:3000/incidents/test-123"

    # Test different message formats
    messages = [
        {
            "name": "HTML link format",
            "text": '<b>Test Message 1</b>\n\n<a href="http://localhost:3000/incidents/test-123">Click Here</a>',
            "parse_mode": "HTML",
        },
        {
            "name": "Markdown link format",
            "text": "*Test Message 2*\n\n[Click Here](http://localhost:3000/incidents/test-123)",
            "parse_mode": "Markdown",
        },
        {
            "name": "MarkdownV2 link format",
            "text": "*Test Message 3*\n\n[Click Here](http://localhost:3000/incidents/test\\-123)",
            "parse_mode": "MarkdownV2",
        },
        {
            "name": "Plain text with URL",
            "text": "Test Message 4\n\nhttp://localhost:3000/incidents/test-123",
            "parse_mode": None,
        },
    ]

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    for i, msg_config in enumerate(messages, 1):
        print(f"\n📤 Sending test {i}/{len(messages)}: {msg_config['name']}")
        print(f"   Parse mode: {msg_config['parse_mode']}")
        print(f"   Text preview: {msg_config['text'][:50]}...")

        payload = {
            "chat_id": chat_id,
            "text": msg_config["text"],
        }

        if msg_config["parse_mode"]:
            payload["parse_mode"] = msg_config["parse_mode"]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()

                if result.get("ok"):
                    print(
                        f"   ✅ Success! Message ID: {result['result']['message_id']}"
                    )
                else:
                    print(f"   ❌ Failed: {result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Wait a bit between messages
        await asyncio.sleep(1)

    print("\n" + "=" * 50)
    print("Test complete! Check your Telegram chat.")
    print("Which message format shows clickable links?")


if __name__ == "__main__":
    asyncio.run(test_telegram_html_link())


#!/bin/bash
# Setup script to configure public URL for Telegram links

echo "🔧 OpsSage Telegram Links Setup"
echo "================================"
echo ""
echo "Telegram requires a PUBLIC URL for clickable links."
echo "Localhost URLs will NOT work."
echo ""
echo "Choose an option:"
echo ""
echo "1) Use ngrok (create temporary public tunnel)"
echo "2) Enter your server's public URL manually"
echo "3) Skip (keep localhost - links won't be clickable)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
1)
    echo ""
    echo "📡 Starting ngrok tunnel to port 3000..."

    # Check if ngrok is installed
    if ! command -v ngrok &>/dev/null; then
        echo "❌ ngrok is not installed"
        echo ""
        echo "Install ngrok:"
        echo "  macOS: brew install ngrok"
        echo "  Linux: snap install ngrok"
        echo "  Or download from: https://ngrok.com/download"
        exit 1
    fi

    # Start ngrok in background
    echo "Starting ngrok..."
    ngrok http 3000 >/dev/null &
    NGROK_PID=$!

    # Wait for ngrok to start
    sleep 2

    # Get the public URL
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1)

    if [ -z "$NGROK_URL" ]; then
        echo "❌ Failed to get ngrok URL"
        kill $NGROK_PID 2>/dev/null
        exit 1
    fi

    echo "✅ Ngrok tunnel created: $NGROK_URL"
    echo ""
    export DASHBOARD_URL="$NGROK_URL"
    ;;

2)
    echo ""
    read -p "Enter your public URL (e.g., https://yourdomain.com): " PUBLIC_URL

    if [[ ! $PUBLIC_URL =~ ^https?:// ]]; then
        echo "❌ URL must start with http:// or https://"
        exit 1
    fi

    export DASHBOARD_URL="$PUBLIC_URL"
    echo "✅ Using URL: $DASHBOARD_URL"
    ;;

3)
    echo ""
    echo "⚠️  Keeping localhost - links will NOT be clickable in Telegram"
    export DASHBOARD_URL="http://localhost:3000"
    ;;

*)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "📝 Setting DASHBOARD_URL=$DASHBOARD_URL"
echo ""

# Update .env file if it exists, or create it
if [ -f .env ]; then
    # Remove old DASHBOARD_URL if exists
    grep -v "^DASHBOARD_URL=" .env >.env.tmp
    mv .env.tmp .env
fi

echo "DASHBOARD_URL=$DASHBOARD_URL" >>.env

echo "✅ Updated .env file"
echo ""
echo "🔄 Restarting backend..."
docker-compose restart backend

echo ""
echo "⏳ Waiting for backend to be ready..."
sleep 5

# Verify the setting
echo ""
echo "🔍 Verifying configuration..."
ACTUAL_URL=$(docker exec opssage-backend python -c "from sages.notifications import get_notifier; print(get_notifier().dashboard_url)" 2>/dev/null)

if [ "$ACTUAL_URL" = "$DASHBOARD_URL" ]; then
    echo "✅ Dashboard URL configured correctly: $ACTUAL_URL"
else
    echo "⚠️  Warning: URL mismatch"
    echo "   Expected: $DASHBOARD_URL"
    echo "   Actual: $ACTUAL_URL"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🧪 Test it by sending an alert:"
echo "   curl -X POST http://localhost:8000/api/v1/alerts \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"alert_name\":\"Test\",\"severity\":\"warning\",\"message\":\"Test\",\"labels\":{},\"annotations\":{},\"firing_condition\":\"test\",\"timestamp\":\"2025-12-01T00:00:00Z\"}'"
echo ""
echo "Check your Telegram - the link should now be clickable!"

if [ ! -z "$NGROK_PID" ]; then
    echo ""
    echo "ℹ️  Note: ngrok is running in background (PID: $NGROK_PID)"
    echo "   To stop: kill $NGROK_PID"
    echo "   The tunnel will stop when you close this terminal"
fi


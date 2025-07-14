#!/bin/bash

# Render Deployment Script for Gemini Backend Clone
set -e

echo "🚀 Preparing for Render deployment..."

# Check if render.yaml exists
if [ ! -f render.yaml ]; then
    echo "❌ render.yaml not found!"
    exit 1
fi

echo "📝 Render deployment instructions:"
echo ""
echo "1. 🌐 Go to https://render.com and sign up/login"
echo "2. 📁 Connect your GitHub repository"
echo "3. 🔧 Create a new Blueprint and upload render.yaml"
echo "4. ⚙️ Set the following environment variables in Render dashboard:"
echo "   - GEMINI_API_KEY=your-gemini-api-key-here"
echo "   - STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key"
echo "   - STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key"
echo "   - STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret"
echo "   - STRIPE_PRICE_ID=price_your-pro-subscription-price-id"
echo "   - SECRET_KEY=$(openssl rand -hex 32)"
echo ""
echo "5. 🚀 Deploy the blueprint"
echo "6. 🔗 Configure Stripe webhook URL with your Render app URL"
echo ""
echo "📋 Alternative manual setup:"
echo "1. Create PostgreSQL database"
echo "2. Create Redis instance"
echo "3. Create Web Service from GitHub repo"
echo "4. Set build command: pip install -r requirements.txt"
echo "5. Set start command: python -m uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "✅ Follow the instructions above to complete deployment"


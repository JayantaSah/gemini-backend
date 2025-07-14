#!/bin/bash

# Fly.io Deployment Script for Gemini Backend Clone
set -e

echo "🚀 Deploying to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Fly CLI not found. Installing..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

echo "🔐 Please login to Fly.io if not already logged in:"
flyctl auth login

echo "📦 Launching Fly.io app..."
flyctl launch --no-deploy

echo "🗄️ Creating PostgreSQL database..."
flyctl postgres create --name gemini-postgres --region iad

echo "🔗 Attaching database to app..."
flyctl postgres attach gemini-postgres

echo "🔴 Creating Redis database..."
flyctl redis create --name gemini-redis --region iad

echo "⚙️ Setting secrets..."
flyctl secrets set GEMINI_API_KEY="your-gemini-api-key-here"
flyctl secrets set STRIPE_SECRET_KEY="sk_test_your-stripe-secret-key"
flyctl secrets set STRIPE_PUBLISHABLE_KEY="pk_test_your-stripe-publishable-key"
flyctl secrets set STRIPE_WEBHOOK_SECRET="whsec_your-webhook-secret"
flyctl secrets set STRIPE_PRICE_ID="price_your-pro-subscription-price-id"
flyctl secrets set SECRET_KEY="$(openssl rand -hex 32)"

echo "🚀 Deploying application..."
flyctl deploy

echo "✅ Deployment completed!"
echo "🌐 Your application URL:"
flyctl info

echo ""
echo "⚠️  Don't forget to:"
echo "1. Update secrets with real API keys: flyctl secrets set KEY=value"
echo "2. Configure Stripe webhook URL in Stripe dashboard"
echo "3. Scale your app if needed: flyctl scale count 2"


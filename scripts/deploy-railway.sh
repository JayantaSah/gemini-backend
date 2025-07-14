#!/bin/bash

# Railway Deployment Script for Gemini Backend Clone
set -e

echo "🚀 Deploying to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "🔐 Please login to Railway if not already logged in:"
railway login

echo "📦 Creating new Railway project..."
railway init

echo "🗄️ Adding PostgreSQL database..."
railway add --database postgresql

echo "🔴 Adding Redis database..."
railway add --database redis

echo "⚙️ Setting environment variables..."
railway variables set GEMINI_API_KEY="your-gemini-api-key-here"
railway variables set STRIPE_SECRET_KEY="sk_test_your-stripe-secret-key"
railway variables set STRIPE_PUBLISHABLE_KEY="pk_test_your-stripe-publishable-key"
railway variables set STRIPE_WEBHOOK_SECRET="whsec_your-webhook-secret"
railway variables set STRIPE_PRICE_ID="price_your-pro-subscription-price-id"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"

echo "🚀 Deploying application..."
railway up

echo "✅ Deployment completed!"
echo "🌐 Your application URL:"
railway domain

echo ""
echo "⚠️  Don't forget to:"
echo "1. Update environment variables with real API keys"
echo "2. Configure Stripe webhook URL in Stripe dashboard"
echo "3. Test all endpoints with the provided Postman collection"


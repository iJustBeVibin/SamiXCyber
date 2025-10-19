#!/bin/bash
# Quick script to push to GitHub
# Usage: ./QUICK_PUSH.sh "your commit message"

echo "🚀 Preparing to push to GitHub..."
echo ""

# Check if commit message provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide a commit message"
    echo "Usage: ./QUICK_PUSH.sh \"your commit message\""
    exit 1
fi

# Add all changes
echo "📦 Adding all changes..."
git add -A

# Commit with provided message
echo "💾 Committing changes..."
git commit -m "$1"

# Check if remote exists
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️  No remote 'origin' found!"
    echo "Please set up your GitHub repository first:"
    echo ""
    echo "  git remote add origin https://github.com/YOUR_USERNAME/tech-risk-scorer.git"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Push to GitHub
echo "🌐 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
else
    echo ""
    echo "❌ Push failed. Please check the error message above."
    echo ""
    exit 1
fi

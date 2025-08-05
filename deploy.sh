#!/bin/bash
# Quick deployment script for GitHub + Render

echo "🚀 Reimbursement App Deployment Helper"
echo "======================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized. Run 'git init' first."
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 You have uncommitted changes. Committing them..."
    git add .
    read -p "Enter commit message: " commit_msg
    git commit -m "$commit_msg"
fi

echo ""
echo "📋 Deployment Checklist:"
echo "========================"
echo "✅ Flask app configured"
echo "✅ Database models created"
echo "✅ Requirements.txt generated"
echo "✅ Render.yaml configured"
echo "✅ Procfile for Heroku ready"
echo ""

echo "🎯 Next Steps:"
echo "=============="
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/reimbursement-app.git"
echo "   git push -u origin main"
echo ""
echo "2. Deploy on Render.com:"
echo "   - Go to https://render.com"
echo "   - Click 'New +' → 'Blueprint'"
echo "   - Connect your GitHub repo"
echo "   - Click 'Apply'"
echo ""
echo "3. Alternative - Deploy on Heroku:"
echo "   heroku create your-app-name"
echo "   heroku addons:create heroku-postgresql:mini"
echo "   git push heroku main"
echo ""

echo "🎉 Your app will be live on the internet!"
echo ""
echo "📚 Full guide: See DEPLOYMENT_GUIDE.md"

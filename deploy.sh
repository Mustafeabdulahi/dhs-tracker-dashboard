#!/bin/bash
# Deployment Helper Script

echo "🚀 DHS Tracker Dashboard - Deployment Helper"
echo "============================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📝 Step 1: Initialize Git Repository"
    echo "------------------------------------"
    git init
    git add .
    git commit -m "Initial commit - DHS Tracker Dashboard"
    echo "✅ Git repository initialized"
    echo ""
else
    echo "✅ Git repository already initialized"
    echo ""
fi

# Check if remote exists
if ! git remote | grep -q 'origin'; then
    echo "🔗 Step 2: Add GitHub Remote"
    echo "-----------------------------"
    echo "Please create a GitHub repository first at: https://github.com/new"
    echo ""
    read -p "Enter your GitHub username: " username
    read -p "Enter your repository name: " reponame
    echo ""
    git remote add origin "https://github.com/$username/$reponame.git"
    echo "✅ Remote added: https://github.com/$username/$reponame.git"
    echo ""
else
    echo "✅ GitHub remote already configured"
    echo ""
fi

# Push to GitHub
echo "📤 Step 3: Push to GitHub"
echo "-------------------------"
read -p "Push to GitHub now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git branch -M main
    git push -u origin main
    echo "✅ Code pushed to GitHub!"
    echo ""
fi

# Deployment options
echo "🌐 Step 4: Choose Deployment Platform"
echo "--------------------------------------"
echo ""
echo "Choose your deployment platform:"
echo "  1) Streamlit Community Cloud (RECOMMENDED - FREE)"
echo "  2) Railway (FREE TIER)"
echo "  3) Heroku (FREE TIER)"
echo "  4) Skip for now"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🌟 Deploying to Streamlit Cloud"
        echo "-------------------------------"
        echo ""
        echo "Next steps:"
        echo "  1. Go to: https://share.streamlit.io/"
        echo "  2. Sign in with GitHub"
        echo "  3. Click 'New app'"
        echo "  4. Select your repository"
        echo "  5. Set main file: dashboard_v2.py"
        echo "  6. Click 'Deploy'!"
        echo ""
        echo "Your app will be live in a few minutes! 🎉"
        ;;
    2)
        echo ""
        echo "🚂 Deploying to Railway"
        echo "----------------------"
        echo ""
        echo "Next steps:"
        echo "  1. Go to: https://railway.app/"
        echo "  2. Sign up with GitHub"
        echo "  3. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "  4. Select your repository"
        echo "  5. Railway will auto-deploy!"
        echo ""
        echo "Your app will be live in a few minutes! 🎉"
        ;;
    3)
        echo ""
        echo "☁️  Deploying to Heroku"
        echo "----------------------"
        echo ""
        read -p "Have you installed Heroku CLI? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            heroku login
            read -p "Enter app name (e.g., dhs-tracker-dashboard): " appname
            heroku create "$appname"
            git push heroku main
            heroku open
            echo ""
            echo "✅ Deployed to Heroku!"
        else
            echo ""
            echo "Please install Heroku CLI first:"
            echo "  Mac: brew install heroku/brew/heroku"
            echo "  Linux: curl https://cli-assets.heroku.com/install.sh | sh"
            echo "  Windows: Download from https://devcenter.heroku.com/articles/heroku-cli"
        fi
        ;;
    4)
        echo ""
        echo "Deployment skipped. You can deploy later using DEPLOYMENT_GUIDE.md"
        ;;
    *)
        echo ""
        echo "Invalid choice. Please run again and choose 1-4."
        ;;
esac

echo ""
echo "============================================"
echo "✅ Deployment setup complete!"
echo "============================================"
echo ""
echo "📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md"
echo ""

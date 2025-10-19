# GitHub Setup Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `tech-risk-scorer` (or your preferred name)
3. Description: `Multi-Chain Technical Risk Scoring System for Ethereum and Hedera`
4. Choose: **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/tech-risk-scorer.git

# Verify the remote was added
git remote -v

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Verify Upload

1. Refresh your GitHub repository page
2. You should see all files uploaded
3. The README.md will be displayed on the main page

## Step 4: Set Up GitHub Actions (Optional)

Create `.github/workflows/tests.yml` for automated testing:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v
      env:
        ETHERSCAN_API_KEY: ${{ secrets.ETHERSCAN_API_KEY }}
```

## Step 5: Add Secrets (for CI/CD)

If using GitHub Actions:

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `ETHERSCAN_API_KEY`
4. Value: Your Etherscan API key
5. Click "Add secret"

## Alternative: Using SSH

If you prefer SSH over HTTPS:

```bash
# Add SSH remote
git remote add origin git@github.com:YOUR_USERNAME/tech-risk-scorer.git

# Push
git push -u origin main
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:

1. **Personal Access Token** (recommended):
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate new token with `repo` scope
   - Use token as password when pushing

2. **SSH Key**:
   - Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
   - Add to GitHub: Settings → SSH and GPG keys

### Push Rejected

If push is rejected:

```bash
# Pull first (if repository has changes)
git pull origin main --rebase

# Then push
git push -u origin main
```

## Next Steps

After successful push:

1. ✅ Add repository description and topics on GitHub
2. ✅ Enable GitHub Pages (if you want to host documentation)
3. ✅ Add collaborators (Settings → Collaborators)
4. ✅ Set up branch protection rules (Settings → Branches)
5. ✅ Create issues for future enhancements
6. ✅ Add a LICENSE file if not already present

## Useful Git Commands

```bash
# Check status
git status

# View commit history
git log --oneline

# Create new branch
git checkout -b feature-name

# Push new branch
git push -u origin feature-name

# Pull latest changes
git pull origin main

# View remotes
git remote -v
```

## Repository Badges (Optional)

Add these to your README.md:

```markdown
![Tests](https://github.com/YOUR_USERNAME/tech-risk-scorer/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

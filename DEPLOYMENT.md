# Adaptive SQL Optimizer - Streamlit Cloud Deployment

## 📋 Prerequisites
- GitHub account
- Streamlit Cloud Pro subscription
- MySQL database (can be local or cloud-hosted)

## 🚀 Deployment Steps

### 1. Prepare for GitHub
```bash
git init
git add .
git commit -m "Initial commit: Adaptive SQL Optimizer"
git remote add origin https://github.com/YOUR_USERNAME/Adaptive-SQL-Optimizer.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Click **"New App"**
3. Select:
   - **Repository**: Your-GitHub-Repo
   - **Branch**: main
   - **Main file path**: app.py
4. Click **Deploy**

### 3. Add Secrets in Streamlit Cloud
After deployment, go to your app dashboard:
1. Click the **⋯** menu → **Settings**
2. Go to **Secrets**
3. Add your MySQL credentials in this format:
```toml
[mysql]
host = "your-mysql-host.com"
user = "your_username"
password = "your_password"
database = "sql_optimizer"
port = 3306
```

### 4. Testing Database Connection
- If using local MySQL, you may need a **public/cloud MySQL** service:
  - AWS RDS
  - Google Cloud SQL
  - Azure Database for MySQL
  - PlanetScale
  - DigitalOcean Managed MySQL

---

## 📝 Local Testing
```bash
streamlit run app.py
```

## ⚠️ Important Notes
- **Never commit `secrets.toml`** (already in .gitignore)
- Use remote MySQL database for Streamlit Cloud (localhost won't work)
- Keep `.streamlit/secrets.toml` only for local development
- All sensitive data must be added via Streamlit Cloud dashboard

---

## 🔗 Useful Links
- [Streamlit Cloud Docs](https://docs.streamlit.io/deploy/streamlit-cloud)
- [Managing Secrets](https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app/secrets-management)

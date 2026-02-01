# 🚀 Deployment Guide

This guide provides step-by-step instructions for deploying the LLM Prompts Repository to production.

## Table of Contents
- [Quick Deployment (Free)](#quick-deployment-free)
- [Railway + Vercel](#railway--vercel)
- [Render + Netlify](#render--netlify)
- [AWS](#aws-deployment)
- [Digital Ocean](#digital-ocean)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Post-Deployment](#post-deployment)

---

## Quick Deployment (Free)

The fastest way to deploy using free tiers.

### Prerequisites
- GitHub account
- Backend and frontend code pushed to GitHub

---

## Railway + Vercel

**Best for:** Beginners, fast deployment, automatic scaling
**Cost:** Free tier available (500 hours/month)

### 1. Deploy Database & Backend on Railway

1. **Sign up** at [railway.app](https://railway.app)

2. **Create New Project**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"

3. **Add PostgreSQL**
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Database is created automatically

4. **Add Backend Service**
   - Click "+ New"
   - Select "GitHub Repo"
   - Choose your repository
   - Railway will detect it's a Python app

5. **Configure Backend**
   - Go to backend service settings
   - Set Root Directory: `backend`
   - Build Command: (auto-detected)
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   
6. **Environment Variables** (auto-set by Railway)
   - `DATABASE_URL` - automatically linked from PostgreSQL
   - `PORT` - automatically set

7. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Note your backend URL (e.g., `https://your-app.railway.app`)

### 2. Deploy Frontend on Vercel

1. **Sign up** at [vercel.com](https://vercel.com)

2. **Import Project**
   - Click "New Project"
   - Import from GitHub
   - Select your repository

3. **Configure Build**
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Environment Variables**
   - Add: `VITE_API_URL`
   - Value: Your Railway backend URL (from step 1.7)

5. **Deploy**
   - Click "Deploy"
   - Wait 1-2 minutes
   - Your app is live! 🎉

### Updating Your App

**Railway (Backend):**
- Push to GitHub → Auto-deploys

**Vercel (Frontend):**
- Push to GitHub → Auto-deploys

---

## Render + Netlify

**Best for:** Alternative to Railway/Vercel
**Cost:** Free tier available

### 1. Deploy Backend on Render

1. **Sign up** at [render.com](https://render.com)

2. **Create PostgreSQL Database**
   - Dashboard → New → PostgreSQL
   - Name: `promptdb`
   - Choose free tier
   - Create database
   - Note the **Internal Database URL**

3. **Create Web Service**
   - Dashboard → New → Web Service
   - Connect GitHub repository
   - Name: `prompts-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**
   - Add: `DATABASE_URL`
   - Value: Your PostgreSQL Internal Database URL

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes
   - Note your service URL

### 2. Deploy Frontend on Netlify

1. **Sign up** at [netlify.com](https://netlify.com)

2. **Import Project**
   - Sites → Add new site → Import from Git
   - Connect to GitHub
   - Select repository

3. **Configure Build**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`

4. **Environment Variables**
   - Site settings → Environment variables
   - Add: `VITE_API_URL`
   - Value: Your Render backend URL

5. **Deploy**
   - Click "Deploy site"
   - Wait 2-3 minutes
   - Your app is live! 🎉

---

## AWS Deployment

**Best for:** Enterprise, full control, scalability
**Cost:** Varies (free tier available for 12 months)

### Architecture
- **Frontend:** S3 + CloudFront
- **Backend:** Elastic Beanstalk or ECS
- **Database:** RDS PostgreSQL

### 1. Database (RDS)

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier promptdb \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123 \
  --allocated-storage 20
```

### 2. Backend (Elastic Beanstalk)

```bash
# Initialize EB
cd backend
eb init -p python-3.11 prompts-backend

# Create environment
eb create prompts-env

# Set environment variables
eb setenv DATABASE_URL="postgresql://..."

# Deploy
eb deploy
```

### 3. Frontend (S3 + CloudFront)

```bash
cd frontend

# Build
npm run build

# Create S3 bucket
aws s3 mb s3://prompts-frontend

# Upload
aws s3 sync dist/ s3://prompts-frontend

# Configure as website
aws s3 website s3://prompts-frontend \
  --index-document index.html
```

---

## Digital Ocean

**Best for:** Simple VPS deployment
**Cost:** $5/month minimum

### 1. Create Droplet

1. Create Ubuntu 22.04 droplet
2. SSH into droplet

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Nginx
sudo apt install nginx -y
```

### 3. Setup Database

```bash
sudo -u postgres psql
CREATE DATABASE promptdb;
CREATE USER promptuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE promptdb TO promptuser;
\q
```

### 4. Deploy Backend

```bash
# Clone repo
git clone <your-repo> /var/www/prompts

# Setup backend
cd /var/www/prompts/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
nano .env
# Set DATABASE_URL

# Install systemd service
sudo nano /etc/systemd/system/prompts-backend.service
```

**Service file:**
```ini
[Unit]
Description=Prompts Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/prompts/backend
Environment="PATH=/var/www/prompts/backend/venv/bin"
ExecStart=/var/www/prompts/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start prompts-backend
sudo systemctl enable prompts-backend
```

### 5. Deploy Frontend

```bash
cd /var/www/prompts/frontend

# Set API URL
echo "VITE_API_URL=http://your-droplet-ip:8000" > .env

# Build
npm install
npm run build

# Copy to Nginx
sudo cp -r dist/* /var/www/html/
```

### 6. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/prompts
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/prompts /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

### Frontend (.env)

```env
VITE_API_URL=https://your-backend-url.com
```

---

## Database Setup

### Creating Database Locally

```bash
# PostgreSQL
createdb promptdb

# Or via psql
psql -U postgres
CREATE DATABASE promptdb;
```

### Cloud Databases (Free Tiers)

**Supabase** (500MB free)
1. Sign up at supabase.com
2. Create new project
3. Copy connection string
4. Use in DATABASE_URL

**ElephantSQL** (20MB free)
1. Sign up at elephantsql.com
2. Create new instance
3. Copy URL
4. Use in DATABASE_URL

**Railway** (Built-in)
- Auto-configured when you add PostgreSQL

---

## Post-Deployment

### 1. Test Your Deployment

```bash
# Test backend
curl https://your-backend.com/api/prompts

# Should return JSON array
```

### 2. Monitor Your App

**Railway:**
- View logs in dashboard
- Monitor usage

**Render:**
- Logs tab
- Metrics tab

**Vercel/Netlify:**
- Analytics dashboard
- Function logs

### 3. Set up Custom Domain (Optional)

**Vercel:**
1. Domains → Add domain
2. Follow DNS instructions

**Railway:**
1. Settings → Domains
2. Add custom domain

### 4. Enable HTTPS

Most platforms (Vercel, Netlify, Railway, Render) provide automatic HTTPS.

For custom deployments:
```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 5. Backup Database

**Automated backups:**
- Railway: Automatic
- Render: Automatic
- Supabase: Automatic

**Manual backup:**
```bash
pg_dump -U user dbname > backup.sql
```

---

## Troubleshooting

### Backend doesn't start
- Check logs for errors
- Verify DATABASE_URL is correct
- Ensure PostgreSQL is running
- Check port is not blocked

### Frontend can't reach backend
- Verify VITE_API_URL is correct
- Check CORS settings in backend
- Ensure backend is running
- Check firewall rules

### Database connection fails
- Verify DATABASE_URL format
- Check database is running
- Confirm user has permissions
- Test connection with psql

### Build fails
- Check Node.js version (18+)
- Check Python version (3.8+)
- Clear caches and rebuild
- Check for missing dependencies

---

## Cost Estimates

### Free Tier (Hobby Projects)
- **Railway:** 500 hours/month free
- **Vercel:** Unlimited
- **Netlify:** 100GB bandwidth/month
- **Render:** 750 hours/month
- **Total:** $0/month

### Paid (Production)
- **Railway:** ~$5-20/month
- **Vercel Pro:** $20/month
- **Render:** ~$7-25/month
- **Total:** ~$15-50/month

### Enterprise (High Traffic)
- **AWS:** $50-500+/month
- **Digital Ocean:** $50-200+/month
- **Google Cloud:** $50-500+/month

---

## Security Checklist

- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up CORS properly
- [ ] Regular database backups
- [ ] Monitor error logs
- [ ] Update dependencies regularly
- [ ] Use strong database passwords
- [ ] Set up monitoring alerts

---

## Performance Optimization

1. **Enable caching**
   - CloudFlare CDN
   - Browser caching headers

2. **Database optimization**
   - Add indexes on frequently queried columns
   - Use connection pooling

3. **Frontend optimization**
   - Already optimized with Vite
   - Assets automatically minified

4. **Backend optimization**
   - Use async/await
   - Enable gzip compression

---

## Scaling

When you need to scale:

1. **Vertical Scaling**
   - Upgrade server instance
   - Increase database resources

2. **Horizontal Scaling**
   - Add load balancer
   - Deploy multiple backend instances
   - Use read replicas for database

3. **Caching Layer**
   - Add Redis for frequently accessed data
   - Use CDN for static assets

---

## Support

If you encounter issues:
1. Check logs first
2. Review this guide
3. Check platform-specific documentation
4. Open GitHub issue

---

**Happy deploying! 🚀**

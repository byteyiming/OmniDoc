# Railway Environment Variables Setup - Step by Step

## 🚨 Current Issue

Your Railway service is not finding `DATABASE_URL` and `REDIS_URL`. The logs show:
```
Environment variables found: ['GPG_KEY', 'RAILWAY_STATIC_URL', 'RAILWAY_SERVICE_OMNIDOC_URL']
```

This means Railway is only seeing system variables, not your custom variables.

## ✅ Solution: Set Variables at Service Level

### Method 1: Bulk Import (Fastest)

1. **Open Railway Dashboard**
   - Go to https://railway.app
   - Click on your project: `zesty-exploration`
   - Click on your service: `OmniDoc`

2. **Open Variables Tab**
   - Click on **"Variables"** tab (top menu)
   - You should see a list of variables

3. **Bulk Edit**
   - Look for a button that says **"Bulk Edit"** or **"Import Variables"** or **"Add Variables"**
   - OR click the **"+"** button to add variables

4. **Copy and Paste**
   - Open `RAILWAY_VARIABLES.txt` from this repository
   - Copy ALL the content (starting from `DATABASE_URL=...`)
   - Paste into Railway's bulk edit field
   - **IMPORTANT**: Make sure you're pasting at the SERVICE level, not project level

5. **Save**
   - Click **"Update Variables"** or **"Save"**
   - Wait for Railway to redeploy (should happen automatically)

### Method 2: Manual Entry (If Bulk Edit Doesn't Work)

1. **Go to Service Variables**
   - Railway → Your Project → Your Service (`OmniDoc`)
   - Click **"Variables"** tab
   - **Make sure you're at SERVICE level** (not project level)

2. **Add Each Variable**
   - Click **"New Variable"** or **"+"** button
   - Add these variables ONE BY ONE:

#### Required Variables (MUST HAVE):

```
DATABASE_URL=postgresql://neondb_owner:npg_wUg5P3SnCMcF@ep-divine-meadow-a4epnyhw-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

```
REDIS_URL=redis://default:AXVjAAIncDJINDY0OGUwNzdkMjc0M2U50GE2Yzg4ZGUzYWU3YWVlZXAyMzAwNTE@right-loon-30051.upstash.io:6379
```

#### Other Important Variables:

```
UPSTASH_REDIS_REST_URL=https://right-loon-30051.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXVjAAIncDJlNDY0OGUwNzdkMjc0M2U5OGE2Yzg4ZGUzYWU3YWVlZXAyMzAwNTE
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyCf00kyTW30dixD8MEYj8Z6xFkWDfX46M8
ENVIRONMENT=prod
LOG_LEVEL=INFO
LOG_FORMAT=json
ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info,https://*.vercel.app
JWT_SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
RATE_LIMIT_PER_MINUTE=2
RATE_LIMIT_PER_DAY=50
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

3. **For Each Variable**:
   - **Key**: `DATABASE_URL` (no quotes)
   - **Value**: `postgresql://neondb_owner:...` (no quotes, copy the full string)
   - **IMPORTANT**: 
     - ✅ Value should NOT be empty
     - ✅ Value should NOT have quotes around it
     - ✅ Value should be the complete connection string

4. **Save**
   - Click **"Update Variables"** after adding all variables
   - Wait for automatic redeploy

## 🔍 Verify Variables Are Set

After saving, check the logs. You should see:
```
✓ DATABASE_URL is set (length: 150)
✓ REDIS_URL is set (length: 120)
```

If you still see:
```
WARNING | DATABASE_URL exists in os.environ but is empty string
```

Then the variable exists but has an empty value. Go back and **enter the actual value**.

## ⚠️ Common Mistakes

1. **Project Level vs Service Level**
   - ❌ Setting variables at PROJECT level
   - ✅ Set at SERVICE level (inside your `OmniDoc` service)

2. **Empty Values**
   - ❌ Variable name exists but value is empty
   - ✅ Variable must have a non-empty value

3. **Quotes**
   - ❌ `DATABASE_URL="postgresql://..."`
   - ✅ `DATABASE_URL=postgresql://...` (no quotes)

4. **Not Saving**
   - ❌ Adding variables but not clicking "Update Variables"
   - ✅ Always click "Update Variables" or "Save"

## 📝 Quick Reference

All variables are in `RAILWAY_VARIABLES.txt` - copy and paste that entire file into Railway's bulk edit.


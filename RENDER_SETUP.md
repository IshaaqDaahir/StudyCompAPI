# Render Environment Variables Setup

## Required Environment Variables for Render

Add these environment variables in your Render dashboard:

### Django Settings
```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
```

### Database (if using PostgreSQL)
```
DATABASE_URL=your-postgres-url-from-render
```

### AWS S3 Configuration (Required for file uploads)
```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

## AWS S3 Setup Steps

1. **Create an S3 Bucket:**
   - Go to AWS S3 Console
   - Create a new bucket (e.g., `your-app-name-media`)
   - Choose a region (e.g., us-east-1)
   - Uncheck "Block all public access" for media files
   - Enable versioning (optional)

2. **Create IAM User:**
   - Go to AWS IAM Console
   - Create a new user for your app
   - Attach policy: `AmazonS3FullAccess` (or create custom policy)
   - Save the Access Key ID and Secret Access Key

3. **Configure Bucket Policy (for public read access):**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/media/*"
        }
    ]
}
```

4. **Configure CORS for your bucket:**
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

## Alternative: Use Cloudinary (Easier Setup)

If you prefer not to use AWS S3, you can use Cloudinary:

1. Install: `pip install cloudinary`
2. Add to requirements.txt: `cloudinary`
3. Update settings.py with Cloudinary configuration
4. Set environment variables: `CLOUDINARY_URL`

## Troubleshooting

- Make sure all environment variables are set in Render
- Check Render logs for any errors during deployment
- Verify S3 bucket permissions and CORS settings
- Test file upload in development first
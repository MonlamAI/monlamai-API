# Monlamai FastAPI

A FastAPI-based backend service for Monlam AI models, providing various AI services including translation, OCR, speech-to-text, text-to-speech, chat, and more.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

Monlamai FastAPI is a RESTful API service that provides access to various AI models developed by Monlam AI. The service includes endpoints for translation, OCR, speech-to-text, text-to-speech, chat, and more.

## Features

- **Translation Services**: API endpoints for text translation
- **OCR (Optical Character Recognition)**: Convert images to text
- **Speech-to-Text**: Convert audio to text (currently under maintenance)
- **Text-to-Speech**: Convert text to audio (currently under maintenance)
- **Chat**: Conversational AI interface
- **User Management**: User authentication and management
- **File Upload**: S3 integration for file uploads
- **Rate Limiting**: API rate limiting to prevent abuse
- **Authentication**: Token-based authentication

## Prerequisites

- Python 3.8+
- PostgreSQL database
- AWS S3 account (for file uploads)
- Docker (optional, for containerized deployment)

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```
# Server Configuration
PORT=8000

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# Authentication
MODEL_AUTH=your_model_auth_token
API_KEY=your_api_key

# Model URLs
MT_MODEL_URL=your_translation_model_url

# AWS S3 Configuration (for file uploads)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
S3_BUCKET=your_s3_bucket_name

# Other Services
# Add any other service-specific environment variables here
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/monlamai-fast-api.git
   cd monlamai-fast-api
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Generate Prisma client:
   ```bash
   prisma generate
   ```

## Running the Application

### Development Mode

Run the application in development mode with auto-reload:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

For production, it's recommended to use a production ASGI server like Gunicorn with Uvicorn workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

### Cloud Deployment

#### Render (Direct Deployment)

> **Note**: This project is deployed directly to Render.com without using Docker.

1. Create a new Web Service on Render:
   - Sign in to your Render account and go to the dashboard
   - Click on "New" and select "Web Service"
   - Connect your GitHub/GitLab repository or use the manual deploy option

2. Configure the service:
   - **Name**: Choose a name for your service (e.g., monlamai-api)
   - **Runtime**: Select Python
   - **Build Command**: `pip install -r requirements.txt && prisma generate`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. Set environment variables:
   - Go to the "Environment" tab
   - Add all required environment variables from your .env file:
     - `MODEL_AUTH`
     - `API_KEY`
     - `MT_MODEL_URL`
     - `DATABASE_URL`
     - AWS credentials if using S3
     - Any other required variables

4. Configure database (if needed):
   - Create a PostgreSQL database in Render
   - Render will automatically set the `DATABASE_URL` environment variable
   - Or connect to an external database by setting the `DATABASE_URL` manually

5. Deploy:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Your API will be available at `https://your-service-name.onrender.com`

6. Monitoring and Logs:
   - Monitor your application's performance in the Render dashboard
   - View logs by clicking on the "Logs" tab



## Project Structure

```
monlamai-fast-api/
├── main.py                  # Main application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in version control)
├── .gitignore               # Git ignore file
├── prisma/                  # Prisma ORM configuration
├── v1/                      # API version 1
│   ├── auth/                # Authentication modules
│   ├── Config/              # Configuration modules
│   ├── dict-data/           # Dictionary data
│   ├── libs/                # Library modules
│   ├── model/               # Data models
│   ├── models.py            # Pydantic models
│   ├── routes/              # API routes
│   ├── test/                # Test modules
│   └── utils/               # Utility functions
└── README.md                # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[Specify your license here]

---

For more information, contact [officials@monlam.com](mailto:officials@monlam.com) or visit [https://monlam.ai](https://monlam.ai).

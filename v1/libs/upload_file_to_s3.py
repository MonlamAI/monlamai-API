import aioboto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from typing import Tuple, Any
from dotenv import load_dotenv
import os
import asyncio

load_dotenv(override=True)

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_REGION")

async def upload_file_to_s3(file: Any, content_type: str, filename: str) -> str:
    session = aioboto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )
    async with session.client('s3') as s3_client:
        try:
            # Upload file to S3
            await s3_client.upload_fileobj(
                file,
                AWS_S3_BUCKET_NAME,
                filename,
                ExtraArgs={"ContentType": content_type}
            )
            file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{filename}"
            return file_url
        except NoCredentialsError:
            raise ValueError("AWS credentials not found")
        except PartialCredentialsError:
            raise ValueError("Incomplete AWS credentials")
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

# Example usage
async def main():
    with open('v1/ocr_sample.json', 'rb') as file:
        file_url = await upload_file_to_s3(file, 'text/plain', 'example.json')

if __name__ == "__main__":
    asyncio.run(main())

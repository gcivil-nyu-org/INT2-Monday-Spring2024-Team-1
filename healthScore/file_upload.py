import boto3
import os
from django.conf import settings


def medical_or_profile(file, loc, request):
    if file:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, file.name)
            with open(file_path, "wb") as f:
                for chunk in file.chunks():
                    f.write(chunk)

            aws_access_key_id = settings.AWS_ACCESS_KEY_ID
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
            aws_region = settings.AWS_S3_REGION_NAME
            s3 = boto3.resource(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
            )
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            if "userEmail" in request.POST:
                user = request.POST.get("userEmail").split("@")[0]
            else:
                user = request.user.email.split("@")[0]

            s3.Bucket(bucket_name).upload_file(
                file_path,
                "documents-health-score/" + loc + "/" + user + "/" + file.name,
            )

            file_name = loc + "/" + user + "/" + file.name
            file_url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/documents-health-score/{file_name}"
            os.remove(file_path)

            return file_url
        except Exception:
            return ""


def file_upload(request, loc):
    if request.FILES.get("profile_picture"):
        uploaded_file = request.FILES.get("profile_picture")
        return medical_or_profile(uploaded_file, loc, request)

    elif request.FILES.get("medical_document"):
        uploaded_file = request.FILES.get("medical_document")
        return medical_or_profile(uploaded_file, loc, request)

    elif request.FILES.get("identity_proof"):
        # User not logged in at this point
        uploaded_file = request.FILES.get("identity_proof")
        if uploaded_file:
            try:
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
                with open(file_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                aws_access_key_id = settings.AWS_ACCESS_KEY_ID
                aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
                aws_region = settings.AWS_S3_REGION_NAME
                s3 = boto3.resource(
                    "s3",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=aws_region,
                )
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                user = request.POST.get("email").split("@")[0]
                s3.Bucket(bucket_name).upload_file(
                    file_path,
                    "documents-health-score/"
                    + loc
                    + "/"
                    + user
                    + "/"
                    + uploaded_file.name,
                )

                file_name = loc + "/" + user + "/" + uploaded_file.name
                uploaded_file_url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/documents-health-score/{file_name}"
                os.remove(file_path)

                return uploaded_file_url
            except Exception:
                return ""
    else:
        return ""

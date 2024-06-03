from django.shortcuts import redirect
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework import status
from .request_serializers import OAuthSerializer
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
import os, json
from django.contrib.auth import login

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, "secrets.json")

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = f"Set the {setting} environment variable"
        raise ImproperlyConfigured(error_msg)

GOOGLE_SCOPE_USERINFO = get_secret("GOOGLE_SCOPE_USERINFO")
GOOGLE_REDIRECT = get_secret("GOOGLE_REDIRECT")
GOOGLE_CALLBACK_URI = get_secret("GOOGLE_CALLBACK_URI")
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = get_secret("GOOGLE_SECRET")

def google_login(request):
    scope = GOOGLE_SCOPE_USERINFO  # + "https://www.googleapis.com/auth/drive.readonly" 등 scope 설정 후 자율적으로 추가
    return redirect(f"{GOOGLE_REDIRECT}?client_id={GOOGLE_CLIENT_ID}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    code = request.GET.get("code")  # Query String 으로 넘어옴
    return JsonResponse(code, safe=False)
    # token_req = requests.post(
    #     f"https://oauth2.googleapis.com/token?client_id={GOOGLE_CLIENT_ID}&client_secret={GOOGLE_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}"
    # )
    # token_req_json = token_req.json()
    # error = token_req_json.get("error")
    #
    # if error is not None:
    #     raise JSONDecodeError(error)
    #
    # google_access_token = token_req_json.get('access_token')
    #
    # email_response = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={google_access_token}")
    # res_status = email_response.status_code
    #
    # if res_status != 200:
    #     return JsonResponse({'status': 400, 'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
    #
    # email_res_json = email_response.json()
    #
    # serializer = OAuthSerializer(data=email_res_json)
    # if serializer.is_valid(raise_exception=True):
    #     user = serializer.validated_data["user"]
    #     access_token = serializer.validated_data["access_token"]
    #     refresh_token = serializer.validated_data["refresh_token"]
    #
    #     # 사용자 인증 설정
    #     login(request, user)
    #
    #     res = JsonResponse(
    #         {
    #             "user": {
    #                 "id": user.id,
    #                 "email": user.email,
    #             },
    #             "message": "login success",
    #             "token": {
    #                 "access_token": access_token,
    #                 "refresh_token": refresh_token,
    #             },
    #         },
    #         status=status.HTTP_200_OK,
    #     )
    #     res.set_cookie("access-token", access_token, httponly=True)
    #     res.set_cookie("refresh-token", refresh_token, httponly=True)
    #     return res
    # return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def google_callback_re(request):
    code = request.GET.get("code")  # Query String 으로 넘어옴

    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={GOOGLE_CLIENT_ID}&client_secret={GOOGLE_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}"
    )
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)

    google_access_token = token_req_json.get('access_token')

    email_response = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={google_access_token}")
    res_status = email_response.status_code

    if res_status != 200:
        return JsonResponse({'status': 400, 'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

    email_res_json = email_response.json()

    serializer = OAuthSerializer(data=email_res_json)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data["user"]
        access_token = serializer.validated_data["access_token"]
        refresh_token = serializer.validated_data["refresh_token"]

        # 사용자 인증 설정
        login(request, user)

        res = JsonResponse(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "message": "login success",
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        res.set_cookie("access-token", access_token, httponly=True)
        res.set_cookie("refresh-token", refresh_token, httponly=True)
        return res
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

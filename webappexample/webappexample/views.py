import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid fhirUser",
    },
    server_metadata_url=settings.ISSUER_ENDPOINT,
)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    resp = oauth.auth0.get(token.get('userinfo').get('fhirUser'), token=token, headers = {
        'Accept': 'application/json'
    })
    resp.raise_for_status()
    fhirUser = resp.json()    
    request.session["user"] = token
    request.session["fhirUser"] = fhirUser
    return redirect(request.build_absolute_uri(reverse("index")))

def logout(request):
    request.session.clear()

    return redirect(request.build_absolute_uri(reverse("index")))

def index(request):
    user = request.session.get("user")
    fhirUser = request.session.get("fhirUser")
    if user is None:
        return render(
            request,
            "index.html",
        )
    else:
        return render(
            request,
            "index.html",
            context={
                "session": user,
                "username": fhirUser.get('name')[0].get('text'),
                "pretty": json.dumps(user, indent=4),
                "fhirUser": json.dumps(fhirUser, indent=4),
            },
        )
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import os
from pytube import YouTube
import assemblyai as aai
import openai

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if (request.method=="POST"):
        yt_link = ""
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            #return JsonResponse({'content':yt_link})
        except(KeyError, json.JSONDecodeError):
            return JsonResponse({'error':'Invalid data sent'}, status=400)
        #get title
        title = yt_title(yt_link)
        #get transcript
        transcript = transcription(yt_link)
        if not transcript:
            return JsonResponse({'error':'Failed transcription'}, status=500)

        #use OpenAI to generate blog
        blog = transcript_to_blog(transcript)
        if not blog:
            return JsonResponse({'error':'Failed blog generation'}, status=500) 
        #save blog article to database
        return JsonResponse({'content': blog})
    else:
        return JsonResponse({'error':'Invalid request method'}, status=405)

def transcript_to_blog(transcript):
    openai.api_key = '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'
    prompt = f"Based on the following transcript of a Youtube video, write a blog article descripbing that video:\n\n{transcript}"
    response = openai.completions.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=2048
    )
    content = response.choices[0].text.strip()
    return content

def yt_title(link):
    return YouTube(link).title
def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()

    #download file
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    #save file
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file


def transcription(link):
    audio = download_audio(link)
    aai.settings.api_key('8b7314ebbe95442c8ba600daa56ce035')
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe(audio)
    return transcript.text

def user_login(request):
    if (request.method=="POST"):
        username=request.POST['username']
        pw=request.POST['password']

        user = authenticate(request, username = username, password = pw)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'signup.html', {'error_message': error_message})

    return render(request, 'login.html')
def signup(request):
    if (request.method=="POST"):
        username=request.POST['username']
        email=request.POST['email']
        pw=request.POST['password']
        rpw=request.POST['repeatPassword']
        if (pw==rpw):
            try:
                user=User.objects.create_user(username, email, pw)
                user.save()
                login(request,user)
                return redirect('/')
            except:
                error_message = "Error creating account"
                return render(request, 'signup.html', {'error_message': error_message})
                      
        else:
            error_message = "Passwords do not match"
            return render(request, 'signup.html', {'error_message': error_message})

    return render(request, 'signup.html')
def allBlogs(request):
    return render(request, 'all-blogs.html')
def blogDetails(request):
    return render(request, 'blog-details.html')
def user_logout(request):
    logout(request)
    return redirect('/')
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
from youtube_transcript_api import YouTubeTranscriptApi
import assemblyai as aai
import google.generativeai as genai
import openai
from .models import BlogPost
from .keys import openai_key, aiassembly_key, gemini_key1, gemini_key2
from math import ceil

# Create your views here.

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, 'all-blogs.html', {'blog_articles': blog_articles})
def yt_title(link):
        return YouTube(link).title
    
@login_required
def index(request):
    return render(request, 'index.html')

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
    #try:
    #youtube id is 11 chars
    srt = YouTubeTranscriptApi.get_transcript(link[-11:])
    transcript=[]
    count=0
    for i in srt:
        transcript.append(i['text'])
        count+=len(i['text'])
    
    #ditching a portion of the transcript to make it under 100000 chars (found by trial and error)
    if (count>100000):
        c = ceil(count/100000)
        transcript = "".join(transcript[::c])
    else:
        transcript = ''.join(transcript)


    return transcript
    '''except:
        audio = download_audio(link)
        aai.settings.api_key=aiassembly_key
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio)

        #removing both files created previously
        os.remove(audio)
        
        #making sure transcript is smaller than 100000 chars
        transcript = transcript.text[:min(100000, len(transcript))]
        return transcript'''
    

def transcript_to_blog(transcript):
# openai.api_key = openai_key
    prompt = f"Do not use titles and just write a single paragraph. Based on the following transcript of a Youtube video, write a blog article descripbing that video. Add in a little personnality and try to sell that video to readers, while summarizing at the same time. Some parts of the transcripts might or might not be missing:\n\n{transcript}"
    '''response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=2048
    )'''
    #content = response.choices[0].text.strip()
    genai.configure(api_key=gemini_key1)

    model = genai.GenerativeModel('gemini-1.5-pro')
    content = model.generate_content(prompt)
    return content.text.replace('#','')

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
        new_blog_article = BlogPost.objects.create(
            user = request.user,
            youtube_title = title,
            youtube_link = yt_link,
            content = blog
        )
        new_blog_article.save()

        return JsonResponse({'content': blog})
    else:
        return JsonResponse({'error':'Invalid request method'}, status=405)

@csrf_exempt
def generate_ts(request):
    def format_timestamps(seconds):
        seconds=int(seconds)
        mins = seconds//60
        hours = seconds//3600
        res = str(mins%60)+':'+str(seconds%60)
        if (hours>0):
            res = str(hours)+':'+res
        return res
    def clean_timestamps(ts):
        #fixing common mistakes and chars that appear in Gemini output
        ts=(ts.text.replace('*', ''))
        ts=(ts.replace('  ', ' '))
        for i in range(10):
            #Mistake: hh:m:ss -> hh:mm:ss
            ts=(ts.replace(':'+str(i)+':', ':0'+str(i)+':'))
            #Mistake: hh:mm:s -> hh:mm:ss
            ts=(ts.replace(':'+str(i)+' ', ':0'+str(i)+' '))
        return ts
    
    def separate_timestamps(ts):
        #reformats hh:mm:ss into a dictionary
        def reformat_time(time):
            dictio = dict()
            time = time.split(':')
            if len(time)==2:
                dictio['min'] = time[0]
                dictio['sec'] = time[1]
            elif len(time)==3:
                dictio['hour'] = time[0]
                dictio['min'] = time[1]
                dictio['sec'] = time[2]
            return dictio
            

        #separates each line
        ts=ts.split('\n')
        result=[]
        for i in range(len(ts)):

            #separates timestamp and title
            ts[i]=ts[i].split(' - ')

            time_dict = reformat_time(ts[i][0])
            #error
            if len(time_dict)==0:
                continue
            title = ts[i][1]
            line = dict()
            line['time'] = time_dict
            line['title'] = title
            result.append(line)
        #result is now an array of dictionaries, each of them containing the info of a single timestamp
        return result




    if (request.method=="POST"):
        yt_link = ""
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            #return JsonResponse({'content':yt_link})
        except(KeyError, json.JSONDecodeError):
            return JsonResponse({'error':'Invalid data sent'}, status=400)
        #get title
        srt = YouTubeTranscriptApi.get_transcript(yt_link[-11:])
        if not srt:
                return JsonResponse({'error':'Failed attempt to get Youtube transcription'}, status=500)

        transcript=[]
        #we save only one timestamp in 4 to reduce size of transcript
        #this works because timestamps are recorded quite frequently
        for j in range(0,len(srt),4):
            string=''
            start=format_timestamps(srt[j]['start'])
            count=j
            while count-j<4 and count<len(srt):
                string+=str(srt[count]['text'])
                count+=1
            
            transcript.append(start+'|'+string)
        
        final_transcript="|".join(transcript)
        prompt = ''
        #ditching a portion of the transcript to make it under 100000 chars (found by trial and error)
        if (len(final_transcript)>100000):
            c = ceil(len(final_transcript)/100000)
            final_transcript = "|".join(transcript[::c])
            prompt="Divide and summarize a youtube video into segments while providing their start time. The segments should be divided by themes and summarized by a short title, nothing more. Do not create too many segments and prioritize the most important (max 20). Here is an example: 'mm:ss - Section title'. Follow the format of Youtube timestamps. Keep in mind that some of the transcript is missing. Here is the video transcript with numbers surrounded by | which signify the start of segments in seconds:\n"+(final_transcript)
        else:
            prompt="Divide and summarize a youtube video into segments while providing their start time. The segments should be divided by themes and summarized by a short title, nothing more. Do not create too many segments and prioritize the most important (max 20). Here is an example: 'mm:ss - Section title'. Follow the format of Youtube timestamps. Here is the video transcript with numbers surrounded by | which signify the start of segments in seconds:\n"+(final_transcript)
        genai.configure(api_key=gemini_key2)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        #clean up common typos and mistakes from Gemini
        response = clean_timestamps(response)

        #change the format to array (easier to handle the display)
        response = separate_timestamps(response)
        if len(response)==0:
            return JsonResponse({'error':"LLM returns invalid format or cannot derive information from the video's transcript"}, status=500)

        return JsonResponse({'content': json.dumps(response)})





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

def blog_details(request, pk):
    details = BlogPost.objects.get(id = pk)
    if request.user == details.user:
        return render(request, 'blog-details.html', {'blog_article_details', details})
    else:
        return redirect('/')
def user_logout(request):
    logout(request)
    return redirect('/')
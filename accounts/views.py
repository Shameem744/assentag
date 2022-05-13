from django.shortcuts import render,redirect, HttpResponse
from .forms import UserForm, UpdateForm
from django.contrib.auth import login as log,authenticate,logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import ProfilePhoto, Posts, Comments, Like, UserAccounts, Friends, FacesPermission, Chat
import json
from .detect_face import detect_face_profile, face_tagging, blur_face, refresh_pickle
from itertools import chain
from django.db.models import Q
import face_recognition

import pickle
import os

# Create your views here.

def registration(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            v = form.save()
            obj=ProfilePhoto(user=v)
            obj.save()
            return redirect("/accounts/login/")
        else:
            return render(request, "accounts/register.html", {"form":form})
    else:
        form = UserForm()
        return render(request, "accounts/register.html", {"form":form})

def login(request):
    # if request.user.is_authenticated:
    #    return redirect('/') 
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"] 
        check = authenticate(username=email,password=password)
        if check:
            log(request,check)
            return redirect("/")
        else:
            return render(request ,"accounts/login.html",{"login_error_msg":"username or password incorrect"})

    else:
        return render(request ,"accounts/login.html")

@login_required(login_url='/accounts/login/')
def home(request):
    if request.method == "POST":
        post_image = request.FILES["post_image"]
        description = request.POST["description"]
        with open("media/temp/temp.jpg","wb") as f:
            f.write(post_image.read())
        founded_faces,unfounded_faces = face_tagging()
        obj = Posts(user=request.user, posted_image=post_image, description=description)
        obj.save()

        for face in founded_faces:
            try: user = UserAccounts.objects.get(email = face["email"])
            except: return HttpResponse("invalid email adreess")
            if not user == request.user:
                FacesPermission.objects.create(post = obj,
                user = user,
                x = face["x"], y = face["y"],
                 w = face["w"], h = face["h"])
        # print("unfounded",unfounded_faces)
        blur_face(obj.posted_image.url, unfounded_faces)
        return redirect("/")
    posts = Posts.objects.filter(Q(user = request.user) | Q(user__in=Friends.objects.filter(follower = request.user).values('following'))).order_by('created_at')

    #notification
    friends_notific = Friends.objects.filter(following = request.user)
    comments_notific = Comments.objects.filter(post__user = request.user).exclude(user=request.user)
    likes_notific = Like.objects.filter(post__user = request.user).exclude(user=request.user)
    permission_notific = FacesPermission.objects.filter(user=request.user)
    result_list = sorted(
    chain(friends_notific, comments_notific, likes_notific, permission_notific),
    key=lambda instance: instance.created_at,reverse= True)

    return render(request, 'accounts/home.html',{"posts":posts, "notifications":result_list[:10]})


def logout_function(request):
    logout(request)
    return redirect("/accounts/login/")


@login_required(login_url='/accounts/login/')
def profile(request):
    if request.method == "POST":
        image =  request.FILES.get("profile")
        security =  request.FILES.get("security")

        if image:
            if request.user.profilephoto_set.all():
                obj = request.user.profilephoto_set.all()[0]
                obj.profile = image
                obj.save()
            else:
                obj = ProfilePhoto(profile=image, user=request.user)
                obj.save()

        if security:
            with open("media/temp/temp.jpg","wb") as f:
                f.write(security.read())
            detected = detect_face_profile()
            if detected:
                if request.user.profilephoto_set.all():
                    obj = request.user.profilephoto_set.all()[0]
                    obj.security = security
                    obj.face_uploaded = True
                    obj.save()
                else:
                    obj = ProfilePhoto(security=security, user=request.user, face_uploaded=True)
                    obj.save()

                refresh_pickle()
                qs_json = json.dumps({"uploaded":True})

            else:
                qs_json = json.dumps({"uploaded":False})
            return HttpResponse(qs_json, content_type='application/json')
        return redirect("/accounts/profile/")
    follower_count = Friends.objects.filter(following=request.user).count()
    following_count = Friends.objects.filter(follower=request.user).count()
    return render(request, 'accounts/profile.html',{"follower_count":follower_count, "following_count":following_count})

@login_required(login_url='/accounts/login/')
def comment(request, id):
    post = Posts.objects.get(id=id)
    if request.method == "POST":
        text = request.POST["comment"]
        obj = Comments(user=request.user, post= post, comment = text)
        obj.save()
        return redirect('/accounts/comment/{}/'.format(id))
    else:
        comments = Comments.objects.filter(post=post)[::-1]
        return render(request, 'accounts/comment.html', {'post':post, 'comments':comments})

@login_required(login_url='/accounts/login/')
def like(request):
    id=request.GET["id"]
    post = Posts.objects.get(id=id)
    check = Like.objects.filter(user=request.user,post=post)
    d={}
    if check:
        check[0].delete()
        d["like"]=False
    else:
        Like.objects.create(user=request.user,post=post)
        d["like"]=True
    d["count"] = Like.objects.filter(post=post).count()
    qs_json = json.dumps(d)
    print("asd")
    return HttpResponse(qs_json, content_type='application/json')
        
@login_required(login_url='/accounts/login/')
def edit_profile(request):
    if request.method == "POST":
        form = UpdateForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("/")
        else:
            return render(request, "accounts/edit_profile.html", {"form":form})
    else:
        form = UpdateForm(instance=request.user)
        form1 = PasswordChangeForm(request.user)
        return render(request, "accounts/edit_profile.html", {"form":form,"form1":form1})

@login_required(login_url='/accounts/login/')
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("/")
        else:
            return render(request, "accounts/edit_profile.html", {"form":form})
    else:
        form = PasswordChangeForm(request.user)
        return render(request, "accounts/edit_profile.html", {"form":form})


@login_required(login_url='/accounts/login/')
def delete_post(request,id):
    post = Posts.objects.get(id=id)
    if request.user == post.user:
        post.delete()
    return redirect("/")

@login_required(login_url='/accounts/login/')
def user_profile(request, id):
    user = UserAccounts.objects.get(id=id)
    if user.id == request.user.id:
        return redirect('/accounts/profile/')
    following_user = Friends.objects.filter(follower=request.user, following= user)
    follower_count = Friends.objects.filter(following=user).count()
    following_count = Friends.objects.filter(follower=user).count()
    context = {"profile":user,'following_user':following_user,
                "follower_count":follower_count, "following_count":following_count}
    return render(request,'accounts/user_profile.html', context)

@login_required(login_url='/accounts/login/')
def follow_user(request, id):
    following = UserAccounts.objects.get(id=id)
    try:
        obj = Friends.objects.get(follower=request.user, following= following)
        obj.delete()
    except:
        Friends.objects.create(follower=request.user, following= following)
    return redirect('/accounts/profile/user/{}/'.format(id))

@login_required(login_url='/accounts/login/')
def search_user(request):
    query = request.GET["query"]
    if query != "":
        result = ProfilePhoto.objects.filter(user__email__contains=query).values('user__id','user__email','profile')
        # qs_json = serializers.serialize('json', result)
        qs_json = json.dumps(list(result))
        return HttpResponse(qs_json, content_type='application/json')
    else:
        qs_json = json.dumps(list())
        return HttpResponse(qs_json, content_type='application/json')

@login_required(login_url='/accounts/login/')
def list_following(request, id):
    followings = Friends.objects.filter(follower__id=id)
    return render(request, 'accounts/following.html',{"followings": followings})

@login_required(login_url='/accounts/login/')
def list_followers(request, id):
    followers = Friends.objects.filter(following__id=id)
    return render(request, 'accounts/followers.html',{"followers": followers})

@login_required(login_url='/accounts/login/')
def allow_image(request, id):
    obj = FacesPermission.objects.get(id = id)
    if request.user != obj.user:
        return redirect('/accounts/login/')
    obj.allowed = True
    obj.save()
    return redirect('/')

@login_required(login_url='/accounts/login/')
def blur_image(request, id):
    obj = FacesPermission.objects.get(id = id)
    if request.user != obj.user:
        return redirect('/accounts/login/')
    if obj.allowed:
        return redirect('/')
    blur_face(obj.post.posted_image.url, [[obj.x, obj.y, obj.w, obj.h]])
    obj.blurred = True
    obj.save()
    return redirect('/')

@login_required(login_url='/accounts/login/')
def notifications(request):
    friends_notific = Friends.objects.filter(following = request.user)
    comments_notific = Comments.objects.filter(post__user = request.user).exclude(user=request.user)
    likes_notific = Like.objects.filter(post__user = request.user).exclude(user=request.user)
    permission_notific = FacesPermission.objects.filter(user=request.user)
    result_list = sorted(
    chain(friends_notific, comments_notific, likes_notific, permission_notific),
    key=lambda instance: instance.created_at,reverse= True)
    return render(request, 'accounts/notifications.html',{"notifications":result_list})


@login_required(login_url='/accounts/login/')
def chat_home(request):
    chats = Chat.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    chats =set([i.sender for i in chats]+[i.receiver for i in chats])
    try:
        chats.remove(request.user)
    except:
        pass
    return render(request , 'accounts/chat_home.html', {"chats":chats})

@login_required(login_url='/accounts/login/')
def chat_box(request, id):
    user_data = UserAccounts.objects.get(id = id) 
    if request.method == "POST":
        message = request.POST["message"]
        if message != "":
            Chat.objects.create(sender = request.user, receiver = user_data, message=message)
        return redirect(f'/accounts/chat/{id}/')
    chats = Chat.objects.filter(Q(sender=request.user, receiver = user_data) | Q(sender= user_data,receiver=request.user)).order_by('created_at')
    return render(request, 'accounts/chat_box.html',{"user_data":user_data, "chats":chats})
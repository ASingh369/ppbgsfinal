from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
import math, random
from django.db.models import Avg

# Import required models
from .models import Topic, Video, Question, Pdf, Query, Comment
from userprogress.models import UserAttemptedQuestion, UserWatchedVideo, UserReadNotes, TotalCoins, TotalPoints, UserLastLocation, UserAttemptedChallenge, Level
from django.contrib.auth.models import User
from challenges.models import Challenge, DoublePoint, FreeWin, Hint
from userprogress.models import TotalPoints, TotalCoins

def get_user_rank(user):
    # list of all the users
    allUsers = TotalPoints.objects.order_by('-points')

    rank = 1
    for singleUser in allUsers:
        if singleUser.user == user:
            break
        rank += 1
    return rank

def user_info(request):
    # current user's total points
    userPoints = TotalPoints.objects.get(user=request.user)

    # list of all the users
    allUsers = TotalPoints.objects.order_by('-points')

    # current user's rank
    rank = get_user_rank(request.user)
    

    # current user's coins
    userCoins = TotalCoins.objects.get(user=request.user)

    user_data = {
        'userPoints': userPoints,
        'rank': rank,
        'allUsers': allUsers,
        'userCoins': userCoins
    }

    return user_data


def update_user_points(request, points):
    # update total points
    total_points = TotalPoints.objects.get(user=request.user)
    total_points.points = total_points.points + points
    total_points.save()


def update_user_coins(request, coins):
    # update total coins
    total_coins = TotalCoins.objects.get(user=request.user)
    total_coins.coins = total_coins.coins + coins
    total_coins.save()


def update_user_last_location(request, location, topic):
    # update user's last visited location
    user_last_location = UserLastLocation.objects.get(user=request.user)
    user_last_location.topic = topic
    user_last_location.location = location
    user_last_location.save()


@login_required
def topic(request, topic_name):

    user_data = user_info(request)

    # get current topic otherwise 404 page
    topic = get_object_or_404(Topic, topicName=topic_name)

    # default video for videos page
    videos = Video.objects.filter(topic=topic)

    context = {
        'topic': topic,
        'video': videos[0].key,
        'user_data': user_data
    }

    return render(request, 'pages/topic.html', context)


@login_required
def videos(request):

    # Initializing points update message
    message_title = None
    points_up = None
    coins_up = None

    # retreive topic name from GET request
    if 'topic_name' in request.GET:
        topic_name = request.GET['topic_name']

    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)

    # Fetch all the videos related to current topic
    videos = Video.objects.filter(topic=topic)

    # key of the current video to display
    key = request.GET['key']

    # current video
    current_video = Video.objects.get(topic=topic, key=key)

    already_watched_video = UserWatchedVideo.objects.filter(
        video=current_video, user=request.user)

    if not already_watched_video:
        # add video to user watched history
        watched_video = UserWatchedVideo(
            video=current_video, user=request.user)
        watched_video.save()

        update_user_points(request, 2)
        update_user_coins(request, 4)

        message_title = "Explored new Video!"
        points_up = 2
        coins_up = 4

    user_data = user_info(request)

    update_user_last_location(request, 'videos', topic)

    context = {
        'topic': topic,
        'videos': videos,
        'key': key,
        'user_data': user_data,
        'message_title': message_title,
        'points_up': points_up,
        'coins_up': coins_up
    }

    return render(request, 'pages/videos.html', context)


@login_required
def notes(request):
    # Initializing points update message
    message_title = None
    points_up = None
    coins_up = None

    # retreive topic name from GET request
    if 'topic_name' in request.GET:
        topic_name = request.GET['topic_name']

    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)

    # Fetch current topic's pdf
    pdf = Pdf.objects.get(topic=topic)

    already_read_notes = UserReadNotes.objects.filter(
        pdf=pdf, user=request.user)
    if not already_read_notes:
        read_notes = UserReadNotes(pdf=pdf, user=request.user)
        read_notes.save()

        update_user_points(request, 4)
        update_user_coins(request, 8)

        message_title = "Started to read notes!"
        points_up = 4
        coins_up = 8

    # default video for videos page
    videos = Video.objects.filter(topic=topic)

    user_data = user_info(request)

    update_user_last_location(request, 'notes', topic)

    context = {
        'topic': topic,
        'video': videos[0].key,
        'pdf': pdf,
        'user_data': user_data,
        'message_title': message_title,
        'points_up': points_up,
        'coins_up': coins_up
    }
    return render(request, 'pages/notes.html', context)


@login_required
def quiz(request):
    # Initializing points update message
    message_title = None
    points_up = None
    coins_up = None
    danger_message = None

    # retreive topic name from GET request
    if 'topic_name' in request.GET:
        topic_name = request.GET['topic_name']

    # default values of context variables
    submitted_question = None
    user_answer = None

    # if user submits a answer
    if request.method == 'POST':
        # retreive question and user data
        user_id = request.POST['user_id']
        question_number = request.POST['question_number']
        user_answer = int(request.POST['radio'])

        # Fetch question submitted by user
        submitted_question = Question.objects.get(id=question_number)

        # check if user has previously submitted the question
        if request.user.is_authenticated:
            current_user = request.user
            already_attempted_question = UserAttemptedQuestion.objects.filter(
                question=submitted_question, user=current_user)

        # when user is attempting question again
        if already_attempted_question:
            if (user_answer == submitted_question.answer):
                if already_attempted_question[0].isCorrect:
                    message_title = "Correct Answer!"
                else:
                    already_attempted_question[0].isCorrect = True
                    already_attempted_question[0].save()
                    update_user_points(request, 1)
                    update_user_coins(request, 2)
                    message_title = "Correct answer!"
                    points_up = 1
                    coins_up = 2
            else:
                danger_message = "Incorrect answer!"
        # when user is attempting the question for first time
        else:
            if (user_answer == submitted_question.answer):
                attemptedQuestion = UserAttemptedQuestion(
                    question=submitted_question, user=request.user, isCorrect=True)
                attemptedQuestion.save()
                update_user_points(request, 1)
                update_user_coins(request, 2)
                message_title = "Correct answer!"
                points_up = 1
                coins_up = 2
            else:
                attemptedQuestion = UserAttemptedQuestion(
                    question=submitted_question, user=request.user, isCorrect=False)
                attemptedQuestion.save()
                danger_message = "Incorrect answer!"

    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)

    # Fetching all the questions of current topic
    questions = Question.objects.filter(topic=topic)

    # allow only one question to display on each page
    paginator = Paginator(questions, 1)
    page = request.GET.get('page')
    paged_questions = paginator.get_page(page)

    # default video for videos page
    videos = Video.objects.filter(topic=topic)

    user_data = user_info(request)

    update_user_last_location(request, 'quiz', topic)

    context = {
        'topic': topic,
        'questions': paged_questions,
        'submitted_question': submitted_question,
        'video': videos[0].key,
        'user_answer': user_answer,
        'user_data': user_data,
        'message_title': message_title,
        'points_up': points_up,
        'coins_up': coins_up,
        'danger_message': danger_message
    }

    return render(request, 'pages/quiz.html', context)


@login_required
def questions(request):

    user_data = user_info(request)

    # retreive topic name from GET request
    if 'topic_name' in request.GET:
        topic_name = request.GET['topic_name']

    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)

    # if user posts a question
    if 'question' in request.POST:
        question = request.POST['question']
        details = request.POST['details']
        query = Query(topic=topic, user=request.user,
                      question=question, details=details)
        query.save()

    # list of all the questions of current topic
    questions = Query.objects.filter(topic=topic)

    context = {
        'topic': topic,
        'questions': questions,
        'user_data': user_data
    }

    return render(request, 'pages/questions.html', context)


@login_required
def question(request):

    user_data = user_info(request)

    # retreive topic name from GET request
    if 'topic_name' in request.GET:
        topic_name = request.GET['topic_name']

    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)

    # current question/query
    if 'questionID' in request.GET:
        questionID = request.GET['questionID']

    query = Query.objects.get(id=questionID)

    # if user posts a comment
    if 'comment' in request.POST:
        comment = request.POST['comment']
        new_comment = Comment(user=request.user, query=query, comment=comment)
        new_comment.save()

    # list of all the comments of current topic
    comments = Comment.objects.filter(query=query)

    context = {
        'topic': topic,
        'query': query,
        'comments': comments,
        'user_data': user_data
    }

    return render(request, 'pages/question.html', context)


@login_required
def challenges(request):
    # pop message
    message_title = None

    if 'dp' in request.GET:
        challenge_id = request.GET['dp']
        # challenge
        dp_challenge = Challenge.objects.get(id=challenge_id)
        # check if chip is already baught
        dp_already_baught = DoublePoint.objects.filter(
            challenge=dp_challenge, user=request.user)

        if not dp_already_baught:
            double_point = DoublePoint(
                challenge=dp_challenge, user=request.user)
            double_point.save()
            update_user_coins(request, -32)
            message_title = "Chip Activated!"

    if 'fw' in request.GET:
        challenge_id = request.GET['fw']
        # challenge
        fw_challenge = Challenge.objects.get(id=challenge_id)
        # check if chip is already baught
        fw_already_baught = FreeWin.objects.filter(
            challenge=fw_challenge, user=request.user)

        if not fw_already_baught:
            free_win = FreeWin(challenge=fw_challenge, user=request.user)
            free_win.save()
            update_user_coins(request, -24)
            message_title = "Chip Activated!"

    user_all_dp = DoublePoint.objects.filter(user=request.user)

    dp_challenge_list = []

    for user_dp in user_all_dp:
        dp_challenge_list.append(user_dp.challenge)

    user_all_fw = FreeWin.objects.filter(user=request.user)

    fw_challenge_list = []

    for user_fw in user_all_fw:
        fw_challenge_list.append(user_fw.challenge)

    user_data = user_info(request)

    # retreive topic name from GET request
    if 'topic_name' in request.GET:
        topic_name = request.GET['topic_name']

    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)

    # Fetch easy challenges
    easy_challenges = Challenge.objects.filter(topic=topic, difficulty="easy")

    # Fetch medium challenges
    medium_challenges = Challenge.objects.filter(
        topic=topic, difficulty="medium")

    # Fetch hard challenges
    hard_challenges = Challenge.objects.filter(topic=topic, difficulty="hard")

    update_user_last_location(request, 'challenges', topic)

    context = {
        'topic': topic,
        'easy_challenges': easy_challenges,
        'medium_challenges': medium_challenges,
        'hard_challenges': hard_challenges,
        'user_data': user_data,
        'message_title': message_title,
        'dp_challenge_list': dp_challenge_list,
        'fw_challenge_list': fw_challenge_list
    }

    return render(request, 'pages/challenges.html', context)


def hint(request):
    # current user's total coins
    userCoins = TotalCoins.objects.get(user=request.user)
    total_coins = userCoins.coins

    # retreive challenge id
    if 'challenge_id' in request.POST:
        challenge_id = int(request.POST['challenge_id'])
    else:
        return JsonResponse({'error': 'no challenge_id'})

    # retreive coins
    if 'coins' in request.POST:
        coins = int(request.POST['coins'])
        if coins > total_coins:
            return JsonResponse({'error': 'Not enough coins'})
        if coins > 0:
            coins = coins * (-1)
    else:
        return JsonResponse({'error': 'no coins'})

    challenge = Challenge.objects.get(id=challenge_id)

    # check if user has already used any hint for that question
    pre_hint = Hint.objects.filter(challenge=challenge, user=request.user)

    # if hint exists
    if pre_hint:
        hint = Hint.objects.get(challenge=challenge, user=request.user)
        hint.hints_baught = hint.hints_baught + 1
        hint.save()
        update_user_coins(request, coins)
        hint_number = hint.hints_baught
    else:
        hint = Hint(challenge=challenge, user=request.user)
        hint.save()
        update_user_coins(request, coins)
        hint_number = 1

    return JsonResponse({'total_coins': total_coins+coins, 'hint_number': hint_number})


@login_required
def challenge(request):

    # data related to user: coins, points, rank
    user_data = user_info(request)

    # get current topic name
    if 'topic_name' in request.GET:
        topic_name = request.GET['topic_name']

    # get current challenge id
    if 'exercise' in request.GET:
        exercise = request.GET['exercise']
    else:
        return redirect('topics')

    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)

    # Current challenge
    challenge = Challenge.objects.get(topic=topic, id=exercise)

    # check if any user hints exists
    hint_exits = Hint.objects.filter(challenge=challenge, user=request.user)

    if hint_exits:
        # get hints bought for this challenge
        hint = Hint.objects.get(challenge=challenge, user=request.user)
    else:
        # create new Hint for user
        hint = Hint(challenge=challenge, user=request.user, hints_baught=0)
        hint.save()

    hint_number = hint.hints_baught

    # check if user has attempted challenge earlier
    attempted_challenge = UserAttemptedChallenge.objects.filter(challenge=challenge, user=request.user)

    # if attempted
    if attempted_challenge:
        # get already attempted challenge
        old_attempted_challenge= UserAttemptedChallenge.objects.get(challenge=challenge, user=request.user)
        # if user is returning to question without finishing first time
        if old_attempted_challenge.start_datetime == old_attempted_challenge.end_datetime:
            # time taken is never > 5 hours
            if ((datetime.now() - old_attempted_challenge.start_datetime).seconds / 3600) > 5:
                if (old_attempted_challenge.time_taken == 0):
                    old_attempted_challenge.time_taken = timedelta(hours=5)
        # if user is attempting challenge again
        else:
            update_time = datetime.now()
            old_attempted_challenge.start_datetime = update_time
            old_attempted_challenge.end_datetime = update_time
            print(old_attempted_challenge.start_datetime == old_attempted_challenge.end_datetime)
        print(old_attempted_challenge.time_taken)
        old_attempted_challenge.save()
    # if not ever attempted before by user
    else:
        new_attempted_challenge = UserAttemptedChallenge(challenge=challenge, user=request.user)
        new_attempted_challenge.save()

    context = {
        'challenge': challenge,
        'user_data': user_data,
        'hint_number': hint_number,
        'topic': topic,
    }

    return render(request, 'pages/code_editor.html', context)


# helper function to return random opponent other than user
def get_opponent(request, challenge):
    no_of_possible_opponents = UserAttemptedChallenge.objects.filter(challenge=challenge).count()

    # if no one has ever attempted this question
    if no_of_possible_opponents == 1:
        return UserAttemptedChallenge(challenge=challenge, user=request.user, time_taken=timedelta(seconds=18000), grade=0)

    random_opponent_index = random.randint(1, no_of_possible_opponents)

    random_opponent = UserAttemptedChallenge.objects.filter(challenge=challenge)[random_opponent_index-1]

    if (random_opponent.user == request.user):
        return get_opponent(request, challenge)
    else:
        return random_opponent




def result_update(request):
    coins_earned = 0
    points_earned = 0
    winner = "none"
    time_winner = "none"
    opponent_grade = 0
    opponent_hours = 0
    opponent_minutes = 0
    opponent_seconds = 0
    status = "Keep Codding"
    opponent_name = "None"
    play_dp = False
    play_fw = False

    level_before = Level.objects.get(user=request.user)

    old_level = level_before.level

    progress = level_before.progress

    # get current topic name
    if 'topic_name' in request.POST:
        request.session['topic_name'] = request.POST['topic_name']

    # get current challenge
    if 'challenge_id' in request.POST:
        challenge_id = request.POST['challenge_id']

    challenge = Challenge.objects.get(id=challenge_id)


    if 'grade' in request.POST:
        grade = math.ceil(float(request.POST['grade']) * 100)

    # grade = math.ceil(float(0.2) * 100)

    # user rank before this challenge
    old_rank = get_user_rank(request.user)

    # user points before
    old_points = TotalPoints.objects.get(user=request.user).points

    # user coins before adding final coins
    after_hints_coins = TotalCoins.objects.get(user=request.user).coins

    # user coins before buying hints
    old_coins = after_hints_coins

    # Update user stats for this challenge
    attempted_challenge = UserAttemptedChallenge.objects.get(user=request.user, challenge=challenge)
    
    # yeah.. I don't remember why I did this
    if (attempted_challenge.start_datetime == attempted_challenge.end_datetime):
        attempted_challenge.end_datetime = datetime.now()
        attempted_challenge.save()
        # maybe this means if user has completed this question for first time
        if attempted_challenge.time_taken == timedelta(seconds=0):
            play_dp = True
            if ((attempted_challenge.end_datetime - attempted_challenge.start_datetime).seconds / 3600) > 5:
                attempted_challenge.time_taken = timedelta(hours=5)
            else:
                attempted_challenge.time_taken = (attempted_challenge.end_datetime - attempted_challenge.start_datetime)
            if challenge.difficulty == "easy":
                points_earned = math.ceil(5 * (grade / 100))
            elif challenge.difficulty == "medium":
                points_earned = math.ceil(7 * (grade / 100))
            else:
                points_earned = math.ceil(10 * (grade / 100))
            
            attempted_challenge.save()
            coins_earned = points_earned * 2
            update_user_points(request, points_earned)
            update_user_coins(request, coins_earned)
            attempted_challenge.grade = grade

            # get opponent
            opponent = get_opponent(request, challenge)

            if opponent.user != request.user:
                winner = "user"
                opponent_name = opponent.user.username

            opponent_grade = opponent.grade
            opponent_hours = str(opponent.time_taken.seconds // 3600)
            opponent_minutes = str(opponent.time_taken.seconds % 3600 // 60)
            opponent_seconds = str(opponent.time_taken.seconds % 60)

            if opponent.time_taken > attempted_challenge.time_taken:
                time_winner = "user"
            elif opponent.time_taken == attempted_challenge.time_taken:
                time_winner = "draw"
            else:
                time_winner = "opponent"

            # check if free hit is active
            free_win = FreeWin.objects.filter(challenge=challenge, user=request.user)

            if free_win:
                play_fw = True
                winner = "user"
            else:
                if (grade > opponent.grade):
                    winner = "user"
                elif (grade == opponent.grade):
                    if opponent.time_taken > attempted_challenge.time_taken:
                        winner = "user"
                    elif opponent.time_taken == attempted_challenge.time_taken:
                        winner = "draw"
                    else:
                        winner = "opponent"
                else:
                    winner = "opponent"

            # manage user's level

            level = Level.objects.get(user=request.user)
            level.tries = level.tries + 1

            if winner == "user":
                level.progress = level.progress + 3
            elif winner == "draw":
                level.progress = level.progress + 1
            level.save()

            progress = level.progress

            if level.progress >= 9:
                level.level = level.level + 1
                status = "Promoted"
                level.points = 0
                level.tries = 0

            if (level.progress < 4 and level.tries == 5) or (level.progress == 0 and level.tries == 4) :
                if level.level != 1:
                    level.level = level.level - 1
                    status = "Relegated"
                    level.points = 0
                    level.tries = 0
            level.save()
    else:
        return redirect('index')

    if attempted_challenge.grade == 0:
        attempted_challenge.grade = grade
    
    attempted_challenge.save()

    time_taken = attempted_challenge.time_taken

    level = Level.objects.get(user=request.user)

    # if double points chip is active
    double_point = DoublePoint.objects.filter(challenge=challenge, user=request.user)
    if double_point:
        if play_dp == True:
            points_earned = points_earned*2

    request.session['tries'] = level.tries
    request.session['level'] = level.level
    request.session['old_level'] = old_level
    request.session['hours'] = str(time_taken.seconds // 3600)
    request.session['minutes'] = str(time_taken.seconds % 3600 // 60)
    request.session['seconds'] = str(time_taken.seconds % 60)
    request.session['old_rank'] = old_rank
    request.session['old_points'] = old_points
    request.session['old_coins'] = old_coins
    request.session['points_earned'] = points_earned
    request.session['coins_earned'] = coins_earned
    request.session['grade'] = grade
    request.session['winner'] = winner
    request.session['time_winner'] = time_winner
    request.session['opponent_grade'] = opponent_grade
    request.session['opponent_hours'] = opponent_hours
    request.session['opponent_minutes'] = opponent_minutes
    request.session['opponent_seconds'] = opponent_seconds
    request.session['opponent_name'] = opponent_name
    request.session['status'] = status
    request.session['challenge_id'] = challenge_id
    request.session['progress'] = progress
    request.session['play_dp'] = play_dp
    request.session['play_fw'] = play_fw

    return redirect('result')

def result(request):

    # yeah I'm an idiot

    old_rank = request.session.get('old_rank')
    old_points = request.session.get('old_points')
    old_coins = request.session.get('old_coins')
    topic_name = request.session.get('topic_name')
    challenge_id = int(request.session.get('challenge_id'))
    hours = request.session.get('hours')
    minutes = request.session.get('minutes')
    seconds = request.session.get('seconds')
    grade = int(request.session.get('grade'))
    winner = request.session.get('winner')
    time_winner = request.session.get('time_winner')
    opponent_grade = request.session.get('opponent_grade')
    opponent_hours = request.session.get('opponent_hours')
    opponent_minutes = request.session.get('opponent_minutes')
    opponent_seconds = request.session.get('opponent_seconds')
    opponent_name = request.session.get('opponent_name')
    status = request.session.get('status')
    tries = int(request.session.get('tries'))
    level = int(request.session.get('level'))
    old_level = int(request.session.get('old_level'))
    progress = int(request.session.get('progress'))
    play_dp = request.session.get('play_dp')
    play_fw = request.session.get('play_fw')


    # managing user progress this way because I'm not cool enough
    rel_progress = 0
    stay_progress = 0
    pro_progress = 0
    if progress == 1:
        rel_progress = 25
    elif progress == 2:
        rel_progress = 50
    elif progress == 3:
        rel_progress = 75
    elif progress == 4:
        rel_progress = 100
    elif progress == 5:
        rel_progress = 100
        stay_progress = 20
    elif progress == 6:
        rel_progress = 100
        stay_progress = 40
    elif progress == 7:
        rel_progress = 100
        stay_progress = 60
    elif progress == 8:
        rel_progress = 100
        stay_progress = 80
    elif progress == 9:
        rel_progress = 100
        stay_progress = 100
    elif progress == 10:
        rel_progress = 100
        stay_progress = 100
        pro_progress = 16.5
    elif progress == 11:
        rel_progress = 100
        stay_progress = 100
        pro_progress = 33.3
    elif progress == 12:
        rel_progress = 100
        stay_progress = 100
        pro_progress = 50
    elif progress == 13:
        rel_progress = 100
        stay_progress = 100
        pro_progress = 66.6
    elif progress == 14:
        rel_progress = 100
        stay_progress = 100
        pro_progress = 83.3
    elif progress == 15:
        rel_progress = 100
        stay_progress = 100
        pro_progress = 100
    


    # Fetch current topic
    topic = get_object_or_404(Topic, topicName=topic_name)
    
    challenge = Challenge.objects.get(id=challenge_id)

     # total number of users who attempted this challenge
    total_users = UserAttemptedChallenge.objects.filter(challenge=challenge).count()

    # get new rank
    new_rank = get_user_rank(request.user)

    # get new user points
    new_points = TotalPoints.objects.get(user=request.user).points

    # get new user points
    new_coins = TotalCoins.objects.get(user=request.user).coins

    # all users who attempted current challenge sorted
    all_users = UserAttemptedChallenge.objects.filter(challenge=challenge).order_by('-grade', 'time_taken')

    rank = 1
    for user in all_users:
        if user.user == request.user:
            break
        rank += 1

    # average points
    average_points_aggregate = UserAttemptedChallenge.objects.filter(challenge=challenge).aggregate(Avg('grade'))
    average_points = int(average_points_aggregate['grade__avg'])

    # user's grade compare to average
    grade_compare = grade - average_points

    # average time taken
    average_time_taken = UserAttemptedChallenge.objects.filter(challenge=challenge).aggregate(Avg('time_taken'))
    average_minutes_taken = round(average_time_taken['time_taken__avg'].seconds / 60, 1)

    # get user's minutes taken
    user_minutes_taken = round(UserAttemptedChallenge.objects.get(challenge=challenge, user=request.user).time_taken.seconds / 60 ,1)

    # user's minutes compared to average
    minutes_compare = int(((user_minutes_taken - average_minutes_taken) / average_minutes_taken) * 100)

    abs_minutes_compare = 0

    if minutes_compare < 0:
        abs_minutes_compare = minutes_compare  * -1
    
    context = {
        'topic': topic,
        'challenge': challenge,
        'old_rank': old_rank,
        'old_points': old_points,
        'old_coins': old_coins,
        'total_users': total_users,
        'hours': int(hours),
        'minutes': int(minutes),
        'seconds': int(seconds),
        'new_rank': new_rank,
        'rank_change': new_rank - old_rank,
        'new_points': new_points,
        'points_change': new_points - old_points,
        'coins_earned': (new_points - old_points)*2,
        'new_coins': new_coins,
        'coins_change': new_coins - old_coins,
        'rank': rank,
        'average_points': average_points,
        'average_minutes_taken': average_minutes_taken,
        'grade_compare': grade_compare,
        'minutes_compare': minutes_compare,
        'abs_minutes_compare': abs_minutes_compare,
        'all_users': all_users,
        'grade': grade,
        'opponent_grade': opponent_grade,
        'opponent_name': opponent_name,
        'opponent_hours': int(opponent_hours),
        'opponent_seconds': int(opponent_seconds),
        'opponent_minutes': int(opponent_minutes),
        'status': status,
        'winner': winner,
        'time_winner': time_winner,
        'tries': 5 - tries,
        'level': level,
        'old_level': old_level,
        'level_before': old_level - 1,
        'level_after': old_level + 1,
        'rel_progress': rel_progress,
        'stay_progress': stay_progress,
        'pro_progress': pro_progress,
        'play_dp': play_dp,
        'play_fw': play_fw,
    }
    return render(request, 'pages/result.html', context)

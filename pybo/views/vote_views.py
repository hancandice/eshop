from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from ..models import Question, Answer

@login_required(login_url='account_login')
def voteQuestion(request, questionId):
    question = get_object_or_404(Question, pk=questionId)
    if request.user == question.author:
        messages.warning(request, "You can't 'Like' your own post")
    else:
        question.voter.add(request.user)
    return redirect('pybo:detail', questionId=question.id)

    # Question 모델의 vorter는 여러사람을 추가할 수 있는 ManyToManyField이므로 question.voter.add(request.user) 처럼 add 함수를 사용하여 추천인을 추가해야 한다. 
    # ※ 동일한 사용자가 동일한 질문을 여러번 추천하더라도 추천수가 증가하지는 않는다. ManyToManyField를 사용하더라도 중복은 허락되지 않는다.

@login_required(login_url='account_login')
def voteAnswer(request, answerId):
    answer = get_object_or_404(Answer, pk=answerId)
    if request.user == answer.author:
        messages.warning(request, "You can't 'Like' your own post")
    else:
        answer.voter.add(request.user)
    return redirect('pybo:detail', questionId=answer.question.id)
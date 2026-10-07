from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as login_django, logout
from django.contrib.auth.decorators import login_required
from .models import Perfil, Escola, Questao, Alternativa, TentativaQuestao
from urllib.parse import urlencode

def cadastro(request):
    escolas = Escola.objects.all().order_by("nome")

    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        escola_id = request.POST.get("escola")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get("confirmar_senha")

        if len(nome.split()) < 2:
            messages.error(request, "Você deve inserir seu nome completo")
            return render(request, "cadastro.html", {"escolas": escolas})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Esse email ja está cadastrado")
            return render(request, "cadastro.html", {"escolas": escolas})

        if len(senha) < 8:
            messages.error(request, "A senha deve ter pelo menos 8 caracteres")
            return render(request, "cadastro.html", {"escolas": escolas})

        if senha != confirmar_senha:
            messages.error(request, "Os campos devem ter a mesma senha")
            return render(request, "cadastro.html", {"escolas": escolas})

        escola = Escola.objects.get(id=escola_id)

        user = User.objects.create_user(username=email, email=email, password=senha)
        Perfil.objects.create(usuario=user, nome=nome, escola=escola)

        messages.success(request, "Cadastro realizado com sucesso")
        return redirect("login")

    return render(request, "cadastro.html", {"escolas": escolas})

def login(request):

    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        user = authenticate(request, username=email, password=senha)

        print("USUÁRIO:", user)

        if user is not None:
            login_django(request, user)
            print("LOGIN REALIZADO")
            return redirect("questoes")
        
        messages.error(request, "E-mail ou senha incorretos")
    return render(request, "login.html")

@login_required
def questoes(request):
    questoes = Questao.objects.all()
    perfil = Perfil.objects.get(usuario=request.user)
    filtro = request.GET.get("filtro", "todas")

    questoes_acertadas = Questao.objects.filter(tentativaquestao__perfil=perfil, tentativaquestao__acertou=True).distinct()
    questoes_respondidas = Questao.objects.filter(tentativaquestao__perfil=perfil).distinct()
    questoes_nao_respondidas = Questao.objects.exclude(id__in=questoes_respondidas.values("id"))
    questoes_erradas = questoes_respondidas.exclude(id__in=questoes_acertadas.values("id"))

    if filtro == "acertadas":
        questoes = questoes_acertadas
    elif filtro == "erradas":
        questoes = questoes_erradas
    elif filtro == "nao_respondidas":
        questoes = questoes_nao_respondidas

    print("ERRADAS:", questoes_erradas)
    if request.method == "POST":
        alternativa_id = request.POST.get("alternativa")
        alternativa = Alternativa.objects.get(id=alternativa_id)
        questao = alternativa.questao

        tentativas = TentativaQuestao.objects.filter(perfil=perfil, questao=questao).count()
        numero_tentativa = tentativas + 1

        xp_ganho = 0

        if alternativa.e_correta and numero_tentativa == 1:
            if questao.dificuldade == "Fácil":
                xp_ganho = 1
            elif questao.dificuldade == "Médio":
                xp_ganho = 2
            elif questao.dificuldade == "Difícil":
                xp_ganho = 3

        perfil.xp += xp_ganho
        perfil.save()

        TentativaQuestao.objects.create(
            xp_ganho=xp_ganho,
            acertou=alternativa.e_correta,
            numero_tentativa=numero_tentativa,
            perfil=perfil,
            questao=questao,
            alternativa=alternativa
        )

        alternativa_correta = Alternativa.objects.get(questao=questao, e_correta=True)

        if alternativa.e_correta:
            messages.success(request, f"Você acertou! +{xp_ganho} XP")
        else:
            messages.error(request, f"Você errou! A alternativa correta é item {alternativa_correta.letra}.")

        return redirect(f"/auth/questoes/?filtro={filtro}")
    
    return render(request, "questoes.html", {"questoes": questoes, "filtro": filtro})






@login_required
def conteudos(request):
    questoes = Questao.objects.all()

    return render(request, "questoes.html", {"questoes": questoes})

@login_required
def ranking(request):
    questoes = Questao.objects.all()

    return render(request, "questoes.html", {"questoes": questoes})

@login_required
def sobre(request):
    questoes = Questao.objects.all()

    return render(request, "questoes.html", {"questoes": questoes})

def logout_view(request):
    logout(request)
    return redirect("login")
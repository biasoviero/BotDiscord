from itertools import count
import discord
from unidecode import unidecode
from discord.ext import commands
import requests
import json
from random import shuffle, choice, randint
import os

client = commands.Bot(command_prefix='elton ')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#Informa os comandos disponíveis
@client.command()
async def info(ctx):
    embed = discord.Embed(title="Comandos Elton John bot", description = "Cada comando tem o prefixo elton", color = 0xf541af)
    embed.add_field(name = "jogo_da_velha", value = "Mencionados  dois membros do server, é iniciado um jogo da velha", inline=False)
    embed.add_field(name = "place", value="Apenas funciona durante um jogo da velha, após chamar o comando, é esperado um número de 1 a 9", inline=False)
    embed.add_field(name = "forca", value="Escolhe uma palavra aleatória e inicia um jogo de forca", inline=False)
    embed.add_field(name = "letra", value="É esperado uma letra, apenas funciona enquanto estiver ocorrendo um jogo de forca", inline=False)
    embed.add_field(name = "times", value="Após digitar nomes, são sorteados dois times e, caso o número de jogadores seja ímpar, é escolhido um jogador que começará fora do jogo", inline=False)
    embed.add_field(name = "server", value="Mostra informações sobre o server", inline=False)
    embed.add_field(name = "wiki", value="Sorteia duas páginas da Wikipedia para jogar The Wiki Game, cujo objetivo é achar um caminho a partir da primeira página sorteada que chegue até a segunda página sorteada.", inline=False)
    await ctx.send(embed=embed)


#Jogo da Wikipedia#

#Seleciona um artigo aleatório da Wikipedia
def get_wiki():
    response = requests.get('https://pt.wikipedia.org/api/rest_v1/page/random/summary')
    json_data = json.loads(response.text)
    link = json_data.pop('content_urls')
    link = link.pop('desktop')
    link = link.pop('page')
    image = json_data.pop('thumbnail')
    image = image.pop('source')
    artigo = {
        'title' : json_data.pop('title'),
        'image' : image,
        'description' : json_data.pop('extract'),
        'link' : link}
    return artigo

#Inicia um jogo novo
@client.command()
async def wiki(ctx):
    entrada = get_wiki()
    saída = get_wiki()

    embedE = discord.Embed(
         title = 'THE WIKI GAME',
         color =0xf541af)
    embedE.set_thumbnail(url = entrada.pop('image'))
    embedE.add_field(name = entrada.pop("title"), 
    value =  f'{entrada.pop("description").capitalize()}\n{entrada.pop("link")}', 
    inline = False)
    embedS = discord.Embed(
          color =0xf541af)
    embedS.add_field(name = saída.pop("title"), value =  f'{saída.pop("description").capitalize()}\n{saída.pop("link")}', inline = False)
    embedS.set_thumbnail(url = saída.pop('image'))
    await ctx.send(embed = embedE)
    await ctx.send(embed = embedS)

#Jogo da Forca#

#Seleciona uma palavra aleatória do dicionário
def get_word():
    response = requests.get('https://api.dicionario-aberto.net/random')
    json_data = json.loads(response.text)
    palavra = json_data['word']
    return palavra

#Inicia um jogo
@client.command()
async def forca(ctx):
    global palavra
    global jogo
    global repetidas
    global lista
    global chances
    global fim
    palavra = str(get_word()).strip().upper()
    jogo = []
    repetidas = []
    lista = []
    chances = 0
    print(palavra)
    fim = True

    if fim == True:
        for i in range(0, len(palavra)):
            jogo.append(':white_small_square:')

        for letra in palavra:
            lista.append(letra)
            if ''.join(jogo) == palavra:
                fim = True
            elif chances == 6:
                fim = True
        embedJ= discord.Embed(color = 0xf541af, 
        description = ''.join(jogo))
        await ctx.send(embed = embedJ)
    else:
        await ctx.send('Já está rolando um jogo! Espera terminar antes de começa outro.')

#Informa uma letra
@client.command()
async def letra(ctx, letra):
    global chances
    global lista
    global repetidas
    global palavra
    global fim
    fim = False
    if fim == False:
        if letra.isalpha() == True:
            letra = letra.upper()
            if letra not in repetidas:
                for index, value in enumerate(lista):
                    if value == '-' or value == ' ' or letra == unidecode(value):
                        jogo[index] = value
                if letra not in unidecode(palavra):
                    chances += 1
                repetidas.append(letra)
                embedJ= discord.Embed(color = 0xf541af, 
                description = ''.join(jogo))
                await ctx.send(embed = embedJ)
                if ''.join(jogo) == palavra:
                    embedV = discord.Embed(title = 'Ganhou!',
                    color = 0xf541af)
                    embedV.set_image(url = 'https://c.tenor.com/25rTRRgixjMAAAAd/elton-john.gif')
                    await ctx.send(embed = embedV)
                    fim = True
                elif chances == 6:
                    embedF = discord.Embed(title = 'FORCA!',
                    color = 0xf541af,
                    description = f'Perdeu o jogo, a palavra era {palavra}')
                    embedF.set_image(url = 'https://c.tenor.com/V6qR89YfhkkAAAAS/fell-down-fall.gif')
                    await ctx.send(embed = embedF)
                    fim = True
                embedL = discord.Embed(title = 'Letras tentadas',
                color = 0xf541af,
                description = f'{",".join(repetidas)}\nVidas: {(6-chances)}')
                await ctx.send(embed  =embedL)
                
            else:
                await ctx.send('Essa já foi. Escolhe outra!')
        else:
            await ctx.send('Não digitou uma letra.')
    else:
        await ctx.send('Começa um jogo antes de digitar uma letra.')

#Erro em que a letra não é informada
@letra.error
async def letra_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Faltou a letra.')

#Jogo da Velha#

#Inicializando o tabuleiro
player1 = ''
player2 = ''
turn =''
gameOver = True
board = []
conditions = [
    [0,1,2],
    [3,4,5],
    [6,7,8],
    [0,3,6],
    [1,4,7],
    [2,5,8],
    [0,4,8],
    [2,4,6]
]

@client.command()
#Inicia um jogo da velha
async def jogo_da_velha(ctx, p1:discord.Member, p2 :discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver
    if gameOver:
        global board
        board = [":white_large_square:",":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ''
        gameOver = False
        count = 0
        player1 = p1
        player2 = p2
        line =''

        for x in range(len(board)):
            if x ==2 or x == 5 or x ==8:
                line += ' ' + board[x]
                await ctx.send(line)
                line = ''
            else:
                line += ' ' + board[x]
        
        n = randint(1,2)
        if n == 1:
            turn = player1
            await ctx.send(f'{str(player1.name)} começa.')
        elif n == 2:
            turn = player2
            await ctx.send(f'{str(player2.name)} começa.')
    else:
        await ctx.send('Já está rolando um jogo, espera terminar!')

@client.command()
#Posiciona no jogo da velha
async def place(ctx, pos : int):
    global count
    global player1
    global player2
    global turn
    global gameOver
    global board

    if not gameOver:
        mark = ''
        if turn == ctx.author:
            if turn == player1:
                mark = ':x:'
            elif turn == player2:
                mark = ':o:'
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                board[pos-1] = mark
                count += 1

                line = ''
                for x in range(len(board)):
                    if x == 2 or x==5 or x==8:
                        line += ' ' + board[x]
                        await ctx.send(line)
                        line = ''
                    else:
                        line += ' ' + board[x]
                
                checkWinner(conditions, mark)
                if gameOver == True:
                    await ctx.send(turn.name + ' ganhou')
                    await ctx.send('https://tenor.com/view/oh-yeah-feathers-hello-there-bird-birdman-gif-13606398')
                elif count >= 9:
                    gameOver = True
                    await ctx.send('Deu velha!')
                    await ctx.send('https://tenor.com/view/elton-confused-mystified-thinking-elton-john-gif-19050130')
                
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send('Escolhe um número entre 1 e 9.')
        else:
            await ctx.send('Não é a tua vez!')
    else:
        await ctx.send('Começa um jogo novo!')

#Checa se há um vencedor
def checkWinner(conditions, mark):
    global gameOver
    for condition in conditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

#Erro ao informar os nomes dos jogadores
@jogo_da_velha.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Coloque dois jogadores após o comando.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Coloque o @ na frente dos nomes.')

#Erro ao informar a posição desejada
@place.error
async def place_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Põe uma posição válida.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Põe um número.')

#Mostra as informações do servidor
@client.command()
async def server(ctx):
    name = ctx.guild.name
    description = ctx.guild.description
    owner = ctx.guild.owner
    id = ctx.guild.id
    region = ctx.guild.region
    memberCount = ctx.guild.member_count
    icon = ctx.guild.icon_url
    embed = discord.Embed(
        title = 'Informações do Server ' + name,
        color =0xf541af,
        description= description)
    embed.set_thumbnail(url=icon)
    embed.add_field(name='Dono do server', value = owner, inline=True)
    embed.add_field(name='ID do server', value=id, inline=True)
    embed.add_field(name='Número de membros',value=memberCount, inline=True)
    await ctx.send(embed=embed)

#Comando que recebe nomes e sorteia dois times
@client.command()
async def times(ctx, *args):
    lista = []
    for arg in args:
        arg = str(arg).title()
        lista.append(arg)

    shuffle(lista)
    quantidade = len(lista)
    pessoas_grupo = quantidade / 2
    grupos = 2

    embed = discord.Embed(
        title = 'Sorteio dos Times',
        color =0xf541af)

    if quantidade % 2 == 0:
        grupos_sorteados = [lista[i::grupos] for i in range(grupos)]
        embed.add_field(name='Grupo 1', value =f'{", ".join(str(x) for x in grupos_sorteados[0])}' , inline=False)
        embed.add_field(name='Grupo 2', value =f'{", ".join(str(x) for x in grupos_sorteados[1])}' , inline=False)
    else:
        sobra = choice(lista)
        lista.remove(sobra)
        grupos_sorteados = [lista[i::grupos] for i in range(grupos)]
        embed.add_field(name='Grupo 1', value =f'{", ".join(str(x) for x in grupos_sorteados[0])}', inline=False)
        embed.add_field(name='Grupo 2', value =f'{", ".join(str(x) for x in grupos_sorteados[1])}', inline=False)
        embed.add_field(name='Sobra', value =f'O jogador {sobra} revezará a sua vez.', inline=False)
        
    await ctx.send(embed=embed)    


client.run('TOKEN')

# Автоматическая раздача подарков ВКонтакте на форуме lolz.guru
# by REMEMBER https://lolz.guru/members/5116193 https://github.com/1member1

# lolzteam api https://github.com/grisha2217/Lolzteam-Public-API/blob/master/docs/


import requests
from time import sleep
from loguru import logger as p
from random import randint as rand
from threading import Thread

#------------------------------VARIABLES-------------------------------------------
proxies='' # Proxies dict, Example : {"https":"http://login:password@127.0.0.1:80"}

messages_to_send=[]

posts = []

data=eval(open('config.json').read()) # import config

tokens=open('tokens.txt').read().split('\n')


manual="""[SPOILER="Что делать если адрес неверный?"]Убедитесь, что вы ввели ник без форматирований, попробуйте ввести ник вручную!
Например если ваш ник был окружен буквами B например BnickB, значит ваш ник выделен [B]жирным шрифтом,[/B] введите ник вручную!
Если ник слишком длинный проверьте, чтобы он не был объединен с предыдущим

[IMG]https://i.imgur.com/svemhR4.png[/IMG][/SPOILER]"""

additional_text="""Дополнительный текст"""

ignore_vk_list=[]

gift_id=data["vk"]["gift_id"]

token_worker=data["vk"]["token_worker"]
#----------------------------------------------------------------------------------

#----------------------------------SOME MODULES-------------------------------------

def clean_link(url): # clean link
	return str(url[url.find("']")+1:]).replace(']','').replace('[', '').replace('/','').replace('URL','').replace('www.','').replace('m.','').replace('vk.com','').replace("SRCI","").replace("\n","").replace(' ','').replace('https:','').replace('http:','').replace(',', '')

with open('allpost.txt', "r") as f: # import ignore posts
	for s in f:
		posts.append(int(s))

def add(p): # add to ignore list
	with open('allpost.txt', "a") as f:
		f.write(str(p)+"\n")
	posts.append(p)


def send_gift(vk_id):
	if tokens:
		try:
			req=requests.get(f"https://api.vk.com/method/gifts.send?user_ids={vk_id}&access_token={tokens[0]}&v=5.126&gift_id={gift_id}&guid={rand(1,9999999)}").json()
			print(req)
			if req["response"]["success"]:
				return True
		except Exception as e:
			pass
		p.info(f"{tokens[0]} Удален!")

		tokens.remove(tokens[0])
		send_gift(vk_id)
	else:
		p.info('Токены закончились!')
		exit()
#----------------------------------------------------------------------------------



def getPosts():
	res=requests.get(f'https://lolz.guru/api/index.php?posts/&thread_id={data["lzt"]["thread_id"]}', proxies=proxies).json()
	try:
		pages=res['links']['pages'] # Get last page
	except:
		pages = 1 # if none pages
	p.info('Parsed')
	return requests.get(f'https://lolz.guru/api/index.php?posts/&thread_id={data["lzt"]["thread_id"]}&page={pages}', proxies=proxies).json()['posts']

def sendMes_thread():
	p.info('Thread sender started')
	while True:
		sleep(1)
		for mes in messages_to_send:
			sleep(5)
			messages_to_send.remove(mes)
			try:
				print(requests.post(url='https://lolz.guru/api/index.php?posts',data={'quote_post_id': mes[0],'thread_id': data["lzt"]["thread_id"],'post_body': mes[1]},headers={'Authorization': 'Bearer '+data["lzt"]["token"],'Cookie': 'xf_logged_in=1'}, proxies=proxies).text)
			except Exception as e:
				print(e)
				try:
					print(requests.post(url='https://lolz.guru/api/index.php?posts',data={'quote_post_id': mes[0],'thread_id': data["lzt"]["thread_id"],'post_body': mes[1]},headers={'Authorization': 'Bearer '+data["lzt"]["token"],'Cookie': 'xf_logged_in=1'}, proxies=proxies).text)
				except Exception as e:
					print(e)
			
			

def pars(): 
	p.info('Thread pars started')
	while True:
		sleep(rand(30,45))
		try:
			post = getPosts()
		except Exception as e:
			print(e)
			continue
		for i in range(len(post)):
			postId, postBody, postUser, postUsername = post[i]['post_id'],post[i]['post_body'],post[i]['poster_user_id'],post[i]['poster_username']
			if postUser == data["lzt"]["creator_id"]:
				continue
			if postId in posts:
				continue
			p.info(postUsername)
			add(postId)
			username=clean_link(postBody)
			if len(str(username)) > 33:
				messages_to_send.append((postId,f"""Максимальная длина адреса ВКонтакте 32 символа

{manual}

{additional_text}"""))
				continue
			if username == "Скрытыйконтент":
				messages_to_send.append((postId,f"""К сожалению, я не умею читать хайды!

Пожалуйста, отправь ссылку/id аккаунта без хайда!

{additional_text}"""))
				continue
			try:
				vk_id=requests.get(f"https://api.vk.com/method/users.get?user_ids={username}&access_token={token_worker}&v=5.126").json()['response'][0]['id']
			except:
				messages_to_send.append((postId,f"""Пользователя [SRCI]{username}[/SRCI] не существует ВКонтакте

{manual}

{additional_text}"""))
				continue

			if vk_id in ignore_vk_list:
				messages_to_send.append((postId,f"""Пользователю [SRCI]{username}[/SRCI] уже был отправлен подарок!
ID пользователя: [SRCI]{vk_id}[/SRCI]

{manual}

{additional_text}"""))
				continue

			send_gift(vk_id)
			messages_to_send.append((postId,f"""Пользователю [SRCI]{username}[/SRCI] был отправлен подарок!
ID пользователя: [SRCI]{vk_id}[/SRCI]

{manual}


{additional_text}"""))
			if data["lzt"]["resending"] == False:
				ignore_vk_list.append(vk_id)

Thread(target=pars).start()
Thread(target=sendMes_thread).start()

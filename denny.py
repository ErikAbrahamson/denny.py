import requests
import json
import sys
import discord
import re
import os
import random
import logging
import signal
from datetime import date, timedelta, datetime
from textgenrnn import textgenrnn

IMGFLIP_USERNAME = os.getenv('IMGFLIP_USERNAME')
IMGFLIP_PASSWORD = os.getenv('IMGFLIP_PASSWORD')
TOKEN = os.getenv('DENNY_DISCORD_TOKEN')

MODEL_DIR = os.getcwd() + '/model/v1/'
env_has_cuda = os.name == 'nt'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
client = discord.Client()

class DennyClient(discord.Client):
    async def on_ready(self):
        print('discord.py version {}'.format(discord.__version__))
        print('Logged in as {}'.format(client.user.name))
        print('-------------------------------------------------')

    #async def join(self):


    async def on_message(message):
        if message.author == client.user:
            return

        def predicate(message):
            return not message.author.bot

        batch_size = 1024 if env_has_cuda else 128
        match = re.findall('(?i)denny', message.content)
        train = re.findall('(?i)homework', message.content)
        meme = re.findall('(?i)meme', message.content)

        model = textgenrnn(
            config_path=MODEL_DIR + 'denny_config.json',
            weights_path=MODEL_DIR + 'denny_weights.hdf5',
            vocab_path=MODEL_DIR + 'denny_vocab.json')

        if match:
            async with message.channel.typing():
                msg = ''
                try:
                    if train and env_has_cuda:
                        print('Training Denny...')
                        model.train_on_texts(msgs, max_length=10, new_model=False,
                            batch_size=batch_size,
                            num_epochs=100,
                            gen_epoch=50
                        )
                        model.save('./model/v1/denny_weights.hdf5')
                        print(model.model.summary())
                    elif meme:
                        random_meme = random.choice(meme_list['data']['memes'])
                        num_input = random_meme['box_count']

                        msglist = model.generate(num_input, return_as_list=True, temperature=0.9)
                        payload = {
                                'username': IMGFLIP_USERNAME,
                                'password': IMGFLIP_PASSWORD,
                                'template_id': str(random_meme['id']),
                                'text0': msglist[0],
                                'text1': msglist[1]
                        }
                        r = requests.post('https://api.imgflip.com/caption_image', data=payload)
                        resp = r.json()
                        msg = resp['data']['url']
                except:
                    msg = model.generate(1, return_as_list=True, temperature=0.7)[0]
                if msg == '' or msg.startswith('<'):
                    msg = model.generate(1, return_as_list=True, temperature=0.6)[0]
                await message.channel.send(msg)

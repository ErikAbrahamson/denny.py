import requests
import json
import sys
import discord
import re
import os
import random
import markovify
import logging
import signal
from datetime import date, timedelta, datetime
from textgenrnn import textgenrnn

IMGFLIP_USERNAME = os.getenv('IMGFLIP_USERNAME')
IMGFLIP_PASSWORD = os.getenv('IMGFLIP_PASSWORD')
TOKEN = os.getenv('DENNY_DISCORD_TOKEN')

MODEL_DIR = os.getcwd() + '/model/v1/'
on_desktop = os.name == 'nt'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
client = discord.Client()

#logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='./discord.log', encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)

@client.event
async def on_ready():
    print('discord.py version {}'.format(discord.__version__))
    print('Logged in as {}'.format(client.user.name))
    print('-------------------------------------------------')

@client.event
async def on_message(message):
    print(message.author)
    if message.author == client.user:
        return

    def predicate(message):
        return not message.author.bot

    batch_size = 1024 if on_desktop else 128
    match = re.findall('(?i)denny', message.content)
    spicy = re.findall('(?i)spicy', message.content)
    spicier = re.findall('(?i)spicier', message.content)
    spiciest = re.findall('(?i)spiciest', message.content)
    crazy = re.findall('(?i)most', message.content)
    train = re.findall('(?i)homework', message.content)
    meme = re.findall('(?i)meme', message.content)

    textgen = textgenrnn(
        config_path= MODEL_DIR + 'denny_config.json',
        weights_path=MODEL_DIR + 'denny_weights.hdf5',
        vocab_path=MODEL_DIR + 'denny_vocab.json')

    if match:
        async with message.channel.typing():
            msg = ''
            try:
                if train:
                    if on_desktop:
                        print('Training Denny...')
                        textgen.train_on_texts(msgs, max_length=10, new_model=False,
                            batch_size=batch_size,
                            num_epochs=100,
                            gen_epoch=50
                        )
                        textgen.save('./model/v1/denny_weights.hdf5')
                        print('Model saved!')
                        print(textgen.model.summary())

                    result = 'Bitch I\'m not GPU enabled in this chunk of metal, but here\'s a summary:\n'
                    stringlist = []
                    textgen.model.summary(print_fn=lambda x: stringlist.append(x))
                    full_summary = result + '\n'.join(stringlist)
                    msg = full_summary[0:2000]

                elif spicy:
                    print('Setting temperature to 0.8...')
                    msg = textgen.generate(1, return_as_list=True, temperature=0.8)[0]
                elif spicier:
                    print('Setting temperature to 1.2...')
                    msg = textgen.generate(1, return_as_list=True, temperature=1.2)[0]
                elif spiciest or crazy:
                    print('Setting temperature to 1.5...')
                    msg = textgen.generate(2, return_as_list=True, temperature=1.6)[0]
                elif meme:
                    print('Trying meme')
                    with open('./meme_list.json') as l:
                        meme_list = json.load(l)

                    #random_meme = random.choice(meme_list['data']['memes'])
                    random_meme = meme_list['data']['memes'][1]
                    num_input = random_meme['box_count']

                    msglist = textgen.generate(num_input, return_as_list=True, temperature=0.9)
                    payload = {
                            'username': IMGFLIP_USERNAME,
                            'password': IMGFLIP_PASSWORD,
                            'template_id': str(random_meme['id'])
                    }

                    # API is borked
                    #if num_input > 2:
                    #    boxes = []
                    #    for i in range(num_input):
                    #        boxes.append({'text': str(msglist[i])})
                    #        print(boxes[i])

                    #    payload.update({'boxes': boxes})
                    #else:
                    payload.update({'text0': msglist[0]})
                    payload.update({'text1': msglist[1]})

                    print('PAYLOAD: {}'.format(payload))
                    r = requests.post('https://api.imgflip.com/caption_image', data=payload)
                    resp = r.json()
                    print(resp)
                    msg = resp['data']['url']
            except:

                print('fallback')
                msg = textgen.generate(1, return_as_list=True, temperature=0.7)[0]

            if msg == '' or msg.startswith('<'):
                msg = textgen.generate(1, return_as_list=True, temperature=0.6)[0]
            await message.channel.send(msg)

try:
    while True:
        client.run(TOKEN)
except KeyboardInterrupt:
        print('Stopping Denny')

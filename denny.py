import requests
import json
import discord
import re
import os
import random
from textgenrnn import textgenrnn

IMGFLIP_USERNAME = os.getenv('IMGFLIP_USERNAME')
IMGFLIP_PASSWORD = os.getenv('IMGFLIP_PASSWORD')

TOKEN = os.getenv('DENNY_DISCORD_TOKEN')

ENV_HAS_CUDA = os.name == 'nt'
BATCH_SIZE = 1024 if ENV_HAS_CUDA else 128
MODEL_DIR = os.getcwd() + '/model/v1/'
client = discord.Client()


class DennyClient(discord.Client):
    default_temp: 0.9
    model = textgenrnn(
        config_path=MODEL_DIR + 'denny_config.json',
        weights_path=MODEL_DIR + 'denny_weights.hdf5',
        vocab_path=MODEL_DIR + 'denny_vocab.json')

    # @client.event
    async def on_ready(self):
        print('discord {}'.format(discord.__version__))
        print('Logged in as {}'.format(self.user.name))
        print('--------------------------------------')

    def create_meme(self):
        with open('./meme_list.json') as lst:
            meme_list = json.load(lst)

        random_meme = random.choice(meme_list['data']['memes'])
        num_input = random_meme['box_count']
        msgs = self.model.generate(num_input, return_as_list=True,
                                   temperature=self.default_temp)
        params = {
            'username': IMGFLIP_USERNAME,
            'password': IMGFLIP_PASSWORD,
            'template_id': str(random_meme['id']),
            'text0': msgs[0],
            'text1': msgs[1]
        }
        r = requests.post('https://api.imgflip.com/caption_image', data=params)
        resp = r.json()
        return resp['data']['url']

    # @client.event
    async def on_message(self, message):
        if message.author == self.user:
            return
        await message.channel.send(self.generate_response())

    def train(self):
        self.model.train_on_texts(msgs,
                                  max_length=10,
                                  new_model=False,
                                  batch_size=BATCH_SIZE,
                                  num_epochs=100,
                                  gen_epoch=50)

        self.model.save(MODEL_DIR + 'denny_weights.hdf5')
        print(self.model.model.summary())

    def generate_response(self, message):
        match = re.findall('(?i)denny', message.content)
        train = re.findall('(?i)homework', message.content)
        meme = re.findall('(?i)meme', message.content)
        resp = self.model.generate(1, return_as_list=True,
                                          temperature=self.default_temp)[0]
        if match:
            async with message.channel.typing():
                if meme:
                    return self.create_meme()
                elif train and ENV_HAS_CUDA:
                    self.train()
                    return 'Finished my homework!'
                else:
                    if len(resp) == 0:
                        resp = self.model.generate(1, return_as_list=True,
                                                   temperature=0.5)[0]
                    return resp

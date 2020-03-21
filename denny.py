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
MODEL_DIR = os.getcwd() + '/model/v1/'


class DennyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    default_temp = 0.9
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
        try:
            if message.author == self.user:
                return

            resp = self.generate_response(message)

            with message.channel.typing():
                print('Sending message: {}'.format(resp))
                await message.channel.send(resp)

        except discord.HTTPException:
            return

    async def train(self, message):
        try:
            history = await message.channel.history(limit=20000).flatten()
            messages = []

            for m in history:
                line = m.content
                not_author = 'Denny' not in m.author.name
                not_referenced = 'denny' not in m.content.lower()

                if not_author and not_referenced:
                    messages.append(line)

            num_epochs = 100 if ENV_HAS_CUDA else 5
            batch_size = 1024 if ENV_HAS_CUDA else 128
            gen_epoch = 50 if ENV_HAS_CUDA else 1

            self.model.train_on_texts(messages,
                                      max_length=10,
                                      new_model=False,
                                      batch_size=batch_size,
                                      num_epochs=num_epochs,
                                      gen_epoch=gen_epoch)

            self.model.save(MODEL_DIR + 'denny_weights.hdf5')
            print(self.model.model.summary())

        except discord.HTTPException:
            # TODO: Save history to file periodically
            return

    def generate_response(self, message):
        match = re.findall('(?i)denny', message.content)
        train = re.findall('(?i)homework', message.content)
        meme = re.findall('(?i)meme', message.content)

        resp = self.model.generate(1, return_as_list=True,
                                   temperature=self.default_temp)[0]
        if match:
            if meme:
                return self.create_meme()

            elif train and ENV_HAS_CUDA:
                self.train(message)
                return 'Finished my homework!'

            else:
                if len(resp) == 0 or resp.startswith('<'):
                    resp = self.model.generate(1, return_as_list=True,
                                               temperature=0.5)[0]
                return resp


if __name__ == "__main__":
    client = DennyClient()
    client.run(TOKEN)

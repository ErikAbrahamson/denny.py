import requests
import json
import discord
import io
import datetime
import os
import random
import urllib.request
from textgenrnn import textgenrnn

from dream import deep_dream
from corona import get_corona_stats
from dice import roll_the_dice

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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
        with open(os.getcwd() + '/assets/meme/meme_list.json') as lst:
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

            if 'denny' in message.content.lower():
                with message.channel.typing():
                    await self.generate(message)

            elif isinstance(message.channel, discord.DMChannel):
                await self.generate(message)

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
            return

    def dice_roll(self):
        img_path, nick = roll_the_dice()

        with open(img_path, 'rb') as image:
            reader = image.read()

        f = discord.File(io.BytesIO(reader), filename='result.png')
        embed = discord.Embed(title=nick, color=discord.Color.dark_orange())

        embed.set_image(url=f"""attachment://result.png""")
        return embed, f

    async def make_dream(self, message):
        if len(message.attachments) > 0:
            attachment = message.attachments[0]

            try:
                img_bytes = await attachment.read()
                image_path = deep_dream(img_bytes)

                with open(image_path, 'rb') as image:

                    reader = image.read()
                f = discord.File(io.BytesIO(reader), filename='dream.jpg')
                embed = discord.Embed(color=discord.Color.dark_blue())

                embed.set_image(url=f"""attachment://dream.jpg""")
                return embed, f

            except discord.NotFound:
                return
        else:
            return

    async def generate(self, message, msg=None, f=None, embed=None):
        if 'meme' in message.content.lower():
            msg = self.create_meme()

        elif 'dice' in message.content.lower():
            emb, result = self.dice_roll()
            f = result
            embed = emb

        elif 'homework' in message.content.lower():
            await self.train(message)
            msg = 'Finished my homework!'

        elif 'dream' in message.content.lower():
            emb, img = await self.make_dream(message)
            embed = emb
            f = img

        elif 'corona' in message.content.lower():
            embed = get_corona_stats(message=message)

        else:
            msg = self.model.generate(1, return_as_list=True,
                                      temperature=self.default_temp)[0]

            if len(msg) == 0 or msg.startswith('<'):
                msg = self.model.generate(1, return_as_list=True,
                                          temperature=1.0)[0]
        try:
            if msg is None and embed is None and f is None:
                return
            else:
                await message.channel.send(content=msg, embed=embed, file=f)

        except discord.HTTPException:
            return
        except discord.NotFound:
            return
        except discord.Forbidden:
            return
        except discord.InvalidArgument:
            return


client = DennyClient()
client.run(TOKEN)

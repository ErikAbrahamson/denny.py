import random
import datetime
import urllib
import json
import numbers
import discord

def get_corona_stats(message, embed=None, randomize=False):
    def embed_country(country):
        embed = discord.Embed(title=country['country'],
                              color=discord.Color.gold())

        embed.add_field(name='Total Cases:',
                        value=fmt_num(country['cases']))
        embed.add_field(name='Cases Today:',
                        value=fmt_num(country['todayCases']))
        embed.add_field(name='Total Deaths:',
                        value=fmt_num(country['deaths']))
        embed.add_field(name='Deaths Today:',
                        value=fmt_num(country['todayDeaths']))
        embed.add_field(name='Active Cases:',
                        value=fmt_num(country['active']))
        embed.add_field(name='Critical Cases:',
                        value=fmt_num(country['critical']))
        embed.add_field(name='Cases per Million:',
                        value=fmt_num(country['casesPerOneMillion']))
        embed.add_field(name='Deaths per Million:',
                        value=fmt_num(country['deathsPerOneMillion']))
        embed.add_field(name='Total Recovered:',
                        value=fmt_num(country['recovered']))

        date = datetime.datetime.fromtimestamp(
            country['updated']/1000.0)

        date = date.strftime('%Y-%m-%d %H:%M:%S')

        url = country['countryInfo']['flag']
        embed.set_thumbnail(url=url)

        source = 'https://worldometers.info/coronavirus'
        source_title= 'Source Aggregate @ {}:'.format(date)

        embed.add_field(name=source_title, value=source, inline=True)

        return embed

    def fmt_num(raw):
        if isinstance(raw, numbers.Number):
            return '{:,}'.format(raw)
        else:
            return 'N/A'

    agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)' \
        'Gecko/2009021910 Firefox/3.0.7'

    url = 'https://corona.lmao.ninja/states'
    headers = {'User-Agent': agent}

    req = urllib.request.Request(url, None, headers)
    res = urllib.request.urlopen(req)
    results = json.loads(
        res.read().decode(res.info().get_param('charset') or 'utf-8'))

    for state in results:
        if state['state'].lower() in message.content.lower():
            embed = discord.Embed(title=state['state'],
                                    color=discord.Color.dark_gold())

            embed.add_field(name='Total Cases:',
                            value=fmt_num(state['cases']))
            embed.add_field(name='Cases Today:',
                            value=fmt_num(state['todayCases']))
            embed.add_field(name='Total Deaths:',
                            value=fmt_num(state['deaths']))
            embed.add_field(name='Deaths Today:',
                            value=fmt_num(state['todayDeaths']))
            embed.add_field(name='Active Cases:',
                            value=fmt_num(state['active']))

            name = state['state'].replace(' ', '-').lower()
            url = 'https://raw.githubusercontent.com/CivilServiceUSA/'\
                'us-states/master/images/flags/{}-large.png'.format(name)

            embed.set_thumbnail(url=url)

            date = datetime.datetime.today()
            date = date.strftime('%Y-%m-%d %H:%M:%S')

            embed.add_field(name='Fetched At:', value=date)

            source = 'https://worldometers.info/coronavirus'
            embed.add_field(name='Source Aggregate:',
                            value=source, inline=False)

            return embed

    url = 'https://corona.lmao.ninja/countries'

    req = urllib.request.Request(url, None, headers)
    res = urllib.request.urlopen(req)
    results = json.loads(
        res.read().decode(res.info().get_param('charset') or 'utf-8'))

    if randomize is True:
        return embed_country(random.choice(results))

    for country in results:
        if country['country'].lower() in message.content.lower():
            return embed_country(country)


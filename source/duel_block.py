import discord
from discord_components import *
from .db import Session
from .verify import get_user
import random



class DuelBlock:
    def __init__(self, user1, user2):
        self.user1 = Duelist(user1)
        self.user2 = Duelist(user2)
        self.buttons = [[Button(style=ButtonStyle.blue, label='Post'),
                         Button(style=ButtonStyle.blue, label='Lurk'),
                         Button(style=ButtonStyle.blue, label='React'),
                         Button(style=ButtonStyle.red, label='Cancel')]]
        self.file = discord.File('media/images/duel_advantage.png', filename='thumbnail.gif')

        self.embed = discord.Embed(title=f'{user1.display_name} has challenged {user2.display_name} to a duel!', color=discord.Color.dark_red())
        self.embed.set_thumbnail(url='attachment://thumbnail.gif')
        self.embed.add_field(name='\u200b', value=self.user1.get_team_field(), inline=True)
        self.embed.add_field(name='\u200b', value='\u200b', inline=True)
        self.embed.add_field(name='\u200b', value=self.user1.get_stat_field(), inline=True)
        self.embed.add_field(name='\u200b', value='**vs**', inline=False)
        self.embed.add_field(name='\u200b', value=self.user2.get_team_field(), inline=True)
        self.embed.add_field(name='\u200b', value='\u200b', inline=True)
        self.embed.add_field(name='\u200b', value=self.user2.get_stat_field(), inline=True)

    def process_button(self, button):
        if button.author.id == self.user1.id:
            self.user1.attack = button.component.label
        elif button.author.id == self.user2.id:
            self.user2.attack = button.component.label

    def get_winner(self):
        if self.user1.damage > self.user2.damage:
            return self.user1
        return self.user2

    def duel(self):
        # determine who, if anyone, has advantage (0, 1 ,2)
        # Post -> Lurk -> React
        if self.user1.attack == self.user2.attack:
            advantage = 0
        elif self.user1.attack == 'Post':
            if self.user2.attack == 'Lurk':
                advantage = 1
            else:
                advantage = 2
        elif self.user1.attack == 'Lurk':
            if self.user2.attack == 'React':
                advantage = 1
            else:
                advantage = 2
        else:
            if self.user2.attack == 'Post':
                advantage = 1
            else:
                advantage = 2

        x = self.user1.get_stat() + self.user2.get_stat()
        if advantage == 0:
            self.user1.damage = random.randint(1, x)
            self.user2.damage = random.randint(1, x)
        elif advantage == 1:
            self.user1.damage = max(random.randint(1, x), random.randint(1, x))
            self.user2.damage = min(random.randint(1, x), random.randint(1, x))
        else:
            self.user1.damage = min(random.randint(1, x), random.randint(1, x))
            self.user2.damage = max(random.randint(1, x), random.randint(1, x))


class Duelist:
    def __init__(self, user):
        self.id = user.id
        self.name = user.display_name
        self.attack = None

        self.post = 0
        self.lurk = 0
        self.react = 0
        self._set_stats()

        self.damage = 0

    def _set_stats(self):
        session = Session()
        my_user = get_user(session, str(self.id))
        self.active = my_user.get_active(session)

        for card in self.active:
            self.post += card.post
            self.lurk += card.lurk
            self.react += card.react

    def get_team_field(self):
        if len(self.active) == 0:
            return 'None'
        session = Session()
        field = f'**Team {self.name}**\n'
        for card in self.active:
            field += f'{card.get_title(session)}\n'
        return field

    def get_stat_field(self):
        field = f'**Total stats**\n**{self.post}**(post) - **{self.lurk}**(lurk) - **{self.react}**(react)'
        return field

    def get_stat(self):
        if self.attack == 'Post':
            return self.post
        elif self.attack == 'Lurk':
            return self.lurk
        elif self.attack == 'React':
            return self.react





import discord
from discord_components import *
from source.verify import get_user


class TradeBlock:
    def __init__(self, user1, user2, command):
        self.user1 = Trader(user1)
        self.user2 = Trader(user2)

        self.buttons = [[Button(style=ButtonStyle.green, label=user1.display_name),
                         Button(style=ButtonStyle.red, label="Cancel"),
                         Button(style=ButtonStyle.green, label=user2.display_name)]]

        self.embed = discord.Embed(title="Trade Pending",
                                   description=f'{user1.display_name} has proposed a trade to {user2.display_name}',
                                   color=discord.Color.purple())

        self.embed.add_field(name=user1.display_name, value='None', inline=False)
        self.embed.add_field(name=user2.display_name, value='None', inline=False)
        self.embed.add_field(name='.', value=command, inline=False)

    def get_user(self, user_id):
        if user_id == self.user1.id:
            return self.user1
        elif user_id == self.user2.id:
            return self.user2

    def add_block(self, session, user_id, my_card, quantity):
        trade_user = self.get_user(user_id)
        my_user = get_user(session, str(user_id))

        if my_user.get_quantity(session, my_card.id) < quantity:
            return False
        if my_card in trade_user.field:
            trade_user.field[my_card] += quantity
        else:
            trade_user.field[my_card] = quantity
        self.update_embed(trade_user)
        return True

    def remove_block(self, user_id, my_card, quantity):
        trade_user = self.get_user(user_id)

        if my_card in trade_user.field:
            trade_user.field[my_card] -= quantity
            if trade_user.field[my_card] <= 0:
                del trade_user.field[my_card]
            self.update_embed(trade_user)
            return True
        return False

    def update_embed(self, trade_user):
        if trade_user.id == self.user1.id:
            index = 0
        else:
            index = 1

        field_value = ''
        for card in trade_user.field:
            field_value += f'{trade_user.field[card]}x  **{card.title}**  ({card.id})\n'
        if len(trade_user.field) == 0:
            field_value = 'None'
        self.embed.set_field_at(index, name=f'{trade_user.name} gives:', value=field_value, inline=False)

    def reset_buttons(self):
        self.buttons[0][0] = Button(style=ButtonStyle.green, label=self.user1.name)
        self.buttons[0][2] = Button(style=ButtonStyle.green, label=self.user2.name)
        self.user1.accept = False
        self.user2.accept = False

    def accept_button(self, button_text):
        if button_text == self.user1.name:
            self.buttons[0][0] = Button(style=ButtonStyle.blue, label=self.user1.name)
            self.user1.accept = True
        elif button_text == self.user2.name:
            self.buttons[0][0] = Button(style=ButtonStyle.blue, label=self.user2.name)
            self.user2.accept = True


class Trader:
    def __init__(self, user):
        self.id = int(user.id)
        self.name = user.display_name
        self.field = {}
        self.accept = False

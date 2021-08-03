import discord
from discord.ext import commands
from discord_components import *
from source.db import Session
from source.config import COMMAND_PREFIX
from source.verify import verify_mentioned, verify_card, get_user
from source.models.user import User
import asyncio


# TODO: test extensively

async def get_response(self, ctx, user1, user2):
    def check_message(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            if m.content[0] == '+' or m.content[0] == ['-']:
                return True
            return False

    def check_button(b):
        but_text = b.component.label
        if but_text == 'Cancel':
            return b.author == ctx.author and b.channel == ctx.channel
        if ctx.author == user1:
            return but_text == user1.display_name
        if ctx.author == user2:
            return but_text == user2.display_name

    # wait for message or response
    task_block = asyncio.create_task(self.bot.wait_for("message", check=check_message))
    task_button = asyncio.create_task(self.bot.wait_for("button_click", check=check_button))
    done, pending = await asyncio.wait([task_block, task_button], return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()
    msg = None
    button = None
    if task_block in done:
        msg = await task_block
    if task_button in done:
        button = await task_button
    return msg, button


def check_add(session, user_id, card_id, quantity):
    my_user1 = session.query(User).filter(User.id == user_id).one_or_none()
    if my_user1 is None:
        return False
    if my_user1.check_collection(session, card_id, quantity) is False:
        return False
    return True


def check_remove(my_card, quantity, user_field):
    if my_card in user_field:
        if user_field[my_card] >= quantity:
            return True
    return False


def get_field_value(user_field):
    field_value = ''
    for card in user_field:
        field_value += f'{user_field[card]}x {card.title}\n'
    if len(user_field) == 0:
        field_value = 'None'
    return field_value


# verifies that commands to edit the trade block are correct, with a card name and quantity
async def parse_command_block(session,ctx, m):
    try:
        sign = m[0]
        m_split = m[1:].split()
        quantity = m_split[-1]
    except IndexError as e:
        return False, None, None

    card = ' '.join(m_split[:-1])
    my_card = await verify_card(session, ctx, card)

    if not card or not quantity.isdigit() or my_card is False:
        return False, None, None
    return sign, my_card, int(quantity)


def execute_trade(session, user1, user2, field):
    my_user1 = get_user(session, str(user1.id))
    my_user2 = get_user(session, str(user2.id))

    user_field = field[user1]
    for card in user_field:
        my_user1.remove_from_collection(session, card.id, user_field[card])
        my_user2.add_to_collection(session, card.id, user_field[card])

    user_field = field[user2]
    for card in user_field:
        my_user2.remove_from_collection(session, card.id, user_field[card])
        my_user1.add_to_collection(session, card.id, user_field[card])


class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1)
    async def trade(self, ctx):
        command = f'```{COMMAND_PREFIX}t @user```'
        command_block = f'```+/- [card name/id] [quantity]```'
        session = Session()

        # Get both users for the trade
        user1 = ctx.author
        user2 = await verify_mentioned(ctx, command)
        if user2 is False:
            session.rollback()
            return False

        # Create the initial buttons
        buttons = [[Button(style=ButtonStyle.green, label=user1.display_name),
                    Button(style=ButtonStyle.red, label="Cancel"),
                    Button(style=ButtonStyle.green, label=user2.display_name)]]

        # Create the trade block embed
        embed = discord.Embed(title="Trade Pending",
                              description=f'{user1.display_name} has proposed a trade to {user2.display_name}',
                              color=discord.Color.purple())
        embed.set_image(url='attachment://image.png')
        embed.add_field(name=user1.display_name, value='None', inline=False)
        embed.add_field(name=user2.display_name, value='None', inline=False)
        embed.add_field(name='.', value=command_block, inline=False)

        fields = {user1: {}, user2: {}}

        # Trade loop until both users press accept button.  Buttons are reset upon editing trade block
        user1_accept = False
        user2_accept = False
        while True:
            file = discord.File('./media/images/trade.gif', filename='image.png')

            # Send the embed and buttons
            m = await ctx.send(file=file, embed=embed, components=buttons)

            # Wait for either a message command or button response from users
            msg, button = await get_response(self, ctx, user1, user2)

            if msg:
                # Parse the command message to make sure it is formatted correctly and that the card exists
                sign, my_card, quantity = await parse_command_block(session, ctx, msg.content)
                if sign is False:
                    await ctx.send(f'To add or remove cards from the trade block, use:\n{command_block}')
                    continue

                # Check if users have the appropriate cards in collection or on block to perform the commands
                if sign == '+':
                    if check_add(session, str(ctx.author.id), my_card.id, quantity) is False:
                        await ctx.send(f'<@{ctx.author.id}> does not have {quantity}x **{my_card.title}** to add to the trade block')
                    else:
                        user_field = fields[ctx.author]
                        if my_card in user_field:
                            user_field[my_card] += quantity
                        else:
                            user_field[my_card] = quantity
                elif sign == '-':
                    if check_remove(my_card.id, quantity, user_field[ctx.author]) is False:
                        await ctx.send(f'<@{ctx.author.id}> does not have {quantity}x **{my_card.title}** on the trade block')
                    else:
                        fields[ctx.author[my_card]] -= quantity
                        if fields[ctx.author[my_card]] == 0:
                            del fields[ctx.author[my_card]]

                # Update the embed with the edited fields{}
                field_value = get_field_value(fields[user1])
                embed.set_field_at(0, name=f'{user1.display_name} gives:', value=field_value, inline=False)
                field_value = get_field_value(fields[user2])
                embed.set_field_at(1, name=f'{user2.display_name} gives:', value=field_value, inline=False)

                # Reset buttons and user_accept booleans
                user1_accept = False
                user2_accept = False
                buttons[0][0] = Button(style=ButtonStyle.green, label=user1.display_name)
                buttons[0][2] = Button(style=ButtonStyle.green, label=user2.display_name)

            # Handle button response
            if button:
                res_text = button.component.label
                await button.respond(type=6)
                if res_text == 'Cancel':
                    await m.edit(components=[])
                    await ctx.send('Trade cancelled.')
                    return

                elif res_text == user1.display_name:
                    user1_accept = True
                    buttons[0][0] = Button(style=ButtonStyle.blue, label=user1.display_name)

                else:
                    user2_accept = True
                    buttons[0][2] = Button(style=ButtonStyle.blue, label=user2.display_name)

            if user1_accept and user2_accept:
                execute_trade(session, user1, user2, fields)
                session.commit()
                await ctx.send("Trade succeeded.")
            await m.delete()

def setup(bot):
    bot.add_cog(Trade(bot))

from discord.ext import commands
from source.db import Session
from source.config import COMMAND_PREFIX
from source.verify import verify_mentioned, get_card, get_user
from source.trade_block import TradeBlock
import asyncio


# Waits for the user to respond via message or button, returns both
async def get_response(self, ctx, user1, user2):
    def check_message(m):
        if (m.author.id == user1.id or m.author.id == user2.id) and m.channel == ctx.channel:
            if m.content[0] == '-' or m.content[0] == '+':
                return True
            return False

    def check_button(b):
        but_text = b.component.label
        if but_text == 'Cancel':
            return b.author.id == user1.id or b.author.id == user2.id
        if b.author.id == user1.id:
            return but_text == user1.name
        if b.author.id == user2.id:
            return but_text == user2.name
        return False

    # wait for message or response
    try:
        task_block = asyncio.create_task(self.bot.wait_for("message", check=check_message, timeout=180))
        task_button = asyncio.create_task(self.bot.wait_for("button_click", check=check_button, timeout=180))
        done, pending = await asyncio.wait([task_block, task_button], return_when=asyncio.FIRST_COMPLETED)
    except asyncio.TimeoutError:
        return False, False

    for task in pending:
        task.cancel()
    msg = None
    button = None
    if task_block in done:
        msg = await task_block
    if task_button in done:
        button = await task_button
    return msg, button


async def parse_command_block(session, ctx, m):
    try:
        sign = m[0]
        m_split = m[1:].split()
        quantity = m_split[-1]

    except IndexError as e:
        return False, None, None

    card = ' '.join(m_split[:-1])
    if card != '':
        my_card = await get_card(session, ctx, card)

    if not card or not quantity.isdigit() or my_card is False:
        return False, None, None
    return sign, my_card, int(quantity)


def execute_trade(session, user1, user2):
    my_user1 = get_user(session, str(user1.id))
    my_user2 = get_user(session, str(user2.id))

    for card in user1.field:
        my_user1.remove_from_deck(session, card.id, user1.field[card])
        my_user2.add_to_deck(session, card.id, user1.field[card])

    for card in user2.field:
        my_user2.remove_from_deck(session, card.id, user2.field[card])
        my_user1.add_to_deck(session, card.id, user2.field[card])


class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1)
    async def trade(self, ctx):
        command = f'```{COMMAND_PREFIX}t @user```'
        command_block = f'```+/- [card name/id] [quantity]```'

        # Get both users for the trade
        user1 = ctx.author
        user2 = await verify_mentioned(ctx, command)
        if user2 is False:
            return False

        # Create the trade block, which will manage the embed and buttons
        trade_block = TradeBlock(user1, user2, command_block)
        session = Session()

        m = await ctx.send(embed=trade_block.embed, components=trade_block.buttons)
        while True:
            await m.edit(embed=trade_block.embed, components=trade_block.buttons)

            msg, button = await get_response(self, ctx, trade_block.user1, trade_block.user2)
            if msg is False:
                session.rollback()
                await ctx.send("Trade timed out.")
                return

            if msg:
                sign, my_card, quantity = await parse_command_block(session, ctx, msg.content)
                if sign == '+':
                    if trade_block.add_block(session, msg.author.id, my_card, quantity) is False:
                        await ctx.send(
                            f'<@{msg.author.id}> does not have {quantity}x **{my_card.title}** to add to the trade block')
                        trade_block.reset_buttons()

                elif sign == '-':
                    if trade_block.remove_block(msg.author.id, my_card, quantity) is False:
                        await ctx.send(
                            f'<@{msg.author.id}> does not have {quantity}x **{my_card.title}** on the trade block')
                        trade_block.reset_buttons()

            if button:
                res_text = button.component.label
                await button.respond(type=6)

                if res_text == 'Cancel':
                    await m.edit(components=[])
                    await ctx.send('Trade cancelled.')
                    return

                trade_block.accept_button(res_text)

            if trade_block.user1.accept and trade_block.user2.accept:
                execute_trade(session, trade_block.user1, trade_block.user2)
                session.commit()
                await m.edit(components=[])
                await ctx.send("Trade succeeded.")


def setup(bot):
    bot.add_cog(Trade(bot))

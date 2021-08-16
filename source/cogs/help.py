from discord.ext import commands
from source.config import ROLE_PERM


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['h', 'H', '?'])
    async def help(self, ctx):

        # Add basic commands to formatted string
        msg = f"```css\n[ BASIC COMMANDS ]\nYou can use either the card title or id for commands.  If the card title " \
                    f"is multiple words, they must be enclosed in quotes.\n" \
              f".pull                ::  'Gives you your cards for the day.  Refreshes at midnight EST.'}}\n" \
              f".upgrade [card]      ::  'Upgrades the card if you have enough fragments.'}}\n" \
              f".destroy [card]      ::  'Destroys the card, giving you your fragments back at a slightly reduced " \
                    f"rate.'}}\n" \
              f".view [card] [level] ::  'Views the card at the given level.  The level argument is optional and " \
                    f"defaults to level 1.'}}\n" \
              f".deck                ::  'Allows you to browse the cards you own, and all relevant information about " \
                    f"them.'}}\n" \
              f".activate [card x3]  ::  'You may have up to 3 cards active at a time to use in duels.  Your active " \
                    f"cards must all belong to the same house.'}}\n" \
              f"\n[ MULTI-USER COMMANDS ]" \
              f".trade [@user]       ::  'Initiate trade with the pinged user.  Use +/- as prompted by the command " \
                    f"to add or remove items to the trade block.  Both users must accept the trade by clicking the " \
                    f"button with their name on it.  Either user could cancel at any time.'}}\n" \
              f".duel [@user]        ::  'Initiate a duel with the pinged user.  The stats from your active cards " \
                    f"will be totaled, and both duelists will select 1 of 3 attacks to use. Dueling uses rock-paper-" \
                    f"scissor mechanics to determine if a duelist gains an advantage.  POST beats LURK beast REACT.'}}\n" \

        # If the author is an admin, add the admin commands
        user_roles = []
        for role in ctx.author.roles:
            user_roles.append(role.name)
        if ROLE_PERM in user_roles:
            msg += f"\n[ ADMIN - EDIT CARDS ]\n" \
                   f".customcard          ::  'Facilitates the creation of a custom card by asking you to enter in " \
                        f"the relevant information.  Information could be edited before final submittal.  Once " \
                        f"accepted, the card is created.'}}\n" \
                   f".usercard [@user]    ::  'Facilitates the creation of a card based off a user, automatically " \
                        f"using their display name and avatar, while asking you to fill in the rest of the needed " \
                        f"information.  Information could be edited before final submittal.  Once accepted, the card " \
                        f"is created.'}}\n" \
                   f".editcard [card]     ::  'Allows the editing of existing cards, permanently updating them.  " \
                        f"You could edit the following: Title, Art, House, Stats, Flavor Text.  You CANNOT edit the " \
                        f"rarity, nor the set that it is a part of.'}}\n" \
                   f".removecard [card]   ::  'Permanently removes the card, including from the decks of all players." \
                        f"  So be careful.'}}\n" \
                   f"\n[ ADMIN - EDIT USER DECKS ]\n" \
                   f".add [card] [amount] [@user]    :: 'Adds the requested amount of card fragments to the pinged " \
                        f"players deck.'}}\n" \
                   f".remove [card] [amount] [@user] :: 'Removes the requested amount of card fragments to the pinged" \
                        f" players deck.'}}\n" \
                   f".level [card] [level] [@user]   :: 'Sets the level of the card in the pinged players deck.'}}\n" \
                   f"\n[ ADMIN - EDIT SETS ]\n" \
                   f".addset [ID] [name]   :: 'Creates a new set, which new cards can then be created for.'}}\n" \
                   f".removeset [ID]       :: 'Removes a set, but only if no cards belong to it yet.  Otherwise, " \
                        f"all such cards would be wiped from players collections.'}}\n" \
                   f"\n[ ADMIN - OTHER ]\n" \
                   f".boost [ID]           :: 'Boosts a chosen set to have >50% chance of being drawn when pulling" \
                        f" cards.  This affects all users, as well as the FREEPULL commands'}}\n" \
                   f".freepull [amount] [@user]      :: 'Gives a free pull of between 1 and 5 cards to the pinged" \
                        f" player.'}}\n"
        msg += "```"


def setup(bot):
    bot.add_cog(Help(bot))

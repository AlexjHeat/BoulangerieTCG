from PIL import Image, ImageDraw, ImageFont
from source.config import COLOR_STR
from source.models.card_level import CardLevel
import textwrap


def add_art(im_template, path):
    with Image.open(f'{path}') as im_art:
        im_art = im_art.resize((642, 511))
        im_template.paste(im_art, (52, 146))
    return im_template


def add_title(im_template, title):
    draw = ImageDraw.Draw(im_template)

    for size in range(25, 67):
        name_font = ImageFont.FreeTypeFont("./media/fonts/BAHNSCHRIFT.ttf", size=size)
        name_font.set_variation_by_name("SemiBold Condensed")
        w, h = name_font.getsize(title)
        if w > 350 or h > 60:
            break
    draw.text((60, 92), title, fill='#f6f4e8', font=name_font, anchor="lm")
    return im_template

def add_id(im_template, id, house):
    draw = ImageDraw.Draw(im_template)

    id_font = ImageFont.FreeTypeFont("./media/fonts/BAHNSCHRIFT.ttf", size=36)
    id_font.set_variation_by_name("SemiBold Condensed")
    draw.text((515, 60), f'#{id}', fill=COLOR_STR[house], font=id_font, anchor="ra")

    return im_template


def add_emblem(im_template, house, level):
    emblem_address = f'./media/templates/{house}_emblem{level}.png'
    with Image.open(emblem_address) as im_emblem:
        im_template.paste(im_emblem, (0, 0), im_emblem)
    return im_template


def add_flavor(im_template, flavor):
    # TODO: Invent algorithm for dynamic flavor text size
    draw = ImageDraw.Draw(im_template)
    flavor_font = ImageFont.FreeTypeFont("./media/fonts/BAHNSCHRIFT.ttf", size=40)
    flavor_font.set_variation_by_name("SemiBold SemiCondensed")

    rows = flavor.split('\n')
    for i in range(len(rows)):
        rows[i] = "\n".join(textwrap.wrap(rows[i], 40))
    flavor = "\n".join(rows)

    draw.multiline_text((375, 810), flavor, fill="#4b443c", font=flavor_font, anchor='mm', spacing=12)
    return im_template


def add_stats(im_template, post, lurk, react):
    draw = ImageDraw.Draw(im_template)
    stat_font = ImageFont.FreeTypeFont("./media/fonts/BAHNSCHRIFT.ttf", size=50)
    stat_font.set_variation_by_name("Bold SemiCondensed")

    draw.text((90, 1022), str(post), fill='#f6f4e8', font=stat_font, anchor='mm')
    draw.text((344, 1022), str(lurk), fill='#f6f4e8', font=stat_font, anchor='mm')
    draw.text((607, 1022), str(react), fill='#f6f4e8', font=stat_font, anchor='mm')
    return im_template


def create_image(session, my_card, level):
    if level < 6:
        template_address = f'./media/templates/{my_card.house.name}.png'
    elif level < 7:
        template_address = f'./media/templates/{my_card.house.name}6.png'
    else:
        template_address = f'./media/templates/{my_card.house.name}7.png'

    try:
        with Image.open(template_address) as im_template:
            im_template = add_art(im_template, my_card.artPath)
            im_template = add_title(im_template, my_card.title)
            im_template = add_id(im_template, my_card.id, my_card.house.name)
            im_template = add_emblem(im_template, my_card.house.name, level)
            im_template = add_flavor(im_template, my_card.flavor)

            q_level = session.query(CardLevel).filter(CardLevel.card_id == my_card.id, CardLevel.level == level).first()
            im_template = add_stats(im_template, q_level.post, q_level.lurk, q_level.react)

        im_template.save(f'./media/cards/{my_card.id}_{level}.png')
        q_level.artPath = f'./media/cards/{my_card.id}_{level}.png'
    except FileNotFoundError as e:
        print(type(e))
        print(f'File path does not exist for opening/saving during creation of {my_card.id}-{level}')
        return False

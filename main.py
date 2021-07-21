from PIL import Image, ImageDraw, ImageFont
# Reference: https://stackoverflow.com/questions/67760340/how-to-add-text-in-a-textbox-to-an-image

address_template = "./Media/Templates/provence_lvl0.png"
address_pfp = "./Media/pfp/pfp1.png"
with Image.open(address_template) as im_template:
    with Image.open(address_pfp) as im_pfp:
        im_pfp = im_pfp.resize((643, 512))
        im_template.paste(im_pfp, (52, 146))

    im_template.save("./Media/test.png", quality=95)

    # TODO: Re-paste the emblem such that it goes over the pfp, make sure it's transparent.

    draw_template = ImageDraw.Draw(im_template)


    # Name Labeling
    name_shape = [(65, 60), (500, 115)]
    draw_template.rectangle(name_shape, fill=None)

    name = "test"
    selected_size = 0
    for size in range(12, 100):
        name_font = ImageFont.FreeTypeFont("./Media/Fonts/BAHNSCHRIFT.ttf", size=size)
        print(name_font.get_variation_names())
        name_font.set_variation_by_name("SemiBold SemiCondensed")
        w, h = name_font.getsize(name)
        selected_size = size
        if w > 500 or h > 100:
            break

    draw_template.text((65, 30), name, fill=None,font=name_font)

    # TODO: Tack on Flavor Text

    # TODO: Tack on react, post, lurk
    im_template.show()

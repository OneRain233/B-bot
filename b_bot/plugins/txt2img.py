from multiprocessing.context import SpawnContext
from PIL import Image, ImageFont, ImageDraw
import sys


class txt2img():
    def __init__(self, txt, img_path, font_size, font_path):
        self.txt = txt
        self.img_path = img_path
        self.font_size = font_size
        self.padding = 50
        self.spacing = 10
        self.margin = 10
        self.max_width = 1080
        self.font = ImageFont.truetype(font_path, self.font_size)

    def dertermin_txt_size(self, txt, spacing, right_paddind=0, left_padding=0):
        l = txt.split("\n")
        w = max([_ for _ in map(lambda x: self.font.getsize(x)[0], l)]) + right_paddind + left_padding
        h = sum([self.font.getsize(x)[1] for x in l]) + (len(l) - 1) * spacing
        return w, h

    def warp(self):
        res = ""
        t = self.txt.split("\n")
        max_char = int(1080 / self.font_size)
        for i in t:
            if len(i) > max_char:
                res += i[:max_char] + "\n"
                res += i[max_char:] + "\n"
            else:
                res += i + "\n"
        return res


    def save(self):
        padding = 50
        spacing = 10
        margin = 10
        self.txt = self.warp()
        w, h = self.dertermin_txt_size(self.txt, spacing, padding,padding)
        img = Image.new("RGB", (w,h + margin*2), (0, 0, 0))
        draw = ImageDraw.Draw(img)  
        draw.text((padding, margin), self.txt, (255, 255, 255), font=self.font, spacing=spacing)

        # img.save(self.img_path)
        # img.show()
        return img

if __name__ == "__main__":
    txt2img("1231231231231231231231231231123123123123123123123123123123123123\n456\n789", "test.png",20).save()

from datetime import date, datetime

_date, pic = "2022-4-29/2".split("/")
_date = date(*map(int, _date.split("-")))

pic = int(pic)

today = ((datetime.now().date() - _date).days + pic) % 5

print((datetime.now().date()))

show_he_suan = (today - 1) % 5

tomorrow = (today + 1) % 5

if __name__ == '__main__':
    print("今天做核酸", today, "组")
    print("展示核酸截图", show_he_suan, "组")
    print("明天做核酸", tomorrow, "组")

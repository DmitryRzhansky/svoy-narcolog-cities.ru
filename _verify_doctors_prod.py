import re
import urllib.request

home = urllib.request.urlopen("https://svoy-narcolog.ru/", timeout=30).read().decode("utf-8", "replace")
vrachi = urllib.request.urlopen("https://svoy-narcolog.ru/vrachi/", timeout=30).read().decode("utf-8", "replace")

m = re.search(r'<section class="doctors"[^>]*>[\s\S]*?</section>', home)
sec = m.group(0) if m else ""
print("HOME doctors Golev", "Голев" in sec)
print("HOME doctors Kotomkin", "Котомкин" in sec)
print("HOME doctors Beskova", "Бескова" in sec)
print("HOME doctors Morozov", "Морозов" in sec)
print("HOME doctors skills", "Профессиональные навыки" in sec)
print("HOME hero", "paramonov-glavnyy-vrach.webp" in home)

start = vrachi.find("site-meta")
end = vrachi.find("</ul>", start)
print("VRACHI broken site-meta", "doctor-profile" in vrachi[start:end])
print("VRACHI Golev", "Голев Сергей" in vrachi)
print("VRACHI skills", vrachi.count("Профессиональные навыки"))
print("VRACHI services", vrachi.count("Какие услуги оказывает"))

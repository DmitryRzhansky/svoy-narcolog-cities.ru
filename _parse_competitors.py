#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse competitor SERP URLs: H1, Title, Description → competitors.md"""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUT = Path(__file__).resolve().parent / "competitors.md"
TIMEOUT = 25
MAX_WORKERS = 10
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

# Structure: service → geo → engine → [(url, position), ...]
DATA: dict[str, dict[str, dict[str, list[tuple[str, int]]]]] = {
    "Нарколог на дом": {
        "Иваново": {
            "Yandex": [
                ("https://ivanovo.nrod.ru/pomosch-na-domu/", 1),
                ("https://ivanovo.delta-clinic.ru/narkolog-na-dom/", 2),
                ("https://ivanovo.neoplus-clinic.ru/narcolog-na-dom/", 3),
                ("https://panacea.clinic/ivanovo/narkolog-na-dom/", 4),
                ("https://ivanovo.klinika-osoznanie.ru/vyzov-narkologa-na-dom/", 5),
                ("https://ivanovo.kapelnica.clinic/services/narkolog-na-dom/", 6),
                ("https://ivanovo.yuzhnyj-narkolog.ru/uslugi/narkolog-na-dom", 7),
                ("https://ivanovo.metod-dovzhenko.com/uslugi/narkologiya/vyzov-narkologa-na-dom/", 8),
            ],
            "Google": [
                ("https://narcology.clinic/regions/ivanovo/service/vyvod-iz-zapoya/narkolog-na-dom/", 1),
                ("https://ivanovo.narkology.clinic/narkologicheskaya-pomoshch/narkolog-na-dom/", 2),
                ("https://ivanovo.stop-alko.com/narkolog-na-dom/", 3),
                ("https://ivanovo.dr-kalyuzhnaya.ru/uslugi/narkologicheskaya-pomosch/na-domu/", 4),
                ("https://medcenter37.ru/medical-services/narcology", 5),
                ("https://detox24.ru/regions/ivanovo/lechenie-narkomanii/narkologicheskaya-pomosch/", 6),
                ("https://ivanovo.rehab-clinic.ru/narkolog-na-dom/", 7),
                ("https://narkolog-24.ru/services/narkolog-na-dom/ivanovo/", 8),
            ],
        },
        "Шуя": {
            "Yandex": [
                ("https://shuya.chh.ru/treatment-direction/narkolog-na-domu/", 1),
                ("https://shuya.trezvostclinica.ru/narkologicheskaya-pomosh/narkolog-na-dom/", 2),
                ("https://shuya.nrod.ru/vyezd-narkologa/", 3),
                ("https://shuya.dr-kalyuzhnaya.ru/uslugi/narkologicheskaya-pomosch/narkolog-na-dom/", 4),
                ("https://shuya.narkology.clinic/narkologicheskaya-pomoshch/", 5),
                ("https://shuya.resource.clinic/narkolog/", 6),
                ("https://shuya.kapelnica.clinic/services/narkolog-na-dom/", 7),
                ("https://shuya.neoplus-clinic.ru/narcolog-na-dom/", 8),
                ("https://shuja.med-perspectiva.ru/vyzov-narkologa-na-dom", 9),
            ],
            "Google": [
                ("https://shuya.stop-alko.com/narkolog-na-dom/", 1),
                ("https://narcology.clinic/regions/shuya/service/vyvod-iz-zapoya/narkolog-na-dom/", 2),
                ("https://sanati-clinic.ru/regions/shuya/lechenie-narkomanii/narkolog-na-dom", 3),
                ("https://narkolog.express/shuya/uslugi/vyvod-iz-zapoya/narkolog-na-domu/", 4),
                ("https://psychiatr.clinic/regions/shuya/lechenie/narkolog-na-dom/", 5),
                ("https://rc-rehab.ru/shuya/narkolog-na-dom/", 6),
                ("https://detox24.ru/regions/shuya/", 7),
                ("https://narcology.clinic/regions/shuya/service/narkologicheskaya-pomosch/", 8),
            ],
        },
        "Кинешма": {
            "Yandex": [
                ("https://kineshma.nrod.ru/pomosch-na-domu/", 1),
                ("https://kineshma.dr-kalyuzhnaya.ru/uslugi/narkologicheskaya-pomosch/narkolog-na-dom/", 2),
                ("https://kineshma.narkology.clinic/narkologicheskaya-pomoshch/", 3),
                ("https://kineshma.metod-dovzhenko.com/uslugi/narkologiya/vyzov-narkologa-na-dom/", 4),
                ("https://kineshma.narcology.center/nakologicheskaya-pomosh/vyzov-narkologa-na-dom/", 5),
                ("https://kineshma.narkology.pro/narkolog-na-dom/", 6),
                ("https://kineshma.kapelnica.clinic/services/narkolog-na-dom/", 7),
                ("https://kineshma.resource.clinic/narkolog/", 8),
                ("https://kineshma.doctor-yushkov.ru/narkolog-na-dom/", 9),
                ("https://kineshma.vozvrashchenie.com/lechenie-alkogolizma/narkolog-anonimno/", 10),
            ],
            "Google": [
                ("https://narcology.clinic/regions/kineshma/service/vyvod-iz-zapoya/narkolog-na-dom/", 1),
                ("https://kineshma.narkology.clinic/narkologicheskaya-pomoshch/narkolog-na-dom/", 2),
                ("https://sanati-clinic.ru/regions/kineshma/lechenie-narkomanii/narkolog-na-dom", 3),
                ("https://detox24.ru/regions/kineshma/vyvod-iz-zapoya/vyzov-narkologa-na-dom/", 4),
                ("https://psychiatr.clinic/regions/kineshma/lechenie/narkolog-na-dom/", 5),
                ("https://narkolog.express/kineshma/uslugi/vyvod-iz-zapoya/narkolog-na-domu/", 6),
                ("https://panacea.clinic/kineshma/narkolog-na-dom/", 7),
                ("https://kineshma.chh.ru/treatment-direction/narkolog-na-domu/", 8),
            ],
        },
        "Кохма": {
            "Yandex": [
                ("https://kokhma.resource.clinic/narkolog/", 1),
                ("https://kohma.kapelnica.clinic/services/narkolog-na-dom/", 2),
                ("https://kokhma.narkology.pro/narkolog-na-dom/", 3),
                ("https://kokhma.neoplus-clinic.ru/narcolog-na-dom/", 4),
                ("https://kokhma.dr-kalyuzhnaya.ru/uslugi/narkologicheskaya-pomosch/narkolog-na-dom/", 5),
                ("https://kokhma.zapoy.clinic/narkologicheskaya-pomosch/", 6),
                ("https://kohma.chh.ru/treatment-direction/narkolog-na-domu/", 7),
                ("https://kokhma.union.clinic/narkolog/", 8),
                ("https://kokhma.clearway.pro/narkolog-na-dom/", 9),
                ("https://kokhma.narkolog.express/uslugi/narkologicheskaya-pomosh/", 10),
            ],
            "Google": [
                ("https://kohma.stop-alko.com/narkolog-na-dom/", 1),
                ("https://narcology.clinic/regions/kokhma/service/vyvod-iz-zapoya/narkolog-na-dom/", 2),
                ("https://kohma.clinica-plus.ru/narkologicheskaya-pomoshh/narkolog-na-dom/", 3),
                ("https://narkolog.express/kokhma/uslugi/kapelnicy/", 4),
                ("https://kohma.stranaprotivnarkotikov.ru/narkolog-na-dom/", 5),
                ("https://kokhma.union.clinic/narkolog/", 6),
                ("https://detox24.ru/regions/kokhma/lechenie-alkogolizma/narkolog-dlya-nesovershennoletnih-podrostkov/", 7),
                ("https://kokhma.sanati-clinic.ru/regions/kokhma/lechenie-narkomanii/narkolog-na-dom", 8),
            ],
        },
        "Фурманов": {
            "Yandex": [
                ("https://furmanov.dr-kalyuzhnaya.ru/uslugi/narkologicheskaya-pomosch/narkolog-na-dom/", 1),
                ("https://furmanov.kapelnica.clinic/services/narkolog-na-dom/", 2),
                ("https://furmanov.chh.ru/treatment-direction/narkolog-na-domu/", 3),
                ("https://furmanov.trezvostclinica.ru/narkologicheskaya-pomosh/narkolog-na-dom/", 4),
                ("https://furmanov.narkology.pro/narkolog-na-dom/", 5),
                ("https://furmanov.narcology.center/nakologicheskaya-pomosh/vyzov-narkologa-na-dom/", 7),
                ("https://furmanov.narkology.pro/narkolog-na-dom/", 8),
                ("https://furmanov.narcology.clinic/service/vyvod-iz-zapoya/narkolog-na-dom/", 9),
                ("https://furmanov.union.clinic/narkolog/", 10),
            ],
            "Google": [
                ("https://narcology.clinic/regions/furmanov/service/vyvod-iz-zapoya/narkolog-na-dom/", 1),
                ("https://psychiatr.clinic/regions/furmanov/lechenie/narkolog-na-dom/", 2),
                ("https://sanati-clinic.ru/regions/furmanov/lechenie-narkomanii/narkolog-na-dom", 3),
                ("https://narkolog.express/furmanov/uslugi/vyvod-iz-zapoya/narkolog-na-domu/", 4),
                ("https://narcology.clinic/regions/furmanov/", 5),
                ("https://furmanov.narcolog.spb.ru/narkolog-na-dom/", 6),
            ],
        },
        "Приволжск": {
            "Yandex": [
                ("https://privolzhsk.narkology.pro/narkolog-na-dom/", 1),
                ("https://privolzhsk.dr-kalyuzhnaya.ru/uslugi/narkologicheskaya-pomosch/narkolog-na-dom/", 2),
                ("https://privolzhsk.neoplus-clinic.ru/narcolog-na-dom/", 3),
                ("https://privolzhsk.trezvostclinica.ru/narkologicheskaya-pomosh/narkolog-na-dom/", 4),
                ("https://privolzhsk.clearway.pro/narkolog-na-dom/", 5),
                ("https://privolzhsk.union.clinic/narkolog/", 6),
                ("https://privolgsk.medcentr-vosstanovlenie.ru/narkologicheskaya-pomosch/vyzov-narkologa/", 7),
                ("https://privolzhsk.narcology.clinic/service/vyvod-iz-zapoya/narkolog-na-dom/", 8),
            ],
            "Google": [
                ("https://narcology.clinic/regions/privolzhsk/service/vyvod-iz-zapoya/narkolog-na-dom/", 1),
                ("https://narkolog.express/privolzhsk/uslugi/vyvod-iz-zapoya/narkolog-na-domu/", 2),
                ("https://privolzhsk.dr-kalyuzhnaya.ru/uslugi/narkologicheskaya-pomosch/narkolog-na-dom/", 3),
                ("https://privolzhsk.rehab-clinic.ru/narkolog-na-dom/", 4),
                ("https://privolzhsk.resource.clinic/narkolog/", 5),
                ("https://privolzhsk.clinica-plus.ru/narkologicheskaya-pomoshh/narkolog-na-dom/", 6),
                ("https://psychiatr.clinic/regions/privolzhskiy/lechenie/narkolog-na-dom/", 7),
                ("https://privolzhsk.kapelnitsa.clinic/vrach-narkolog-na-dom/", 8),
            ],
        },
    },
    "Капельница от запоя": {
        "Иваново": {
            "Yandex": [
                ("https://ivanovo.clinica-plus.ru/lechenie-alkogolizma/kapelnicza-ot-zapoya/", 1),
                ("https://ivanovo.alkospas.ru/kapelnitsa-na-domu/", 2),
                ("https://ivanovo.med-perspectiva.ru/kapelnitsa-ot-zapoya-na-domu", 3),
                ("https://ivanovo.dr-kalyuzhnaya.ru/uslugi/zapoj/kapelnitsa-ot-alkogolya/", 4),
                ("https://ivanovo.metod-dovzhenko.com/uslugi/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 5),
                ("https://ivanovo.union.clinic/kapelnica/", 6),
                ("https://ivanovo.delta-clinic.ru/kapelnitsa-ot-zapoya/", 7),
                ("https://ivanovo.kapelnica.clinic/services/kapelnica-ot-alkogolya/", 8),
            ],
            "Google": [
                ("https://narcology.clinic/regions/ivanovo/service/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 1),
                ("https://ivanovo.stop-alko.com/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 2),
                ("https://ivanovo.narkology.clinic/narkologicheskaya-pomoshch/kapelnitsa-ot-zapoya/", 3),
                ("https://ivanovo.president-medical.ru/services/kapelnicza-ot-zapoya/", 4),
                ("https://ivanovo.dr-kalyuzhnaya.ru/uslugi/alkogolizm/kapelnitsa-ot-pokhmelya/", 5),
                ("https://alclinic.ru/kapelnica-ot-zapoya-ivanovo/", 6),
                ("https://ivanovo.metod-dovzhenko.com/uslugi/vyvod-iz-zapoya/kapelnitsa-ot-pohmelya-na-domu/", 7),
                ("https://detox24.ru/regions/ivanovo/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 8),
            ],
        },
        "Шуя": {
            "Yandex": [
                ("https://shuya.clinica-plus.ru/lechenie-alkogolizma/kapelnicza-ot-zapoya/", 1),
                ("https://shuya.chh.ru/treatment-direction/medczentr-kapelnicz/kapelniczyi-ot-zapoya/", 2),
                ("https://shuja.astra-klinika.ru/service/vyvod-iz-zapoya/kapelnitsa-ot-zapoya-na-domu/", 3),
                ("https://shuya.president-medical.ru/services/kapelnicza-ot-zapoya/", 4),
                ("https://shuya.narkology.pro/kapelnitsa-ot-zapoya/", 5),
                ("https://shuja.med-perspectiva.ru/vyvod-iz-zapoya", 6),
            ],
            "Google": [
                ("https://psychiatr.clinic/regions/shuya/lechenie/kapelnitsa-ot-zapoya/", 1),
                ("https://shuya.chh.ru/treatment-direction/medczentr-kapelnicz/kapelniczyi-ot-zapoya/", 2),
                ("https://detox24.ru/regions/shuya/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 3),
                ("https://narkolog.express/shuya/uslugi/kapelnicy/", 3),
                ("https://shuya.kapelnica.clinic/services/kapelnica-ot-alkogolya/", 4),
                ("https://narcology.clinic/regions/shuya/service/vyvod-iz-zapoya/", 5),
                ("https://psychiatr.clinic/regions/shuya/lechenie/vyivod-iz-zapoya/", 6),
                ("https://panacea.clinic/shuya/kapelnicza-ot-zapoya/", 7),
            ],
        },
        "Кинешма": {
            "Yandex": [
                ("https://kineshma.health-kapelnica.ru/kapelnitsa-ot-zapoya/", 1),
                ("https://kineshma.metod-dovzhenko.com/uslugi/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 2),
                ("https://kineshma.clinica-plus.ru/lechenie-alkogolizma/kapelnica/", 3),
                ("https://kineshma.clinic-life.site/kapelnitsa-ot-zapoya/", 4),
            ],
            "Google": [
                ("https://narcology.clinic/regions/kineshma/service/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 1),
                ("https://kineshma.narkology.clinic/narkologicheskaya-pomoshch/kapelnitsa-ot-zapoya/", 2),
                ("https://kineshma.stop-alko.com/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 3),
                ("https://narkolog.express/kineshma/uslugi/kapelnicy/", 4),
                ("https://detox24.ru/regions/kineshma/vyvod-iz-zapoya/prokapatsya-ot-alkogolya/", 5),
                ("https://psychiatr.clinic/regions/kineshma/lechenie/kapelnitsa-ot-zapoya/", 6),
            ],
        },
        "Кохма": {
            "Yandex": [
                ("https://kohma.kapelnica.clinic/services/kapelnica-ot-zapoya/", 1),
                ("https://kohma.chh.ru/treatment-direction/medczentr-kapelnicz/kapelniczyi-ot-zapoya/", 2),
                ("https://kokhma.triumf.center/kapelnitsa-ot-zapoya/", 3),
                ("https://kokhma.resource.clinic/kapelnica/", 4),
                ("https://kokhma.sanati-clinic.ru/lechenie-alkogolizma/kapelnitsa-ot-zapoya-na-domu", 5),
                ("https://kokhma.dr-kalyuzhnaya.ru/uslugi/zapoj/kapelnitsa/", 6),
                ("https://kokhma.lotos-clinica.ru/kapelnica-ot-alkogolizma-na-domu/", 7),
                ("https://kokhma.medelen.ru/kapelnitsa-ot-zapoya/", 8),
                ("https://kokhma.trezvostclinica.ru/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 9),
                ("https://kokhma.clinic-life.site/kapelnitsa-ot-zapoya/", 10),
            ],
            "Google": [
                ("https://kohma.clinica-plus.ru/lechenie-alkogolizma/kapelnicza-ot-zapoya/", 1),
                ("https://detox24.ru/regions/kokhma/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 2),
                ("https://psychiatr.clinic/regions/kokhma/lechenie/kapelnitsa-ot-zapoya/", 3),
                ("https://kokhma.trezvostclinica.ru/vyvod-iz-zapoya/kapelnitsa-ot-pohmelya/", 4),
                ("https://kohma.president-medical.ru/services/kapelnicza-ot-zapoya/", 5),
                ("https://rc-rehab.ru/kohma/lechenie-alkogolizma/kapelnicza-ot-alkogolya/", 6),
            ],
        },
        "Фурманов": {
            "Yandex": [
                ("https://furmanov.kapelnica.clinic/services/kapelnica-ot-zapoya/", 1),
                ("https://furmanov.chh.ru/treatment-direction/medczentr-kapelnicz/kapelniczyi-ot-zapoya/", 2),
                ("https://furmanov.metod-dovzhenko.com/uslugi/vyvod-iz-zapoya/lechenie-zapoya/", 3),
                ("https://furmanov.triumf.center/kapelnitsa-ot-zapoya/", 4),
                ("https://furmanov.narkology.pro/kapelnitsa-ot-zapoya/", 5),
                ("https://furmanov.dr-kalyuzhnaya.ru/uslugi/zapoj/kapelnitsa/", 6),
                ("https://furmanov.lotos-clinica.ru/kapelnica-ot-alkogolizma-na-domu/", 7),
            ],
            "Google": [
                ("https://furmanov.stop-alko.com/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 1),
                ("https://detox24.ru/regions/furmanov/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 2),
                ("https://psychiatr.clinic/regions/furmanov/lechenie/kapelnitsa-ot-zapoya/", 3),
                ("https://narkolog.express/furmanov/uslugi/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 4),
                ("https://narkolog.express/furmanov/uslugi/kapelnicy/", 5),
                ("https://narcology.clinic/regions/furmanov/service/kapelnitsy/", 6),
            ],
        },
        "Приволжск": {
            "Yandex": [
                ("https://privolzhsk.clinica-plus.ru/lechenie-alkogolizma/kapelnica/", 1),
                ("https://privolzhsk.health-kapelnica.ru/kapelnitsa-ot-zapoya/", 2),
                ("https://privolzhsk.trezvostclinica.ru/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 3),
                ("https://privolzhsk.dr-kalyuzhnaya.ru/uslugi/zapoj/kapelnitsa/", 4),
            ],
            "Google": [
                ("https://privolzhsk.stop-alko.com/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 1),
                ("https://detox24.ru/regions/privolzhsk/vyvod-iz-zapoya/prokapatsya-ot-alkogolya/", 2),
                ("https://privolzhsk.resource.clinic/kapelnica/", 3),
                ("https://narcology.clinic/regions/privolzhsk/service/vyvod-iz-zapoya/kapelnitsa-ot-zapoya/", 4),
                ("https://psychiatr.clinic/regions/privolzhsk/lechenie/kapelnicza-ot-poxmelya/", 5),
                ("https://privolzhsk.dr-kalyuzhnaya.ru/uslugi/zapoj/kapelnitsa-ot-alkogolya/", 6),
            ],
        },
    },
    "Вывод из запоя на дому": {
        "Иваново": {
            "Yandex": [
                ("https://ivanovo.nrod.ru/vyvod-iz-zapoya/", 1),
                ("https://ivanovo-ivanovskaya-oblast.lvc-health.ru/vyivod-iz-zapoya/", 2),
                ("https://ivanovo.garmonia-clinica.ru/uslugi/narkologiya/alkogolizm/vyvod-iz-zapoya/", 3),
                ("https://ivanovo.clinica-plus.ru/lechenie-alkogolizma/vyivod-iz-zapoya/", 4),
                ("https://ivanovo.our-health.center/vyivod-iz-zapoya/", 5),
                ("https://ivanovo.neoplus-clinic.ru/vyvod-iz-zapoya/", 6),
                ("https://ivanovo-ivanovskaya-oblast.narkolog-psihiatr.ru/vyvod-iz-zapoya/", 7),
                ("https://ivanovo.union.clinic/vivod-iz-zapoya-stacionar/", 8),
                ("https://ivanovo.yuzhnyj-narkolog.ru/uslugi/vyvod-iz-zapoya", 9),
                ("https://ivanovo.lotos-clinica.ru/vyvod-iz-zapoya/", 10),
            ],
            "Google": [
                ("https://ivanovo.stop-alko.com/vyvod-iz-zapoya/", 1),
                ("https://ivanovo.vperemen.com/alkogolizm/lechenie/vyvod-iz-zapoya-na-domu", 2),
                ("https://detox24.ru/regions/ivanovo/vyvod-iz-zapoya/", 3),
                ("https://narcology.clinic/regions/ivanovo/service/vyvod-iz-zapoya/", 4),
                ("https://ivanovo.narkology.clinic/narkologicheskaya-pomoshch/vyvod-iz-zapoya/", 5),
                ("https://razvitie-ivanovo.ru/uslugi/vyvod-iz-zapoya/", 6),
                ("https://ivanovo.psikhiatr.clinic/vyvedenie-iz-zapoya/", 7),
                ("https://ivanovo.rehab-clinic.ru/vyvedenie-iz-zapoya/anonimnyy-vyvod-iz-zapoya/", 8),
            ],
        },
        "Шуя": {
            "Yandex": [
                ("https://shuya.clinica-plus.ru/lechenie-alkogolizma/vivod-iz-zapoya-na-domu/", 1),
                ("https://shuya.dr-kalyuzhnaya.ru/uslugi/zapoj/vyvod-iz-zapoya-na-domu/", 2),
                ("https://shuya.kapelnitsa.clinic/vyvod-iz-zapoya/", 3),
                ("https://shuya.zapoy.clinic/", 4),
                ("https://shuya.kapelnica.clinic/services/vyivod-iz-zapoya/", 5),
                ("https://shuya.resource.clinic/vivod-iz-zapoya-stacionar/", 6),
                ("https://shuya.nrod.ru/vyvod-iz-zapoya/", 7),
                ("https://shuya.sanati-clinic.ru/lechenie-alkogolizma/vyvod-iz-zapoya", 8),
            ],
            "Google": [
                ("https://psychiatr.clinic/regions/shuya/lechenie/vyivod-iz-zapoya/", 1),
                ("https://detox24.ru/regions/shuya/vyvod-iz-zapoya/", 2),
                ("https://narcology.clinic/regions/shuya/service/vyvod-iz-zapoya/", 3),
                ("https://shuya.kapelnica.clinic/services/vyivod-iz-zapoya/", 4),
                ("https://narkolog37.ru/kontakty/shuya/", 5),
                ("https://rc-rehab.ru/shuya/lechenie-alkogolizma/vyvod-iz-zapoya/", 6),
            ],
        },
        "Кинешма": {
            "Yandex": [
                ("https://kineshma.kapelnica.clinic/services/vyivod-iz-zapoya/", 1),
                ("https://kineshma.clinica-plus.ru/lechenie-alkogolizma/vyivod-iz-zapoya/", 2),
                ("https://kineshma.vozvrashchenie.com/lechenie-alkogolizma/vyvod-iz-zapoja/v-statsionare/", 3),
                ("https://kineshma.kapelnitsa.clinic/vyvod-iz-zapoya/", 4),
                ("https://kineshma.union.clinic/zapoy/", 5),
                ("https://kineshma.health-kapelnica.ru/vyvod-iz-zapoya/", 6),
                ("https://kineshma.lotos-clinica.ru/vyvod-iz-zapoya/", 7),
                ("https://kineshma.med-perspectiva.ru/vyvod-iz-zapoya", 8),
                ("https://kineshma.health-clinic.ru/", 9),
                ("https://kineshma.dr-kalyuzhnaya.ru/uslugi/zapoj/vyvod-iz-zapoya-na-domu/", 10),
            ],
            "Google": [
                ("https://narcology.clinic/regions/kineshma/service/vyvod-iz-zapoya/", 1),
                ("https://kineshma.metod-dovzhenko.com/uslugi/vyvod-iz-zapoya/prinuditelnyy-vyvod-iz-zapoya/", 2),
                ("https://kineshma.narkology.clinic/statsionar-narkologii/vyvod-iz-zapoya-v-statsionare/", 3),
                ("https://detox24.ru/regions/kineshma/vyvod-iz-zapoya/", 4),
                ("https://kineshma.stop-alko.com/vyvod-iz-zapoya/prinuditelnyy-vyvod-iz-zapoya/", 5),
                ("https://kineshma.rehab-clinic.ru/vyvedenie-iz-zapoya/", 6),
                ("https://psychiatr.clinic/regions/kineshma/lechenie/vyivod-iz-zapoya/", 7),
                ("https://kineshma.neoplus-clinic.ru/vyvod-iz-zapoya/", 8),
            ],
        },
        "Кохма": {
            "Yandex": [
                ("https://kokhma.sanati-clinic.ru/lechenie-alkogolizma/vyvod-iz-zapoya", 1),
                ("https://kokhma.dr-kalyuzhnaya.ru/uslugi/zapoj/vyvod-iz-zapoya-na-domu/", 2),
                ("https://kokhma.clinic-life.site/vyvod-iz-zapoya/", 3),
                ("https://kohma.kapelnica.clinic/services/vyivod-iz-zapoya/", 4),
                ("https://kokhma.zapoy.clinic/", 5),
                ("https://kokhma.resource.clinic/zapoy/", 6),
                ("https://kokhma.narkology.pro/vyvod-iz-zapoya/", 7),
                ("https://kohma.lvc-health.ru/vyivod-iz-zapoya/", 8),
                ("https://kokhma.psychiatr.clinic/lechenie/vyivod-iz-zapoya-v-staczionare/", 9),
            ],
            "Google": [
                ("https://kohma.stop-alko.com/vyvod-iz-zapoya/", 1),
                ("https://narcology.clinic/regions/kokhma/service/vyvod-iz-zapoya/v-statsionare/", 2),
                ("https://kohma.clinica-plus.ru/lechenie-alkogolizma/kapelnicza-ot-zapoya/", 3),
                ("https://kokhma.rehab-clinic.ru/vyvedenie-iz-zapoya/", 4),
                ("https://kokhma.trezvostclinica.ru/vyvod-iz-zapoya/", 5),
                ("https://psychiatr.clinic/regions/kokhma/lechenie/vyivod-iz-zapoya/", 6),
                ("https://narcology.clinic/regions/kokhma/service/vyvod-iz-zapoya/", 7),
            ],
        },
        "Фурманов": {
            "Yandex": [
                ("https://furmanov.kapelnica.clinic/services/vyivod-iz-zapoya/", 1),
                ("https://furmanov.union.clinic/vivod-iz-zapoya-stacionar/", 2),
                ("https://furmanov.psychiatr.clinic/lechenie/vyivod-iz-zapoya/", 3),
                ("https://furmanov.dr-kalyuzhnaya.ru/uslugi/zapoj/vyvod-iz-zapoya-v-statsionare/", 4),
                ("https://furmanov.trezvostclinica.ru/vyvod-iz-zapoya/", 5),
                ("https://furmanov.zapoy.clinic/", 6),
                ("https://furmanov.vozvrashchenie.com/lechenie-alkogolizma/vyvod-iz-zapoja/", 7),
                ("https://furmanov.metod-dovzhenko.com/uslugi/vyvod-iz-zapoya/", 8),
                ("https://furmanov.premium-clinic.com/vyvod-iz-zapoya-na-domu/", 9),
                ("https://furmanov.neoplus-clinic.ru/vyvod-iz-zapoya/", 10),
            ],
            "Google": [
                ("https://furmanov.stop-alko.com/vyvod-iz-zapoya/", 1),
                ("https://psychiatr.clinic/regions/furmanov/lechenie/vyivod-iz-zapoya/", 2),
                ("https://furmanov.zapoy-clinic.ru/alkogolizm/vyvod-iz-zapoya/prinuditelnyy-vyvod", 3),
                ("https://furmanov.triumf.center/vyvod-iz-zapoya/", 4),
                ("https://narcology.clinic/regions/furmanov/service/vyvod-iz-zapoya/", 5),
            ],
        },
        "Приволжск": {
            "Yandex": [
                ("https://privolzhsk.trezvostclinica.ru/vyvod-iz-zapoya/v-statsionare/", 1),
                ("https://privolzhsk.zapoy.clinic/", 2),
                ("https://privolzhsk.union.clinic/vivod-iz-zapoya-stacionar/", 3),
                ("https://privolgsk.medcentr-vosstanovlenie.ru/vyvod-iz-zapoya/", 4),
                ("https://privolzhsk.narkology.pro/vyvod-iz-zapoya/", 5),
                ("https://privolzhsk.detox24.ru/vyvod-iz-zapoya/", 6),
                ("https://privolzhsk.neoplus-clinic.ru/vyvod-iz-zapoya/", 7),
            ],
            "Google": [
                ("https://privolzhsk.stop-alko.com/vyvod-iz-zapoya/", 1),
                ("https://narcology.clinic/regions/privolzhsk/service/vyvod-iz-zapoya/", 2),
                ("https://privolzhsk.rehab-clinic.ru/vyvedenie-iz-zapoya/", 3),
                ("https://psychiatr.clinic/regions/privolzhsk/lechenie/vyivod-iz-zapoya/", 4),
                ("https://privolzhsk.stop-alko.com/vyvod-iz-zapoya/prinuditelnyy-vyvod-iz-zapoya/", 5),
            ],
        },
    },
    "Кодирование от алкоголя": {
        "Иваново": {
            "Yandex": [
                ("https://ivanovo.union.clinic/kodirovanie/", 1),
                ("https://ivanovo.skoryjdoktor.ru/services/kodirovanie/", 2),
                ("https://ivanovo.med-perspectiva.ru/kodirovanie-alkogolizma", 3),
                ("https://ivanovo.narkology.clinic/alkogolizm/kodirovanie-ot-alkogolizma/", 4),
                ("https://ivanovo.nrod.ru/kodirovanie/", 5),
                ("https://ivanovo.alkospas.ru/kodirovanie-ot-alkogolizma/", 6),
            ],
            "Google": [
                ("https://narcology.clinic/regions/ivanovo/service/kodirovanie-ot-alkogolizma/", 1),
                ("https://ivanovo.narkology.clinic/alkogolizm/kodirovanie-ot-alkogolizma/", 2),
                ("https://ivanovo.stop-alko.com/kodirovanie-ot-alkogolizma/", 3),
                ("https://narkolog37.ru/uslugi-tseny/kodirovanie-ot-alkogolizma/index.htm", 4),
                ("https://ivanovo.vperemen.com/alkogolizm/lechenie/kodirovanie", 5),
                ("https://detox24.ru/regions/ivanovo/kodirovanie-ot-alkogolizma/kodirovanie-ot-alkogolizma-na-domu/", 6),
            ],
        },
        "Шуя": {
            "Yandex": [
                ("https://shuya.lilia.clinic/kodirovanie/", 1),
                ("https://shuya.resource.clinic/kodirovanie/", 2),
                ("https://shuya.trezvostclinica.ru/kodirovanie-ot-alkogolizma/", 3),
                ("https://shuya.nrod.ru/kodirovanie/", 4),
                ("https://shuja.med-perspectiva.ru/kodirovanie-alkogolizma", 5),
                ("https://shuya.union.clinic/kodirovanie/", 6),
                ("https://panacea.clinic/shuya/na-1-god/", 7),
                ("https://shuya.health-clinic.ru/kodirovanie-ot-alkogolizma/", 8),
                ("https://shuya.zapoy.clinic/kodirovanie-ot-alkogolizma/", 9),
            ],
            "Google": [
                ("https://narkolog.express/shuya/uslugi/kodirovanie-ot-alkogolizma/", 1),
                ("https://narcology.clinic/regions/shuya/service/kodirovanie-ot-alkogolizma/", 2),
                ("https://shuya.stop-alko.com/kodirovanie-ot-alkogolizma/", 3),
                ("https://shuya.zapoy-clinic.ru/alkogolizm/kodirovka/prinuditelno", 4),
                ("https://rc-rehab.ru/shuya/kodirovanie-ot-alkogolizma/", 5),
            ],
        },
        "Кинешма": {
            "Yandex": [
                ("https://kineshma.nrod.ru/kodirovanie/", 1),
                ("https://kineshma.health-clinic.ru/kodirovanie-ot-alkogolizma/", 2),
                ("https://kineshma.med-perspectiva.ru/kodirovanie-alkogolizma", 3),
                ("https://kineshma.narcology.center/kodirovanie-alkogolizma/", 4),
                ("https://rehab365.ru/kineshma/kodirovanie-ot-alkogolizma/", 5),
                ("https://kineshma.1narcology.ru/kodirovanie-ot-alkogolizma/", 6),
            ],
            "Google": [
                ("https://detox24.ru/regions/kineshma/kodirovanie-ot-alkogolizma/", 1),
                ("https://narcology.clinic/regions/kineshma/service/kodirovanie-ot-alkogolizma/anonimnoe-kodirovanie/", 2),
                ("https://narcology.clinic/regions/kineshma/service/kodirovanie-ot-alkogolizma/anonimnoe-kodirovanie/", 3),
                ("https://narkolog.express/kineshma/uslugi/kodirovanie-ot-alkogolizma/", 4),
                ("https://kineshma.stop-alko.com/kodirovanie-ot-alkogolizma/kodirovanie-ot-alkogolizma-na-5-let/", 5),
                ("https://panacea.clinic/kineshma/kodirovanie/", 6),
                ("https://detox24.ru/regions/kineshma/kodirovanie-ot-alkogolizma/kodirovanie-gipnozom/", 7),
                ("https://kineshma.narkology.clinic/alkogolizm/kodirovanie-ot-alkogolizma/", 8),
                ("https://kineshma.metod-dovzhenko.com/uslugi/kodirovanie/", 9),
            ],
        },
        "Кохма": {
            "Yandex": [
                ("https://kokhma.resource.clinic/kodirovanie/", 1),
                ("https://kokhma.trezvostclinica.ru/kodirovanie-ot-alkogolizma/", 2),
                ("https://kokhma.clearway.pro/kodirovanie/", 3),
                ("https://kokhma.alco.rehab/kodirovanie-ot-alkogolizma/", 4),
                ("https://kokhma.private-narcology.ru/kodirovanie-ot-alkogolizma/", 5),
            ],
            "Google": [
                ("https://narcology.clinic/regions/kokhma/service/kodirovanie-ot-alkogolizma/", 1),
                ("https://kokhma.trezvostclinica.ru/kodirovanie-ot-alkogolizma/", 2),
                ("https://kokhma.rehab-clinic.ru/kodirovanie-ot-alkogolizma/", 3),
                ("https://kohma.stop-alko.com/kodirovanie-ot-alkogolizma/kodirovanie-ot-alkogolizma-na-5-let/", 4),
                ("https://kohma.clinica-plus.ru/lechenie-alkogolizma/kodirovanie-na-3-mesyaca/", 5),
                ("https://narkolog.express/kokhma/uslugi/kodirovanie-ot-alkogolizma/kodirovanie-ot-alkogolizma-s-provokatsiey/", 6),
                ("https://narcology.clinic/regions/kokhma/service/kodirovanie-ot-alkogolizma/kodirovanie-na-1-god/", 7),
                ("https://kohma.stranaprotivnarkotikov.ru/kodirovanie-alkogolizma/", 8),
            ],
        },
        "Фурманов": {
            "Yandex": [
                ("https://furmanov.sanati-clinic.ru/kodirovanie-ot-alkogolizma", 1),
                ("https://furmanov.narcology.clinic/service/kodirovanie-ot-alkogolizma/", 2),
                ("https://furmanov.zapoy.clinic/kodirovanie-ot-alkogolizma/", 3),
                ("https://furmanov.clinica-plus.ru/lechenie-alkogolizma/kodirovanie/", 4),
                ("https://furmanov.lilia.clinic/kodirovanie/", 5),
            ],
            "Google": [
                ("https://narcology.clinic/regions/furmanov/service/kodirovanie-ot-alkogolizma/", 1),
                ("https://furmanov.stop-alko.com/kodirovanie-ot-alkogolizma/", 2),
                ("https://doctor-narcology.ru/regions/furmanov/kodirovanie/", 3),
                ("https://sanati-clinic.ru/regions/furmanov/kodirovanie-ot-alkogolizma", 4),
                ("https://furmanov.trezvostclinica.ru/kodirovanie-ot-alkogolizma/na-3-goda/", 5),
                ("https://narkolog.express/furmanov/uslugi/kodirovanie-ot-alkogolizma/vnutrivennoe-kodirovanie/", 6),
                ("https://detox24.ru/regions/furmanov/kodirovanie-ot-alkogolizma/kodirovanie-ot-alkogolizma-na-domu/", 7),
            ],
        },
        "Приволжск": {
            "Yandex": [
                ("https://privolzhsk.trezvostclinica.ru/kodirovanie-ot-alkogolizma/", 1),
                ("https://privolgsk.medcentr-vosstanovlenie.ru/kodirovanie-ot-alkogolizma/", 2),
            ],
            "Google": [
                ("https://narcology.clinic/regions/privolzhsk/service/kodirovanie-ot-alkogolizma/", 1),
                ("https://privolzhsk.stop-alko.com/kodirovanie-ot-alkogolizma/", 2),
                ("https://privolzhsk.rehab-clinic.ru/kodirovanie-ukolom/", 3),
                ("https://detox24.ru/regions/privolzhsk/kodirovanie-ot-alkogolizma/trojnoe/", 4),
                ("https://privolzhsk.mk-narkolog-centr.ru/anonimnoe-kodirovanie/", 5),
                ("https://privolzhsk.stop-alko.com/kodirovanie-ot-alkogolizma/kodirovanie-ot-alkogolizma-na-5-let/", 6),
                ("https://privolzhsk.resource.clinic/vitamerc-depo/", 7),
            ],
        },
    },
}


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    text = unescape(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url


def extract_meta(soup: BeautifulSoup, names: list[str]) -> str:
    for name in names:
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return clean_text(tag["content"])
        tag = soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"):
            return clean_text(tag["content"])
    return ""


def parse_page(html: str) -> tuple[str, str, str]:
    soup = BeautifulSoup(html, "lxml")

    title = ""
    if soup.title and soup.title.string:
        title = clean_text(soup.title.string)
    if not title:
        title = extract_meta(soup, ["og:title", "twitter:title"])

    description = extract_meta(
        soup,
        ["description", "og:description", "twitter:description"],
    )

    h1 = ""
    h1_tag = soup.find("h1")
    if h1_tag:
        h1 = clean_text(h1_tag.get_text(" ", strip=True))

    return h1, title, description


def fetch_one(url: str) -> dict:
    url = normalize_url(url)
    result = {
        "url": url,
        "h1": "",
        "title": "",
        "description": "",
        "status": "ok",
        "error": "",
        "final_url": url,
    }
    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,
            verify=False,
        )
        result["final_url"] = resp.url
        if resp.status_code >= 400:
            result["status"] = f"http_{resp.status_code}"
            result["error"] = f"HTTP {resp.status_code}"
        ctype = resp.headers.get("Content-Type", "")
        if "html" not in ctype.lower() and not resp.text[:200].lower().lstrip().startswith(("<!", "<html")):
            if result["status"] == "ok":
                result["status"] = "non_html"
        h1, title, description = parse_page(resp.text)
        result["h1"] = h1
        result["title"] = title
        result["description"] = description
        # bot-check / captcha pages
        bot_markers = (
            "ваш браузер не смог пройти проверку",
            "checking your browser",
            "attention required",
            "just a moment",
            "cf-browser-verification",
        )
        blob = f"{h1} {title} {description}".lower()
        if any(m in blob for m in bot_markers):
            result["status"] = "bot_check"
            result["error"] = "bot protection / captcha"
            result["h1"] = ""
            result["title"] = ""
            result["description"] = ""
        elif not h1 and not title and result["status"] == "ok":
            result["status"] = "empty"
        elif title and result["status"].startswith("http_"):
            # got meta despite error code
            pass
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "timeout"
    except requests.exceptions.SSLError as exc:
        result["status"] = "ssl_error"
        result["error"] = str(exc)[:200]
    except requests.exceptions.RequestException as exc:
        result["status"] = "error"
        result["error"] = str(exc)[:200]
    except Exception as exc:  # noqa: BLE001
        result["status"] = "error"
        result["error"] = str(exc)[:200]
    return result


def collect_unique_urls() -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for service in DATA.values():
        for geo in service.values():
            for engine in geo.values():
                for url, _pos in engine:
                    nu = normalize_url(url)
                    if nu not in seen:
                        seen.add(nu)
                        urls.append(nu)
    return urls


def fetch_all(urls: list[str]) -> dict[str, dict]:
    cache: dict[str, dict] = {}
    total = len(urls)
    done = 0
    print(f"Fetching {total} unique URLs with {MAX_WORKERS} workers...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_one, u): u for u in urls}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                cache[url] = fut.result()
            except Exception as exc:  # noqa: BLE001
                cache[url] = {
                    "url": url,
                    "h1": "",
                    "title": "",
                    "description": "",
                    "status": "error",
                    "error": str(exc)[:200],
                    "final_url": url,
                }
            done += 1
            if done % 20 == 0 or done == total:
                ok = sum(1 for v in cache.values() if v.get("status") == "ok")
                print(f"  {done}/{total} done (ok={ok})")
    return cache


def md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def build_markdown(cache: dict[str, dict]) -> str:
    lines: list[str] = []
    lines.append("# Конкуренты SERP — парсинг H1 / Title / Description")
    lines.append("")
    lines.append(f"Дата парсинга: {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("Структура: услуга / гео / поисковик (Yandex | Google) / позиция.")
    lines.append("")
    lines.append("Для каждой позиции: **H1**, **Title**, **Description**, **URL**.")
    lines.append("")

    for service, geos in DATA.items():
        lines.append(f"## Услуга: {service}")
        lines.append("")
        for geo, engines in geos.items():
            lines.append(f"### Гео: {geo}")
            lines.append("")
            for engine in ("Yandex", "Google"):
                items = engines.get(engine, [])
                lines.append(f"#### {service} — {geo}, {engine}")
                lines.append("")
                if not items:
                    lines.append("_Нет данных_")
                    lines.append("")
                    continue
                for url, pos in items:
                    nu = normalize_url(url)
                    meta = cache.get(nu) or fetch_one(nu)
                    status = meta.get("status", "")
                    h1 = md_escape(meta.get("h1") or "—")
                    title = md_escape(meta.get("title") or "—")
                    desc = md_escape(meta.get("description") or "—")
                    lines.append(f"**Позиция: {pos}**")
                    lines.append("")
                    lines.append(f"- **URL:** {nu}")
                    lines.append(f"- **H1:** {h1}")
                    lines.append(f"- **Title:** {title}")
                    lines.append(f"- **Description:** {desc}")
                    if status != "ok":
                        err = meta.get("error") or status
                        lines.append(f"- **Status:** {status} ({err})")
                    lines.append("")
                lines.append("---")
                lines.append("")
    return "\n".join(lines)


def main() -> None:
    urls = collect_unique_urls()
    print(f"Unique URLs: {len(urls)}")
    cache = fetch_all(urls)

    # retry failures up to 2 times with pause
    for attempt in range(1, 3):
        failed = [
            u
            for u, v in cache.items()
            if v.get("status") not in ("ok",) or not (v.get("title") or v.get("h1"))
        ]
        if not failed:
            break
        print(f"Retry {attempt}: {len(failed)} URLs...")
        time.sleep(2)
        for u in failed:
            time.sleep(0.15)
            cache[u] = fetch_one(u)

    md = build_markdown(cache)
    OUT.write_text(md, encoding="utf-8")
    ok = sum(1 for v in cache.values() if v.get("status") == "ok" and v.get("title"))
    print(f"Saved: {OUT}")
    print(f"Success with title: {ok}/{len(cache)}")


if __name__ == "__main__":
    main()

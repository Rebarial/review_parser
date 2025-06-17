from twogis_parser.tools.parser import create_2gis_reviews
from yandex_parser.tools.parser import create_yandex_reviews
from vl_parser.tools.parser import create_vlru_reviews

def parse_all_providers(branch):
        try:
            if branch.twogis_map_url:
                create_2gis_reviews(url=branch.twogis_map_url, inn=branch.organization.inn, address=branch.address)
        except Exception:
            print(Exception)
        try:
            if branch.vlru_url:
                create_vlru_reviews(branch.vlru_url, branch.organization.inn, address=branch.address)
        except Exception:
            print(Exception)
        try:
            if branch.yandex_map_url:
                create_yandex_reviews(url=branch.yandex_map_url, inn=branch.organization.inn, address=branch.address)
        except Exception:
            print(Exception)
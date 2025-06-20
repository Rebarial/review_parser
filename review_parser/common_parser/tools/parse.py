from twogis_parser.tools.parser import create_2gis_reviews
from yandex_parser.tools.parser import create_yandex_reviews
from vl_parser.tools.parser import create_vlru_reviews
from google_parser.tools.parser import create_google_reviews

def parse_all_providers(branch):
        success_count = 0
        try_count = 0
        dict_results = {
        }
        try:
            if branch.twogis_map_url:
                try_count += 1
                dict_results['2gis'] = create_2gis_reviews(url=branch.twogis_map_url, inn=branch.organization.inn, address=branch.address)
                success_count += 1
        except Exception:
            print(Exception)
        try:
            if branch.vlru_url:
                try_count += 1
                dict_results['vlru'] = create_vlru_reviews(branch.vlru_url, branch.organization.inn, address=branch.address)
                success_count += 1
        except Exception:
            print(Exception)
        try:
            if branch.yandex_map_url:
                try_count += 1
                dict_results['yandex'] = create_yandex_reviews(url=branch.yandex_map_url, inn=branch.organization.inn, address=branch.address)
                success_count += 1
        except Exception:
            print(Exception)
        try:
            if branch.google_map_url:
                try_count += 1
                dict_results['google'] = create_google_reviews(url=branch.google_map_url, inn=branch.organization.inn, address=branch.address)
                success_count += 1
        except Exception:
            print(Exception)

        dict_results['tryes'] = try_count
        dict_results['success'] = success_count
        return dict_results
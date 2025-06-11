from review_parser.twogis_parser.tools.to_reviews import convert_2gis_reviews_to_model
from review_parser.twogis_parser.tools.parser import parse
from review_parser.common_parser.models import Branch
convert_2gis_reviews_to_model(Branch.objects.get(),parse('https://public-api.reviews.2gis.com/2.0/branches/70000001080371174/reviews?limit=50&is_advertiser=true&fields=meta.branch_rating,meta.branch_reviews_count,meta.total_count&without_my_first_review=false&rated=true&sort_by=date_edited&key=37c04fe6-a560-4549-b459-02309cf643ad&locale=ru_RU'))
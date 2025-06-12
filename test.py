@api_view(['GET'])
def reviews_by_branch(request):
    """
    API endpoint to retrieve aggregated ratings and individual reviews by branch ID and providers.

    Parameters:
    request.GET['branch_id']: The ID of the branch.
    Optional filters in request.GET as JSON string: List of dictionaries with structure {'provider': str, 'count': int}
      where 'provider' is one of ['yandex', 'google', '2gis', 'vlru'], and 'count' specifies number of reviews per provider.

    Returns:
    A JSON response containing two parts:
    - 'Common': Aggregated average ratings grouped by provider.
    - 'Reviews': Individual reviews filtered according to provided parameters.
    """
    try:
        branch_id = request.GET.get('branch_id')
        if not branch_id:
            raise ValueError("Branch ID must be specified.")
        
        branch = Branch.objects.get(id=branch_id)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    filter_criteria = []
    raw_filters = request.GET.get('filters') or '[]'
    try:
        filter_criteria = json.loads(raw_filters)
    except Exception as e:
        return JsonResponse({'error': 'Invalid format for filters.'}, status=400)

    # Fetch all reviews associated with this branch
    all_reviews = list(branch.reviews.all())

    # Prepare output data structures
    common_data = {}
    reviews_data = []

    # Grouped aggregation of average ratings per provider
    for provider_choice, _ in Review.PROVIDER_CHOICES:
        relevant_reviews = [review for review in all_reviews if review.provider == provider_choice]
        total_rating = sum(review.rating for review in relevant_reviews)
        num_reviews = len(relevant_reviews)
        avg_rating = round(total_rating / num_reviews, 2) if num_reviews > 0 else None
        common_data[provider_choice] = {
            'rating': num_reviews,
            'avg': avg_rating
        }

    # Filter reviews based on provided criteria
    for criterion in filter_criteria:
        provider = criterion.get('provider')
        limit = criterion.get('count')
        if provider and limit:
            matching_reviews = sorted([rev for rev in all_reviews if rev.provider == provider], key=lambda x: x.published_date, reverse=True)[:limit]
            reviews_data.extend(matching_reviews)

    # Convert reviews into a serializable format
    serialized_reviews = [{
        'author': review.author,
        'avatar': review.avatar,
        'video': review.video,
        'photos': review.photos.split(','),
        'published_date': review.published_date.isoformat(),
        'rating': review.rating,
        'content': review.content,
        'provider': review.provider
    } for review in reviews_data]

    # Final result formatting
    result = {
        'Common': common_data,
        'Reviews': serialized_reviews
    }

    return JsonResponse(result)


class ProviderSerializer(serializers.Serializer):
    provider = serializers.CharField()
    count = serializers.IntegerField()
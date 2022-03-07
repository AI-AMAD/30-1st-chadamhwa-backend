from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, Avg, Count


from drinks.models import Drink


class ProductsView(View):
    def get(self, request):

        drinks = Drink.objects.all()

        q = Q()

        category    = request.GET.getlist("category", None)  
        is_caffeinated   = request.GET.get("is_caffeinated", None)
        price_upper = request.GET.get("price_upper", 200000) 
        price_lower = request.GET.get("price_lower", 0) 
    
        if category:
            categories = category[0].split(',')
            q.add(Q(category__name__in = categories), Q.AND) 

        if is_caffeinated:
            q.add(Q(caffeine__gt=0), Q.AND) if is_caffeinated=="True" else q.add(Q(caffeine__exact=0), Q.AND) 

        q.add(Q(price__range = (price_lower, price_upper)),Q.AND)

        filtered_drinks = drinks.filter(q) 

        filtered_drinks_with_annotation = filtered_drinks.annotate(average_rating = Avg('review__rating'), review_count=Count('review'))

        sort_by = request.GET.get('sort_by', None)
        
        sort_by_options = {
            "newest" : "-updated_at",
            "oldest"  : "updated_at",
            "highest_rating" : "-average_rating",
        }

        result = [{
            "name"           : drink.name,
            "price"          : drink.price,
            "average_rating" : drink.average_rating if drink.average_rating else 0,
            "review_count" : drink.review_count,
            "image" : drink.image.image_url
        }for drink in filtered_drinks_with_annotation.order_by(sort_by_options[sort_by])]

        return JsonResponse({'result':result}, status = 200)





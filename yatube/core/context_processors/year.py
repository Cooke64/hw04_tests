from datetime import date


def year(request):
    d = date.today()
    current_year = d.year
    return {
        'year': current_year
    }

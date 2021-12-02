import json
# from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Media, Character, Update


def index(request):
    year_str = request.GET.get('y')
    month_str = request.GET.get('m')
    day_str = request.GET.get('d')

    if year_str or month_str or day_str:
        birthday_str = f'{year_str}年 ' if year_str else ''
        birthday_str += f'{month_str}月 ' if month_str else ''
        birthday_str += f'{day_str}日 ' if day_str else ''

        # 年 /    /
        if year_str and (not month_str) and (not day_str):
            characters = Character.objects.filter(birthday_date__year=year_str)
        # 年 / 月 /
        elif year_str and month_str and (not day_str):
            characters = Character.objects.filter(birthday_date__year=year_str, birthday_date__month=month_str)
        # 年 / 月 / 日
        elif year_str and month_str and day_str:
            characters = Character.objects.filter(birthday_date__year=year_str, birthday_date__month=month_str, birthday_date__day=day_str)
        #    / 月 / 日
        elif (not year_str) and month_str and day_str:
            characters = Character.objects.filter(birthday_date__month=month_str, birthday_date__day=day_str)
        #    / 月 /
        elif (not year_str) and month_str and (not day_str):
            characters = Character.objects.filter(birthday_date__month=month_str)
        #    /    / 日
        elif (not year_str) and (not month_str) and day_str:
            characters = Character.objects.filter(birthday_date__day=day_str)
        characters = characters.order_by('birthday_date__month', 'birthday_date__day')
        characters = characters_to_json(characters)

        context = {'birthday_str': birthday_str, 'characters': characters}
        return render(request, 'birthday/list.html', context)

    else:
        # 各月份的角色數量
        birthday_month = [m for m in
                          Character.objects.annotate(month=ExtractMonth('birthday_date'))
                          .order_by()
                          .values('month')
                          .annotate(total=Count('*'))
                          .values('month', 'total')
                          ]
        # 找尋最多角色的作品前 10 名
        media_list = [m for m in
                      Character.objects.all()
                      .values('media__id', 'media__name', 'media__country')
                      .annotate(total=Count('media'))
                      .order_by('-total')[:10]
                      ]
        media_count = Media.objects.all().count
        context = {'birthday_month': json.dumps(birthday_month), 'media': json.dumps(media_list), 'media_count': media_count}
        return render(request, 'birthday/index.html', context)


def media(request):
    media_id = request.GET.get('id', '')
    if media_id == '':
        return redirect('index')
    if not Media.objects.filter(id=media_id).exists():
        return HttpResponse("沒有找到此作品")

    media = Media.objects.get(id=media_id)
    # characters = Character.objects.filter(media=media).order_by('birthday_date')
    characters = Character.objects.filter(media=media).order_by('birthday_date__month', 'birthday_date__day')
    characters = characters_to_json(characters)

    context = {'media': media, 'characters': characters}
    return render(request, 'birthday/media.html', context)


def media_list(request, page):
    media = Media.objects.all().order_by('id')
    paginator = Paginator(media, 20)
    # 避免頁數大於總頁數
    if page > paginator.num_pages:
        page = paginator.num_pages
    page_range = paginator.get_elided_page_range(page)
    media_ = paginator.get_page(page)

    page_range_ = []
    for i in page_range:
        page_obj = {'name': '...', 'url': ''}
        if i != '…':
            page_obj['name'] = i
            page_obj['url'] = reverse('media_list', args=[i])
        page_range_.append(page_obj)

    page_info = {
        'page': page,
        'count': paginator.count,   # 資料總筆數
        'num_pages': paginator.num_pages,  # 總頁數
        'page_range': page_range_,  # 各頁數列表(名稱和網址)
    }

    media_list = []
    for medium in media_:
        media_list.append({
            'id': medium.id,
            'name': medium.name,
            'country': medium.country,
            'count': medium.character_set.all().count()
        })

    # print(page_info)
    context = {'media': json.dumps(media_list), 'page_info': json.dumps(page_info)}
    return render(request, 'birthday/media_list.html', context)


def updates(request, page):
    updates = Update.objects.all().order_by('-date')
    paginator = Paginator(updates, 20)
    # 避免頁數大於總頁數
    if page > paginator.num_pages:
        page = paginator.num_pages
    page_range = paginator.get_elided_page_range(page)
    update_ = paginator.get_page(page)

    page_range_ = []
    for i in page_range:
        page_obj = {'name': '...', 'url': ''}
        if i != '…':
            page_obj['name'] = i
            page_obj['url'] = reverse('updates', args=[i])
        page_range_.append(page_obj)

    page_info = {
        'page': page,
        'count': paginator.count,   # 資料總筆數
        'num_pages': paginator.num_pages,  # 總頁數
        'page_range': page_range_,  # 各頁數列表(名稱和網址)
    }

    update_list = []
    for update in update_:
        if update.media:
            media_id = update.media.id
            media_name = update.media.name
        else:
            media_id = None
            media_name = None

        update_list.append({
            'type': update.type,
            'date': update.date.strftime("%Y/%m/%d %H:%M"),
            'text': update.text,
            'media_id': media_id,
            'media_name': media_name,
            'character': update.character,
        })
    # print(page_info)
    context = {'updates': json.dumps(update_list), 'page_info': json.dumps(page_info)}
    return render(request, 'birthday/updates.html', context)


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    character_list = []
    message = ''
    # 關鍵字需大於兩個字
    if keyword and len(keyword) >= 2:
        characters = Character.objects.filter(name__icontains=keyword)
        # characters = Character.objects.filter(name__icontains=keyword).order_by('birthday_date__month', 'birthday_date__day')
        character_list.extend(characters)

        # 限制最大數量，避免造成伺服器負擔
        if len(character_list) < 50:
            media_list = Media.objects.filter(name__icontains=keyword)
            for media in media_list:
                characters = media.character_set.all()
                # characters = media.character_set.all().order_by('birthday_date__month', 'birthday_date__day')
                character_list.extend(characters)
                # 限制最大數量，避免造成伺服器負擔
                if len(character_list) > 50:
                    break

        character_list = character_list[:50]
        character_list = characters_to_json(character_list)
    else:
        message = '請輸入關鍵字或關鍵字需大於兩個字'

    context = {'characters': character_list, 'message': message}
    return render(request, 'birthday/search.html', context)


def test(request):
    data_list = [
        {'name': 'AAA'},
        {'name': 'BBB'},
        {'name': 'CCC'},
        {'name': 'DDD'},
        {'name': 'EEE'},
        {'name': 'FFF'},
        {'name': 'GGG'},
        {'name': 'HHH'},
    ]
    context = {'data_list': json.dumps(data_list)}
    return render(request, 'birthday/test.html', context)


def characters_to_json(characters):
    characters_list = []
    for character in characters:
        character_dict = model_to_dict(character)
        character_dict['birthday_date'] = character_dict['birthday_date'].strftime("%m/%d")
        character_dict['media'] = {
            'id': character.media.id,
            'name': character.media.name,
            'url': f"{reverse('media')}?id={character.media.id}",
        }
        characters_list.append(character_dict)
    return json.dumps(characters_list)

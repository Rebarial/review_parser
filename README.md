# Проект для парсинга отзывов
ссылка на проект: http://185.104.113.137:8000/swagger
http://185.104.113.137:8000/admin

## Добавление новой организации:

1.	Заходим в админку -> организации
2.	Добавляем данные, создаем ветку
 ![image](https://github.com/user-attachments/assets/08bafca2-e0c0-4ff3-b360-02fbba959e8f)

3.	Заполняем данные ветки.
 ![image](https://github.com/user-attachments/assets/d274454b-b7e2-43ce-92e4-1ccf0ba6618d)

Ссылка на яндекс должна быть полной, чтоб при переходе по ней открывалось аналогичное окно.
![image](https://github.com/user-attachments/assets/7ea7db1f-b500-483e-a98d-55b531bf7b7c)

 
Ссылки на 2gis и vlru должны быть аналогичными следующим:
https://2gis.ru/vladivostok/firm/70000001062587396
https://www.vl.ru/art-mesh

так же нужно из страницы vl.ru вытащить company_id и вставить в поле Vlru org id
 ![image](https://github.com/user-attachments/assets/cbd06857-e30b-42f2-945c-0701383c74c4)

4.	При сохранении новой ветки так же включается парсинг, поэтому страница может зависнуть на минут 5.

После парсинга ветки заполняются успешно взятыми данными и создаются отзывы:
 ![image](https://github.com/user-attachments/assets/be605876-527f-4364-87f1-496cffee688e)

## Получение отзывов

5.	Для получения отзывов по ip создаем объект branch ip mapping:
 ![image](https://github.com/user-attachments/assets/d09da0e5-80f2-4b2c-a767-56bc6ba69c97)

6.	Документация по получению данных через api:
http://185.104.113.137:8000/swagger/

В branch – Средние оценки и количество отзывов с провайдеров. Если оценку не получилось определить она будет -1
В provider_reviews_count – количество отзывов по провайдером в БД
В reviews – сами отзывы. Photos – ссылки на картинки через запятую.

## Фильтры и параметры в запросе на получения отзывов

Параметр "only_providers": True отвечает за то, что в результате будут только провайдеры из массива providers.

Фильтры пишутся в параметре "filters" элемента параметра "providers":

{

  "provider": "2gis",
  
  "count": 0,
  
  "filters": "avatar__isnull=false&rating__gt=4"
  
}

Примеры фильтров (фильтр в запросе → какой результат будет). Фильтры можно соединять конструкцией И через "&" между ними

    - author=test
    
    - author!=test
    
    - rating__gt=4 → rating > 4
    
    - rating__lt=5 → rating < 5
    
    - author__icontains=test → test in author
    
    - !author__icontains=test → not test in author
    
    - rating__in=1,2,3 → rating in 1,2,3
    
    - !rating__in=1,2,3 → not rating in 1,2,3
    
    - avatar__isnull=true → avatar = null
    
    - avatar__isnull=false → avatar != null

## Ручной парсинг

Если при создании был неудачный парсинг или понадобилось запарсить вручную. Можно зайти в ветку и нажать на кнопки парсинга:

![image](https://github.com/user-attachments/assets/5ca2a34d-4d89-48a2-a3f2-7cc2c592c237)

![image](https://github.com/user-attachments/assets/eae6e6a4-3cc9-43aa-8852-a84023af8a39)



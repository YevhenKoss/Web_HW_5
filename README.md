Файл main.py запускає скрипт, що дозволяє отримати інформацію про курси валют ПриватБанку.
Запускати скрипт
    
    python main.py Х

де Х - чило від 0 до 10, що вказує кількість днів за які видається інформація про курси валют.


Файл ws_chat_server.py чат на веб-сокетах з можливістю введення команди, що показує користувачам поточний курс валют у текстовому форматі.
Команда для виведення курсу вілют:

    exc USD 2

де exc - ключова фраза команди;

USD - код валюти, відповідно до https://api.privatbank.ua/#p24/exchangeArchive;

2 - чило від 0 до 10, що вказує кількість днів за які видається інформація про курси валют.

У разі введення команди у форматі exc USD - курс обраної валюти буде показано на поточний день.
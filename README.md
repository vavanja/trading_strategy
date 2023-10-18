# trading_strategy
#How to run:

1)git clone https://github.com/vavanja/trading_strategy.git
2)python -m venv venv
3)venv/Script/active
4)pip install -r requirements.txt
5)Create file .env and set telegram bot token: BOT_TOKEN='your token'
6) run file bot.py

Realization:
1. Розраховуємо ордери відносно першої точки входу
2. Створюю ордери із інформацією
3. Потім по кожній годині із файлі .csv звіряємо поточну ціну бітоїна із нашими ордерами якщо ціна близько до ціни ордера - купляємо і виставляєм ордер на продаж по ціні 5% прибутку.
4. Із кожною провіркою рахуєм максимальну просадку і суму капітала погодинно.
5. Далі інформуємо юзера через телеграм бота коли потрібно відкрити\закрити ордер.
6. Коли часовий проміжок закінчується підраховуємо дані і виводиму юзеру в тг + розраховуєм зміну бюджету за цей період у вигляду графіку.

#Link на першу частину задачі:
  https://drive.google.com/file/d/1oNHpMPFCkG4432QptCF66xTFBSPK-IMG/view?usp=sharing

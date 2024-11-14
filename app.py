from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

# URL и заголовки
url_update_subscription = "https://dolphin-anty-api.com/admin/subscription"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_days', methods=['POST'])
def add_days():
    # Получаем данные из формы
    users_emails = request.form.get('emails').split(',')
    api_token = request.form.get('api_token')
    days_to_add = int(request.form.get('days_to_add'))
    payment_amount = int(request.form.get('payment_amount', 0))
    payment_currency = request.form.get('payment_currency', 'RUB')
    reason_option = request.form.get('reason_option', 'cryptoPayment')
    additional_comments = request.form.get('additional_comments', '')

    # Настраиваем заголовки с API токеном
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    results = []
    
    # Цикл по каждому email
    for email in users_emails:
        url_get_user = f"https://dolphin-anty-api.com/admin/users?query={email.strip()}"
        response = requests.get(url_get_user, headers=headers)

        if response.status_code != 200:
            results.append(f"Ошибка при попытке найти аккаунт {email}: {response.status_code} - {response.text}")
            continue

        user_data = response.json()
        user_info = user_data.get('data', [])

        if not user_info:
            results.append(f"Аккаунт не найден {email}")
            continue

        user = user_info[0]
        team_id = user.get("teamId")
        
        if not team_id:
            results.append(f"Ошибка начисления дней для {email}: teamId отсутствует")
            continue

        # Подготовка данных для запроса
        payload = {
            "teamId": team_id,
            "plan": user.get("plan", ""),
            "usersLimit": user.get("usersLimit", 0),
            "browserProfilesLimit": user.get("browserProfilesLimit", 0),
            "subscriptionExpiration": user.get("subscriptionExpiration", ""),
            "daysToAdd": days_to_add,
            "paymentAmount": payment_amount,
            "paymentCurrency": payment_currency,
            "reasonOptions": [reason_option],
            "additionalComments": additional_comments,
        }

        response = requests.patch(url_update_subscription, headers=headers, json=payload)

        if response.status_code == 200:
            results.append(f"Успешно начислены дни для {email}")
        else:
            results.append(f"Ошибка начисления дней для {email}: {response.status_code} - {response.text}")

        time.sleep(5)

    return jsonify(results=results)

if __name__ == '__main__':
    app.run(debug=True)

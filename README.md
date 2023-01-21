# exchangeBTC
Web Application Exchange based on Django and MongoDB

## Project Requests:

- The web platform must provide an endpoint to manage user registration and access.
- Assigns each registered user a variable amount between 1 and 10 bitcoins.
- Each user can publish one or more orders to sell or buy a certain amount of bitcoins at a certain price. If the buy price of the order is equal to or higher than the sell price of any other user, record the transaction and mark both orders as executed.
- Create an endpoint to get all active buy and sell orders and another one to calculate the total profit or loss from each user's trades.
    
## Deployment

To deploy this project:
- Create a Virtual Environment
- Use the folder mongoDB
- Clone the repo and install requirements in ecoHotel/requirements.txt
- Install and run the MongoDB server: You could follow this guide for Windows: https://www.html.it/pag/52332/installazione-2/ or macOs guide: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/
- Use the folder "exchange":

```bash
  cd exchange
```
- Make database migrations
```bash
  python manage.py makemigrations
```
```bash
  python manage.py migrate
```
- Run 
```bash
  python manage.py runserver
```
- Create a super user:

```bash
  python manage.py createsuperuser
```
- Open http://127.0.0.1:8000/ in your browser
- Trade (to the moon) you BTC! (It's free and safety)

## 🛠 Skills
Django, MongoDB, Python, HTML, CSS


## 🔗 Links
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/foschimatteo/)

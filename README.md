# Vijaypaul Milk & Cooldrinks — Full-Stack Website

A modern, responsive full-stack e-commerce website developed for **Vijaypaul Milk & Cooldrinks**. The website provides customers with a convenient way to explore products, add items to their cart, place orders, and track their purchases. It also includes a separate admin dashboard for managing products, inventory, customers, and orders.

## 🌟 Website Features

### 🛍️ Customer Storefront
- Modern and responsive design for desktop, tablet, and mobile devices.
- Attractive homepage with custom branding and product showcase sections.
- Product browsing with category filtering and search functionality.
- Product images, descriptions, prices, and availability.
- Shopping cart with quantity management.
- Easy checkout and order placement.
- Customer registration and login.
- Customer profile and order history.
- Saved delivery addresses.
- Order tracking and delivery status updates.

### 🥛 Product Categories
- **Milk & Dairy:** Milk, curd, paneer, cream, cheese, and mushrooms.
- **Ice Creams:** Cups, chocobars, cones, and family packs.
- **Cool Drinks:** Sprite, Thums Up, Maaza, Coca-Cola, Fanta, and other beverages.
- **Biscuits & Snacks:** Good Day, Marie Gold, 50-50, Bourbon, Parle-G, and assorted snacks.
- **Traditional Snacks:** Chakralu, Palli Vunda, Sunnuvunda, Boondhi, Mixture, and more.
- **Ready-to-Eat:** Ready-made chapathi and poori packets.
- **Chocolates:** Dairy Milk, KitKat, and other chocolate varieties.

### 💳 Cart, Payments & Orders
- Add, remove, and update products in the shopping cart.
- Checkout with customer and delivery details.
- Cash on Delivery (COD).
- UPI payment option and UPI-on-delivery reference capture.
- Manual payment-reference verification.
- Free-delivery messaging.
- Delivery OTP verification.
- Order status updates and tracking.
- PDF invoice generation and download.
- Buy Again functionality.
- Customer return requests with admin review.

### 👨‍💼 Admin Dashboard
- Separate admin login and dashboard.
- View customer and order information.
- Add, edit, and manage products.
- Update product prices and stock availability.
- Upload and change individual product images.
- Manage product categories and catalogue details.
- Update order statuses.
- Review customer return requests.
- Manage shop branding, logo, and homepage caption.
- Configure shop details, UPI ID, and store email.

### 📞 Contact & Store Information
- Direct phone contact.
- WhatsApp contact option.
- Google Maps location link.
- Easy access to shop information.
- Custom shop logo and branding.
- Mobile-friendly navigation and layout.

### 📧 Invoice & Email
- PDF invoice generation.
- Browser-based invoice printing.
- Automatic invoice PDF email after delivery when SMTP settings are configured.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Templates | Jinja2 |
| Image Assets | SVG and product images |
| Authentication | Session-based login and password hashing |
| Invoice Generation | PDF |

## 📂 Project Structure

```text
vijaypaul-milk-cooldrinks/
│
├── app/
│   ├── app.py
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
│
├── requirements.txt
├── run.py
└── README.md
```

## 🚀 Run the Project on Windows

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/vijaypaul-milk-cooldrinks.git
```

### 2. Open the project folder

```bash
cd vijaypaul-milk-cooldrinks
```

### 3. Create a virtual environment

```bash
py -m venv .venv
```

### 4. Activate the virtual environment

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Start the application

```bash
python run.py
```

### 7. Open the website

- **Customer Website:** http://127.0.0.1:5000
- **Admin Dashboard:** http://127.0.0.1:5000/admin

## ⚙️ Configuration Before Production

- Set a strong and unique `SECRET_KEY`.
- Configure secure admin credentials using `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
- Configure persistent storage for uploaded product images and application data.
- Enter the correct shop UPI ID and email address.
- Configure SMTP environment variables if invoice emails are required.
- Verify product names, images, prices, and stock quantities.
- Use a real payment gateway before enabling automatic online payment verification.
- Use HTTPS for the production website.

## 📌 Important Notes

- Product prices are sample values and should be confirmed by the shop before accepting live orders.
- UPI reference capture requires manual payment verification unless a payment gateway is integrated.
- Product images should be replaced with shop-approved images where necessary.
- A production deployment should use persistent database and image storage.
- Never commit passwords, API keys, secret keys, or customer data to GitHub.

---

**Vijaypaul Milk & Cooldrinks**

*Freshness, Quality & Convenience — All in One Place.*
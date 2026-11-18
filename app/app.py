from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, secrets, os, smtplib
from pathlib import Path
from datetime import datetime
from io import BytesIO
from email.message import EmailMessage
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vijaypaul-dev-secret-change-before-production')
DB = Path(__file__).with_name('store.db')
UPLOAD_DIR = Path(__file__).parent / 'static' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
PHONE = '9290641743'
MAP = 'https://maps.app.goo.gl/mdgAWsgEdQepv62T8?g_st=ac'
ADMIN_USER = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASSWORD', 'admin123')

CATS = [
    ('Milk','🥛','Heritage, Sangam & Vijaya'), ('Curd','🥣','200ml, 500ml & family packs'),
    ('Paneer','🧀','Small & big packs'), ('Cream','🥛','Fresh dairy cream'),
    ('Cheese','🧀','Slices & blocks'), ('Mushrooms','🍄','Fresh packs'),
    ('Ice Cream','🍦','Cups, bars, cones & family packs'), ('Cooldrinks','🥤','Small & big bottles'),
    ('Biscuits','🍪','Small & big packets'), ('Bakery & Snacks','🥨','Bakery & traditional snacks'),
    ('Ready-made','🫓','Chapathi, poori & more'), ('Breakfast','🥣','Bread, eggs & breakfast essentials'),
    ('Chocolates','🍫','Dairy Milk, KitKat, 5 Star & more'), ('Snacks & Condiments','🥫','Sauces, namkeen & quick bites'),
]

# These are real photographs rather than blank placeholders. Product-pack images can be
# swapped later for the shop's exact brand photos without changing the database.
IMG = {
 'milk':'https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=900&q=85',
 'curd':'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=900&q=85',
 'paneer':'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=900&q=85',
 'cream':'https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=900&q=85',
 'cheese':'https://images.unsplash.com/photo-1452195100486-9cc805987862?auto=format&fit=crop&w=900&q=85',
 'mushrooms':'https://images.unsplash.com/photo-1504545102780-26774c1bb073?auto=format&fit=crop&w=900&q=85',
 'icecream':'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?auto=format&fit=crop&w=900&q=85',
 'cooldrink':'https://images.unsplash.com/photo-1629203849820-fdd70d49c38e?auto=format&fit=crop&w=900&q=85',
 'biscuit':'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=900&q=85',
 'bakery':'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=900&q=85',
 'chapathi':'https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=900&q=85',
 'poori':'https://images.unsplash.com/photo-1626132647523-66f5bf380027?auto=format&fit=crop&w=900&q=85',
 'bread':'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=900&q=85',
 'eggs':'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=900&q=85',
 'tea':'https://images.unsplash.com/photo-1594631252845-29fc4cc8cde9?auto=format&fit=crop&w=900&q=85',
 'coffee':'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
 'sugar':'https://images.unsplash.com/photo-1603048297172-c92544798d5a?auto=format&fit=crop&w=900&q=85',
 'snack':'https://images.unsplash.com/photo-1621939514649-280e2aa04c33?auto=format&fit=crop&w=900&q=85',
 'chocolate':'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=900&q=85',
}
# Multiple photographic options per category so the catalogue doesn't reuse one photo
# for every item. Admins can replace any product photo with the exact pack image.
IMG_VARIANTS = {
 'milk':['https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1560807707-8cc77767d783?auto=format&fit=crop&w=900&q=85'],
 'curd':['https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1571212515416-fca7b4e3f6e4?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85'],
 'paneer':['https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=900&q=85'],
 'cream':['https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85'],
 'cheese':['https://images.unsplash.com/photo-1452195100486-9cc805987862?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1552767059-ce182ead6c1b?auto=format&fit=crop&w=900&q=85'],
 'mushrooms':['https://images.unsplash.com/photo-1504545102780-26774c1bb073?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=900&q=85'],
 'icecream':['https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1501446529957-6226bd447c46?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1560008581-09826d1de69e?auto=format&fit=crop&w=900&q=85'],
 'cooldrink':['https://images.unsplash.com/photo-1629203849820-fdd70d49c38e?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1554866585-cd94860890b7?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1581636625402-29b2a704ef13?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1527281400683-1aae777175f8?auto=format&fit=crop&w=900&q=85'],
 'biscuit':['https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=900&q=85'],
 'bakery':['https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1608198093002-ad4e005484df?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85'],
 'chapathi':['https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85'],
 'poori':['https://images.unsplash.com/photo-1626132647523-66f5bf380027?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85'],
 'bread':['https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1608198093002-ad4e005484df?auto=format&fit=crop&w=900&q=85'],
 'eggs':['https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?auto=format&fit=crop&w=900&q=85'],
 'tea':['https://images.unsplash.com/photo-1594631252845-29fc4cc8cde9?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=900&q=85'],
 'coffee':['https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=900&q=85'],
 'sugar':['https://images.unsplash.com/photo-1603048297172-c92544798d5a?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1581441363689-1f3c3c414635?auto=format&fit=crop&w=900&q=85'],
 'snack':['https://images.unsplash.com/photo-1621939514649-280e2aa04c33?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1566478989037-eec170784d0b?auto=format&fit=crop&w=900&q=85','https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=900&q=85'],
}
# Product-specific photographs from public retailer/product listings. Different brands
# get their own package image; pack-size variants of the same SKU may share that SKU image.
# Remote URLs are used so the catalogue doesn't ship a single duplicated placeholder.
PRODUCT_IMAGES = {
    ('milk','heritage'): 'https://www.bbassets.com/media/uploads/p/xl/40147599_4-heritage-standardiseda-milk.jpg',
    ('milk','vijaya'): 'https://cdn.grofers.com/da/cms-assets/cms/product/1db30ff2-c833-48b6-9ecc-21125c5d3259.jpg',
    ('milk','sangam'): 'https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=900&q=85',
    ('curd','heritage'): 'https://images.unsplash.com/photo-1571212515416-fca7b4e3f6e4?auto=format&fit=crop&w=900&q=85',
    ('curd','vijaya'): 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=900&q=85',
    ('curd','sangam'): 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85',
    ('paneer','heritage'): 'https://www.starquik.com/cdn/shop/files/SQ113093.jpg?v=1750941804&width=416',
    ('cheese','amul'): 'https://storage.googleapis.com/shy-pub/359659/7f0305e14ee62fa3e063100759f6813e-1712519858663.jpeg',
    ('cooldrinks','sprite'): 'https://img.cdnx.in/299510/0-8-1744512058293.png?format=webp&width=600',
    ('cooldrinks','thums up'): 'https://cdn1.jiomartjcp.com/v2/catalog-cloud/jiomar/original/images/othe/egurhk/.j/pg/0000000004912973101.jpg.4a1acea2b3.jpg',
    ('cooldrinks','maaza'): 'https://www.starquik.com/cdn/shop/files/SQ105002_FOP_a82b4638-54be-4ec2-b184-e9f1d1856dd4.jpg?v=1776846191',
    ('cooldrinks','coca-cola'): 'https://img.clevup.in/285171/SKU-0985_1-1714180626482.png?format=webp&width=600',
    ('cooldrinks','fanta'): 'https://himkhand.com/cdn/shop/files/251019-2_5-fanta-soft-drink-orange-flavoured.png?v=1776799625',
    ('cooldrinks','pepsi'): 'https://images.rdclick.com/product_content/original/P003568/pepsi-pet-bottle-750-ml-1.jpg',
    ('cooldrinks','7up'): 'https://www.mystore.in/s/62ea2c599d1398fa16dbae0a/67b38a68ccec3f7b6f52577c/8902080304059_1.jpg',
    ('cooldrinks','mountain dew'): 'https://www.vishalmegamart.com/dw/image/v2/BGHT_PRD/on/demandware.static/-/Sites-vmm-fmcg-master-catalog/default/dw23a53e61/images/large/1310012850.jpg?sh=900&sw=900',
    ('cooldrinks','limca'): 'https://images.unsplash.com/photo-1581636625402-29b2a704ef13?auto=format&fit=crop&w=900&q=85',
    ('cooldrinks','mirinda'): 'https://images.unsplash.com/photo-1527281400683-1aae777175f8?auto=format&fit=crop&w=900&q=85',
    ('biscuits','good day'): 'https://www.jiomart.com/images/product/original/490863143/britannia-good-day-butter-cookies-30-g-product-images-o490863143-p590142066-0-202303212004.jpg',
    ('biscuits','marie gold'): 'https://aapkabazar.co/_next/image?q=75&url=https%3A%2F%2Fimage.aapkabazar.co%2Fproduct%2F6831%2F1735619223745.png%3Ftype%3Dwebp%26width%3D800&w=1080',
    ('biscuits','50-50'): 'https://www.familygarden.in/image/cache/catalog/Biscuts/5050-GREEN-10RS-1-1000x1000.jpg',
    ('biscuits','bourbon'): 'https://karthika.sg/image/catalog/products/CookiesBiscuits/400052.jpg',
    ('biscuits','parle-g'): 'https://cdn.dotpe.in/longtail/item_thumbnails/9367125/esQk4lsh-800-800.webp',
    ('biscuits','monaco'): 'https://www.bbassets.com/media/uploads/p/xxl/402823-2_11-parle-monaco-biscuits.jpg',
    ('biscuits','hide & seek'): 'https://www.quickpantry.in/cdn/shop/files/Parle_Hide_Seek_Chocolate_120_g_Quick_Pantry.jpg?v=1747302255&width=1214',
    ('biscuits','dark fantasy'): 'https://cdn.grofers.com/da/cms-assets/cms/product_videos_thumbnails/2e2c7a5d-12e0-4d26-9e8f-d5c11c9dbb4d.jpg',
    ('biscuits','jim jam'): 'https://img.cdnx.in/71794/1653225025610_81csNoCxPyLSL1500.jpeg?format=webp',
    ('biscuits','krackjack'): 'https://www.exoticsnackguys.com/cdn/shop/files/parlekrackkjackk_1200x1200.webp?v=1716596747',
    ('chocolates','dairy milk'): 'https://www.jiomart.com/images/product/original/490001325/cadbury-dairy-milk-chocolate-bar-13-2-g-product-images-o490001325-p490001325-0-202203150443.jpg',
    ('chocolates','kitkat'): 'https://www.jiomart.com/images/product/original/490001326/nestle-kitkat-crispy-wafer-coated-with-chocolate-18-g-product-images-o490001326-p490001326-0-202203150443.jpg',
    ('chocolates','5 star'): 'https://www.jiomart.com/images/product/original/490001327/cadbury-5-star-chocolate-bar-22-g-product-images-o490001327-p490001327-0-202203150443.jpg',
    ('chocolates','munch'): 'https://www.jiomart.com/images/product/original/490001329/nestle-munch-crunchy-wafer-coated-with-chocolate-10-g-product-images-o490001329-p490001329-0-202203150443.jpg',
    ('chocolates','perk'): 'https://www.jiomart.com/images/product/original/490001328/cadbury-perk-wafer-chocolate-13-g-product-images-o490001328-p490001328-0-202203150443.jpg',
    ('chocolates','gems'): 'https://www.jiomart.com/images/product/original/490001330/cadbury-gems-coated-chocolate-buttons-8-g-product-images-o490001330-p490001330-0-202203150443.jpg',
    ('chocolates','milkybar'): 'https://www.jiomart.com/images/product/original/490001331/nestle-milkybar-white-chocolate-12-g-product-images-o490001331-p490001331-0-202203150443.jpg',
    ('chocolates','snickers'): 'https://www.jiomart.com/images/product/original/490001332/snickers-peanut-chocolate-bar-22-g-product-images-o490001332-p490001332-0-202203150443.jpg',
    ('daily essentials','tata'): 'https://storage.googleapis.com/shy-pub/285171/1685421444400_SKU-0219_0.png',
    ('daily essentials','bru'): 'https://dukaan.b-cdn.net/1000x1000/webp/master/products/bru-coffee-small-sachet.png',
    ('daily essentials','kissan'): 'https://jaimamart.com/storage/flash-sales/kissan-fresh-tomato-ketchup-1-kg-product-images-o490000799-p490000799-1-202203170349-1.jpg',
    ('daily essentials','cadbury'): 'https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy%2Cf_auto%2Cq_auto/NI_CATALOG/IMAGES/CIW/2025/11/11/c25e7414-aea9-4037-8950-2ebaa3756d01_13729_1.png',
    ('bakery & snacks','boondhi'): 'https://zorastore.eu/cdn/shop/files/image-1000x1000_33_c174743a-0cad-48c7-8f68-83ed5e1bf7cb_512x512.png?v=1739468329',
    ('bakery & snacks','mixture'): 'https://storage.googleapis.com/shy-pub/297573/SKU-13981_0-1773893373709.jpg',
    ('bakery & snacks','murukku'): 'https://punjabigroceries.com/cdn/shop/products/murruku-haldiram.jpg?v=1595794343',
    ('bakery & snacks','banana chips'): 'https://www.keralataste.com/cdn/shop/products/image_a854b010-3b79-40ff-98c3-00f6f95b8d56_800x.jpg?v=1680721192',
    ('bakery & snacks','palli vunda'): 'https://budgetbaskets4u.com/images/products/5184fc40740f04100f4302ccc92cf64c.png',
    ('ready-made','chapathi'): 'https://www.dryfii.com/cdn/shop/files/15_12692d21-9541-4283-b54d-012784688b68.png?v=1737000199&width=1445',
    ('ready-made','poori'): 'https://www.bbassets.com/media/uploads/p/xxl/40262087_1-haiku-instant-poori-100-natural-fresh-healthy.jpg',
}

# For products without a verified branded pack photo, use a distinct, relevant photograph
# rather than repeating the same image across every card.
ITEM_IMAGES = {
    'dairy milk chocolate': 'https://www.jiomart.com/images/product/original/490001325/cadbury-dairy-milk-chocolate-bar-13-2-g-product-images-o490001325-p490001325-0-202203150443.jpg',
    'kitkat chocolate': 'https://www.jiomart.com/images/product/original/490001326/nestle-kitkat-crispy-wafer-coated-with-chocolate-18-g-product-images-o490001326-p490001326-0-202203150443.jpg',
    '5 star chocolate': 'https://www.jiomart.com/images/product/original/490001327/cadbury-5-star-chocolate-bar-22-g-product-images-o490001327-p490001327-0-202203150443.jpg',
    'munch chocolate': 'https://www.jiomart.com/images/product/original/490001329/nestle-munch-crunchy-wafer-coated-with-chocolate-10-g-product-images-o490001329-p490001329-0-202203150443.jpg',
    'perk chocolate': 'https://www.jiomart.com/images/product/original/490001328/cadbury-perk-wafer-chocolate-13-g-product-images-o490001328-p490001328-0-202203150443.jpg',
    'gems chocolate': 'https://www.jiomart.com/images/product/original/490001330/cadbury-gems-coated-chocolate-buttons-8-g-product-images-o490001330-p490001330-0-202203150443.jpg',
    'milkybar chocolate': 'https://www.jiomart.com/images/product/original/490001331/nestle-milkybar-white-chocolate-12-g-product-images-o490001331-p490001331-0-202203150443.jpg',
    'snickers chocolate': 'https://www.jiomart.com/images/product/original/490001332/snickers-peanut-chocolate-bar-22-g-product-images-o490001332-p490001332-0-202203150443.jpg',
    'fresh paneer small pack': 'https://www.starquik.com/cdn/shop/files/SQ113093.jpg?v=1750941804&width=416',
    'fresh paneer big pack': 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=900&q=85',
    'premium paneer': 'https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85',
    'fresh cream': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=900&q=85',
    'processed cheese slices': 'https://storage.googleapis.com/shy-pub/359659/7f0305e14ee62fa3e063100759f6813e-1712519858663.jpeg',
    'cheese block': 'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=900&q=85',
    'mozzarella cheese': 'https://images.unsplash.com/photo-1552767059-ce182ead6c1b?auto=format&fit=crop&w=900&q=85',
    'fresh mushrooms': 'https://images.unsplash.com/photo-1504545102780-26774c1bb073?auto=format&fit=crop&w=900&q=85',
    'ice cream cup': 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?auto=format&fit=crop&w=900&q=85',
    'chocolate chocobar': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=900&q=85',
    'ice cream cone': 'https://images.unsplash.com/photo-1501446529957-6226bd447c46?auto=format&fit=crop&w=900&q=85',
    'kulfi stick': 'https://images.unsplash.com/photo-1560008581-09826d1de69e?auto=format&fit=crop&w=900&q=85',
    'ice cream family pack': 'https://cdn.dotpe.in/longtail/dotpe-bills/6315874/MrBEGbSX.jpeg',
    'ice cream party tub': 'https://images.unsplash.com/photo-1557142046-c704a3adf364?auto=format&fit=crop&w=900&q=85',
    'hide & seek biscuits': 'https://www.quickpantry.in/cdn/shop/files/Parle_Hide_Seek_Chocolate_120_g_Quick_Pantry.jpg?v=1747302255&width=1214',
    'dark fantasy biscuits': 'https://cdn.grofers.com/da/cms-assets/cms/product_videos_thumbnails/2e2c7a5d-12e0-4d26-9e8f-d5c11c9dbb4d.jpg',
    'jim jam biscuits': 'https://img.cdnx.in/71794/1653225025610_81csNoCxPyLSL1500.jpeg?format=webp',
    'krackjack biscuits': 'https://www.exoticsnackguys.com/cdn/shop/files/parlekrackkjackk_1200x1200.webp?v=1716596747',
    'chakralu': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=900&q=85',
    'sunnuvunda': 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=900&q=85',
    'kara boondi': 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=900&q=85',
    'chekkalu': 'https://images.unsplash.com/photo-1621939514649-280e2aa04c33?auto=format&fit=crop&w=900&q=85',
    'ribbon pakoda': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=900&q=85',
    'nippattu': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=900&q=85',
    'white bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=900&q=85',
    'brown bread': 'https://images.unsplash.com/photo-1608198093002-ad4e005484df?auto=format&fit=crop&w=900&q=85',
    'milk bread': 'https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=900&q=85',
    'burger buns': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=900&q=85',
    'eggs': 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=900&q=85',
    'idli/dosa batter': 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=900&q=85',
    'namkeen': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=900&q=85',
    'sugar': 'https://images.unsplash.com/photo-1581441363689-1f3c3c414635?auto=format&fit=crop&w=900&q=85',
    'salt': 'https://images.unsplash.com/photo-1603048297172-c92544798d5a?auto=format&fit=crop&w=900&q=85',
    'toothpaste': 'https://images.unsplash.com/photo-1609840114035-3c981b782dfe?auto=format&fit=crop&w=900&q=85',
}

def best_product_image(name, brand, category, current=''):
    """Pick a relevant SKU/brand photo; preserve admin-uploaded local files."""
    current = (current or '').strip()
    if current and not current.startswith(('http://', 'https://')) and current not in IMG:
        return current
    n = (name or '').lower().strip()
    b = (brand or '').lower().strip()
    c = (category or '').lower().strip()
    if n in ITEM_IMAGES:
        return ITEM_IMAGES[n]
    for (cat_key, brand_key), url in PRODUCT_IMAGES.items():
        if c == cat_key and brand_key in b:
            return url
    # Product names such as brand-labelled biscuit and drink entries use brand photos.
    for (cat_key, brand_key), url in PRODUCT_IMAGES.items():
        if c == cat_key and (brand_key in n or (brand_key == 'parle-g' and 'parle-g' in n)):
            return url
    return current or IMG.get({'cooldrinks':'cooldrink','biscuits':'biscuit','bakery & snacks':'bakery','ready-made':'chapathi','daily essentials':'snack','snacks & condiments':'snack','chocolates':'chocolate'}.get(c, c), IMG['snack'])

P = []
def add(n,c,b,pack,price,img): P.append((n,c,b,pack,price,img))

for b in ['Heritage','Sangam','Vijaya']:
    for pack, pr in [('200 ml',16),('500 ml',32),('1 L',64)]: add(f'{b} Milk','Milk',b,pack,pr,'milk')
    for pack, pr in [('200 ml',15),('500 ml',35),('1 kg',80)]: add(f'{b} Curd Packet','Curd',b,pack,pr,'curd')

for n,pack,pr in [('Fresh Paneer Small Pack','200 g',85),('Fresh Paneer Big Pack','500 g',195),('Premium Paneer','1 kg',380)]: add(n,'Paneer','Assorted',pack,pr,'paneer')
for n,pack,pr in [('Fresh Cream','200 ml',65),('Fresh Cream','500 ml',145)]: add(n,'Cream','Assorted',pack,pr,'cream')
for n,pack,pr in [('Processed Cheese Slices','200 g',110),('Cheese Block','200 g',125),('Mozzarella Cheese','200 g',150)]: add(n,'Cheese','Assorted',pack,pr,'cheese')
for n,pack,pr in [('Fresh Mushrooms','200 g',70),('Fresh Mushrooms','500 g',150)]: add(n,'Mushrooms','Fresh',pack,pr,'mushrooms')
for n,pack,pr in [('Ice Cream Cup','100 ml',30),('Chocolate Chocobar','1 piece',35),('Ice Cream Cone','1 piece',40),('Kulfi Stick','1 piece',35),('Ice Cream Family Pack','700 ml',240),('Ice Cream Family Pack','1 L',320),('Ice Cream Party Tub','2 L',560)]: add(n,'Ice Cream','Assorted',pack,pr,'icecream')
for b in ['Sprite','Thums Up','Maaza','Coca-Cola','Fanta','Limca','Mountain Dew','Pepsi','7UP','Mirinda']:
    for pack,pr in [('250 ml',20),('600 ml',40),('750 ml',45),('1.25 L',55),('2.25 L',95)]: add(b,'Cooldrinks',b,pack,pr,'cooldrink')
for b in ['Good Day','Marie Gold','50-50','Bourbon','Parle-G','Hide & Seek','Dark Fantasy','Jim Jam','Monaco','KrackJack']:
    for pack,pr in [('small pack',10),('big pack',40)]: add(b+' Biscuits','Biscuits',b,pack,pr,'biscuit')
for n in ['Chakralu','Palli Vunda','Sunnuvunda','Boondhi','Mixture','Kara Boondi','Murukku','Chekkalu','Ribbon Pakoda','Nippattu','Banana Chips']:
    add(n,'Bakery & Snacks','Vijaypaul','packet',50,'bakery')
for n,pack,pr,img in [('Ready-made Chapathi','10 pieces',70,'chapathi'),('Ready-made Chapathi','20 pieces',130,'chapathi'),('Ready-made Poori','10 pieces',80,'poori'),('Ready-made Poori','20 pieces',150,'poori')]: add(n,'Ready-made','Vijaypaul',pack,pr,img)
for n,pack,pr,img in [('White Bread','400 g',50,'bread'),('Brown Bread','400 g',60,'bread'),('Milk Bread','400 g',55,'bread'),('Burger Buns','4 pieces',45,'bread'),('Eggs','6 pieces',48,'eggs'),('Eggs','12 pieces',94,'eggs'),('Idli/Dosa Batter','1 kg',100,'bread')]: add(n,'Breakfast','Assorted',pack,pr,img)
for n,b,pack,pr,img in [('Tomato Ketchup','Kissan','500 g',125,'snack'),('Namkeen','Assorted','200 g',50,'snack')]: add(n,'Snacks & Condiments',b,pack,pr,img)
for b,base_price,small_pack,big_pack in [('Dairy Milk',20,'13.2 g','52 g'),('KitKat',20,'18 g','41.5 g'),('5 Star',20,'22 g','40 g'),('Munch',10,'10 g','30 g'),('Perk',10,'13 g','35 g'),('Gems',10,'8 g','22 g'),('Milkybar',10,'12 g','40 g'),('Snickers',30,'22 g','50 g')]:
    add(b+' Chocolate','Chocolates',b,small_pack,base_price,'chocolate')
    add(b+' Chocolate','Chocolates',b,big_pack,base_price*2,'chocolate')

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
    c=db()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY,name,category,brand,pack,price,image,stock INTEGER DEFAULT 20,active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,order_no UNIQUE,name,phone,address,payment,status,total,created,user_id INTEGER);
    CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY,order_id,product_id,name,pack,price,qty);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name,phone UNIQUE,email UNIQUE,password,role TEXT DEFAULT 'customer',created);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS returns(id INTEGER PRIMARY KEY,order_id INTEGER,user_id INTEGER,reason TEXT,status TEXT DEFAULT 'Requested',created TEXT);
    CREATE TABLE IF NOT EXISTS addresses(id INTEGER PRIMARY KEY,user_id INTEGER,label TEXT,address TEXT,phone TEXT, UNIQUE(user_id,label,address));
    ''')
    for col,definition in [('payment_ref','TEXT'),('delivery_otp','TEXT'),('otp_verified','INTEGER DEFAULT 0')]:
        if col not in {r['name'] for r in c.execute('pragma table_info(orders)').fetchall()}: c.execute(f'alter table orders add column {col} {definition}')
    c.execute("insert or ignore into settings(key,value) values('upi_id',''),('store_email',''),('store_name','Vijaypaul Milk & Cooldrinks'),('store_caption','Fresh dairy, chilled drinks and everyday favourites — all in one place.'),('logo_file','')")
    cols={r['name'] for r in c.execute('pragma table_info(orders)').fetchall()}
    if 'user_id' not in cols: c.execute('alter table orders add column user_id INTEGER')
    if c.execute('select count(*) from products').fetchone()[0]==0:
        seed_rows=[]
        counts={}
        for n,cat,brand,pack,price,img_key in P:
            options=IMG_VARIANTS.get(img_key,[IMG.get(img_key,IMG['snack'])])
            index=counts.get(img_key,0); counts[img_key]=index+1
            starter=options[index % len(options)]
            seed_rows.append((n,cat,brand,pack,price,best_product_image(n,brand,cat,starter)))
        c.executemany('insert into products(name,category,brand,pack,price,image) values(?,?,?,?,?,?)',seed_rows)
    # Upgrade old catalogues: use brand/SKU-specific images instead of rotating a tiny
    # category list (which caused unrelated products to display repeated photographs).
    legacy=c.execute('select id,category,name,brand,image from products order by id').fetchall()
    seen={}
    for row in legacy:
        val=row['image'] or ''
        if val in IMG:
            options=IMG_VARIANTS.get(val,[IMG[val]])
            ix=seen.get(val,0); seen[val]=ix+1
            val=options[ix % len(options)]
        if not (val and val.startswith('uploads/')):
            chosen=best_product_image(row['name'],row['brand'],row['category'],val)
            if chosen and chosen != row['image']:
                c.execute('update products set image=? where id=?',(chosen,row['id']))
    # Catalogue cleanup/additions also apply to existing SQLite databases on upgrades.
    c.execute("delete from products where lower(trim(name)) in ('salt','sugar','toothpaste','tea powder','coffee powder')")
    c.execute("delete from products where lower(trim(category))='daily essentials' and lower(trim(name)) in ('salt','sugar','toothpaste','tea powder','coffee powder')")
    c.execute("update products set category='Snacks & Condiments' where lower(trim(category))='daily essentials'")
    for b,base_price,small_pack,big_pack in [('Dairy Milk',20,'13.2 g','52 g'),('KitKat',20,'18 g','41.5 g'),('5 Star',20,'22 g','40 g'),('Munch',10,'10 g','30 g'),('Perk',10,'13 g','35 g'),('Gems',10,'8 g','22 g'),('Milkybar',10,'12 g','40 g'),('Snickers',30,'22 g','50 g')]:
        for pack,price in [(small_pack,base_price),(big_pack,base_price*2)]:
            exists=c.execute('select id from products where lower(name)=? and lower(category)=? and lower(brand)=? and lower(pack)=?',(f'{b} chocolate'.lower(),'chocolates',b.lower(),pack.lower())).fetchone()
            if not exists:
                image=best_product_image(b+' Chocolate',b,'Chocolates',IMG['chocolate'])
                c.execute('insert into products(name,category,brand,pack,price,image,stock,active) values(?,?,?,?,?,?,20,1)',(b+' Chocolate','Chocolates',b,pack,price,image))
    c.commit(); c.close()
init()

@app.context_processor
def ctx():
    user = None
    if session.get('user_id'):
        c=db(); user=c.execute('select id,name,phone,email,role from users where id=?',(session['user_id'],)).fetchone(); c.close()
    c=db(); st={r['key']:r['value'] for r in c.execute('select key,value from settings').fetchall()}; c.close()
    def product_image(value):
        if not value: return IMG['snack']
        if value.startswith('http://') or value.startswith('https://'): return value
        if value in IMG: return IMG[value]
        return url_for('static', filename='uploads/' + value.removeprefix('uploads/'))
    return dict(phone=PHONE,map_url=MAP,categories=CATS,img=IMG,product_image=product_image,cart_count=sum(session.get('cart',{}).values()),current_user=user,store_settings=st)

def products(cat='',q=''):
    c=db(); sql='select * from products where active=1'; a=[]
    if cat: sql+=' and category=?'; a.append(cat)
    if q: sql+=' and (name like ? or brand like ? or category like ? or pack like ?)'; a += ['%'+q+'%']*4
    r=c.execute(sql+' order by category,name,price',a).fetchall(); c.close(); return r

def login_required(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        if not session.get('user_id'):
            flash('Please login to continue.','info'); return redirect(url_for('login',next=request.path))
        return fn(*args,**kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        if not session.get('admin'): return redirect('/admin')
        return fn(*args,**kwargs)
    return wrapper

@app.route('/')
def home(): return render_template('index.html',products=products(request.args.get('category',''),request.args.get('q','')),cat=request.args.get('category',''),q=request.args.get('q',''))

@app.route('/product/<int:id>')
def product(id):
    c=db(); p=c.execute('select * from products where id=? and active=1',(id,)).fetchone(); c.close()
    return render_template('product.html',p=p) if p else ('Not found',404)

@app.post('/cart/add')
def addcart():
    x=str(request.form['product_id']); cart=session.get('cart',{}); cart[x]=cart.get(x,0)+max(1,int(request.form.get('qty',1))); session['cart']=cart
    flash('Added to cart.','success'); return redirect(request.referrer or '/')

@app.route('/cart')
def cart():
    c=db(); cart=session.get('cart',{}); items=[]; total=0
    for k,q in cart.items():
        p=c.execute('select * from products where id=? and active=1',(k,)).fetchone()
        if p: items.append((p,q,p['price']*q)); total+=p['price']*q
    c.close(); return render_template('cart.html',items=items,total=total)

@app.post('/cart/update')
def update():
    cart=session.get('cart',{})
    for k in list(cart):
        q=int(request.form.get('q_'+k,0)); cart.pop(k,None) if q<=0 else cart.__setitem__(k,q)
    session['cart']=cart; return redirect('/cart')

@app.post('/cart/clear')
def clear(): session['cart']={}; return redirect('/cart')

@app.route('/checkout',methods=['GET','POST'])
@login_required
def checkout():
    if not session.get('cart'): return redirect('/cart')
    c=db(); saved_addresses=c.execute('select * from addresses where user_id=? order by id desc',(session['user_id'],)).fetchall(); items=[]; total=0
    for k,q in session['cart'].items():
        p=c.execute('select * from products where id=? and active=1',(k,)).fetchone()
        if p: items.append((p,q,p['price']*q)); total+=p['price']*q
    if request.method=='POST':
        name=request.form['name'].strip(); phone=request.form['phone'].strip(); addr=request.form['address'].strip(); pay=request.form['payment']
        saved_id=request.form.get('saved_address','').strip()
        if saved_id:
            saved=c.execute('select address,phone from addresses where id=? and user_id=?',(saved_id,session['user_id'])).fetchone()
            if saved: addr=saved['address']; phone=saved['phone']
        no='VP'+datetime.now().strftime('%y%m%d')+secrets.token_hex(3).upper()
        cur=c.execute('insert into orders(order_no,name,phone,address,payment,status,total,created,user_id) values(?,?,?,?,?,?,?,?,?)',(no,name,phone,addr,pay,'Order Received',total,datetime.now().isoformat(timespec='seconds'),session['user_id']))
        oid=cur.lastrowid
        otp=f'{secrets.randbelow(900000)+100000}'
        c.execute('update orders set delivery_otp=? where id=?',(otp,oid))
        for p,q,sub in items:
            c.execute('insert into items(order_id,product_id,name,pack,price,qty) values(?,?,?,?,?,?)',(oid,p['id'],p['name'],p['pack'],p['price'],q))
            c.execute('update products set stock=max(stock-?,0) where id=?',(q,p['id']))
        c.execute('insert or ignore into addresses(user_id,label,address,phone) values(?,?,?,?)',(session['user_id'],'Home',addr,phone))
        c.commit(); c.close(); session['cart']={}; return redirect('/order/'+no)
    c.close(); return render_template('checkout.html',items=items,total=total,saved_addresses=saved_addresses)

@app.route('/order/<no>')
def order(no):
    c=db(); o=c.execute('select * from orders where order_no=?',(no,)).fetchone(); its=c.execute('select * from items where order_id=?',(o['id'],)).fetchall() if o else []; c.close()
    return render_template('order.html',o=o,items=its) if o else ('Not found',404)

def invoice_pdf(order, items):
    # PDF invoices are generated only when reportlab is installed (it is in requirements.txt).
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buf=BytesIO(); pdf=canvas.Canvas(buf,pagesize=A4); w,h=A4; y=h-55
    pdf.setFont('Helvetica-Bold',18); pdf.drawString(48,y,store_name()); y-=28
    pdf.setFont('Helvetica',10)
    for line in [f"Order / Invoice: {order['order_no']}", f"Date: {order['created']}", f"Customer: {order['name']}  Phone: {order['phone']}", f"Address: {order['address']}", f"Payment: {order['payment']}  Status: {order['status']}"]:
        pdf.drawString(48,y,line[:110]); y-=17
    y-=10; pdf.setFont('Helvetica-Bold',10); pdf.drawString(48,y,'Item'); pdf.drawString(290,y,'Pack'); pdf.drawString(365,y,'Qty'); pdf.drawString(410,y,'Price'); pdf.drawString(480,y,'Amount'); y-=15
    pdf.setFont('Helvetica',9)
    for item in items:
        if y<70: pdf.showPage(); y=h-55; pdf.setFont('Helvetica',9)
        pdf.drawString(48,y,str(item['name'])[:38]); pdf.drawString(290,y,str(item['pack'])[:12]); pdf.drawRightString(390,y,str(item['qty'])); pdf.drawRightString(455,y,f"Rs. {item['price']:.2f}"); pdf.drawRightString(545,y,f"Rs. {item['price']*item['qty']:.2f}"); y-=16
    y-=10; pdf.setFont('Helvetica-Bold',12); pdf.drawRightString(545,y,f"Total: Rs. {order['total']:.2f}  |  Delivery: FREE")
    pdf.setFont('Helvetica',9); pdf.drawString(48,35,'Thank you for shopping with us. Sample catalogue prices may vary.'); pdf.save(); buf.seek(0); return buf.getvalue()

def store_name():
    c=db(); r=c.execute("select value from settings where key='store_name'").fetchone(); c.close(); return r['value'] if r else 'Vijaypaul Milk & Cooldrinks'

def email_invoice(order, items):
    # Configure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, and SMTP_FROM in deployment.
    required=['SMTP_HOST','SMTP_PORT','SMTP_USER','SMTP_PASSWORD','SMTP_FROM']
    if not all(os.getenv(k) for k in required): return False
    c=db(); user=c.execute('select email from users where id=?',(order['user_id'],)).fetchone() if order['user_id'] else None; c.close()
    if not user or not user['email']: return False
    msg=EmailMessage(); msg['Subject']=f"Your Vijaypaul order invoice {order['order_no']}"; msg['From']=os.environ['SMTP_FROM']; msg['To']=user['email']
    msg.set_content(f"Thank you for shopping with {store_name()}. Your order {order['order_no']} is delivered. Please find your invoice attached.")
    msg.add_attachment(invoice_pdf(order,items),maintype='application',subtype='pdf',filename=f"invoice-{order['order_no']}.pdf")
    with smtplib.SMTP(os.environ['SMTP_HOST'],int(os.environ['SMTP_PORT']),timeout=20) as server:
        server.starttls(); server.login(os.environ['SMTP_USER'],os.environ['SMTP_PASSWORD']); server.send_message(msg)
    return True

@app.route('/order/<no>/invoice.pdf')
def invoice_pdf_download(no):
    from flask import send_file
    c=db(); o=c.execute('select * from orders where order_no=?',(no,)).fetchone(); its=c.execute('select * from items where order_id=?',(o['id'],)).fetchall() if o else []; c.close()
    if not o: return ('Not found',404)
    if not session.get('admin') and (not session.get('user_id') or o['user_id'] != session.get('user_id')): return redirect('/login')
    return send_file(BytesIO(invoice_pdf(o,its)),mimetype='application/pdf',as_attachment=True,download_name=f"invoice-{no}.pdf")

@app.route('/order/<no>/invoice')
def invoice(no):
    c=db(); o=c.execute('select * from orders where order_no=?',(no,)).fetchone(); its=c.execute('select * from items where order_id=?',(o['id'],)).fetchall() if o else []; c.close()
    if not o: return ('Not found',404)
    if not session.get('admin') and (not session.get('user_id') or o['user_id'] != session.get('user_id')): return redirect('/login')
    return render_template('invoice.html',o=o,items=its)

@app.post('/order/<no>/payment-reference')
@login_required
def customer_payment_reference(no):
    ref=request.form.get('payment_ref','').strip()
    if not ref:
        flash('Enter the UPI transaction/reference number.','error'); return redirect('/order/'+no)
    c=db(); o=c.execute('select * from orders where order_no=? and user_id=?',(no,session['user_id'])).fetchone()
    if not o: c.close(); return ('Not found',404)
    if o['payment']!='UPI_ON_DELIVERY' or o['status']!='Out for Delivery':
        c.close(); flash('Payment reference can only be submitted for UPI-on-delivery orders that are out for delivery.','error'); return redirect('/order/'+no)
    c.execute('update orders set payment_ref=? where id=?',(ref,o['id'])); c.commit(); c.close(); flash('UPI reference submitted. The store will verify it manually.','success'); return redirect('/order/'+no)

@app.post('/order/<no>/return')
@login_required
def request_return(no):
    reason=request.form.get('reason','').strip()
    c=db(); o=c.execute('select * from orders where order_no=? and user_id=?',(no,session['user_id'])).fetchone()
    if not o: c.close(); return ('Not found',404)
    if o['status']!='Delivered': flash('Returns can only be requested after delivery.','error')
    else:
        c.execute('insert into returns(order_id,user_id,reason,status,created) values(?,?,?,?,?)',(o['id'],session['user_id'],reason or 'Customer requested return','Requested',datetime.now().isoformat(timespec='seconds'))); c.commit(); flash('Return request submitted to the store.','success')
    c.close(); return redirect('/dashboard')

@app.post('/order/<no>/buy-again')
@login_required
def buy_again(no):
    c=db(); o=c.execute('select * from orders where order_no=? and user_id=?',(no,session['user_id'])).fetchone()
    if not o: c.close(); return ('Not found',404)
    for it in c.execute('select product_id,qty from items where order_id=?',(o['id'],)).fetchall():
        if it['product_id']:
            key=str(it['product_id']); cart=session.get('cart',{}); cart[key]=cart.get(key,0)+it['qty']; session['cart']=cart
    c.close(); flash('Available items from your order were added to the cart.','success'); return redirect('/cart')

@app.route('/orders')
def orders():
    ph=request.args.get('phone',''); c=db()
    r=c.execute('select * from orders where phone=? order by id desc',(ph,)).fetchall() if ph else []
    c.close(); return render_template('orders.html',orders=r,phone=ph)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form['name'].strip(); phone=request.form['phone'].strip(); email=request.form['email'].strip().lower(); password=request.form['password']
        if len(password)<6: flash('Password must be at least 6 characters.','error'); return render_template('register.html')
        c=db()
        try:
            cur=c.execute('insert into users(name,phone,email,password,role,created) values(?,?,?,?,?,?)',(name,phone,email,generate_password_hash(password),'customer',datetime.now().isoformat(timespec='seconds'))); c.commit(); session['user_id']=cur.lastrowid
            flash('Account created successfully.','success'); return redirect('/dashboard')
        except sqlite3.IntegrityError:
            flash('Phone or email is already registered.','error')
        finally: c.close()
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        ident=request.form['identifier'].strip().lower(); password=request.form['password']
        if ident==ADMIN_USER.lower() and password==ADMIN_PASS:
            session.clear(); session['admin']=1; return redirect('/admin')
        c=db(); u=c.execute('select * from users where (lower(email)=? or phone=?) and role="customer"',(ident,ident)).fetchone()
        valid=False
        if u:
            try: valid=check_password_hash(u['password'],password)
            except (ValueError,TypeError): valid=False
            if not valid and u['password']==password:
                c.execute('update users set password=? where id=?',(generate_password_hash(password),u['id'])); c.commit(); valid=True
        c.close()
        if u and valid:
            session.clear(); session['user_id']=u['id']; return redirect(request.form.get('next') or '/dashboard')
        flash('Invalid login details.','error')
    return render_template('login.html',next=request.args.get('next',''))

@app.route('/logout')
def logout(): session.clear(); flash('You have been logged out.','success'); return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    c=db(); u=c.execute('select id,name,phone,email from users where id=?',(session['user_id'],)).fetchone(); os=c.execute('select * from orders where user_id=? order by id desc',(session['user_id'],)).fetchall(); c.close()
    return render_template('dashboard.html',user=u,orders=os)

@app.route('/dashboard/profile',methods=['POST'])
@login_required
def profile():
    name=request.form['name'].strip(); phone=request.form['phone'].strip(); email=request.form['email'].strip().lower(); c=db()
    try: c.execute('update users set name=?,phone=?,email=? where id=?',(name,phone,email,session['user_id'])); c.commit(); flash('Profile updated.','success')
    except sqlite3.IntegrityError: flash('Phone or email is already used by another account.','error')
    finally: c.close()
    return redirect('/dashboard')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method=='POST':
        if request.form.get('identifier')==ADMIN_USER and request.form.get('password')==ADMIN_PASS: session.clear(); session['admin']=1
        else: flash('Wrong admin login.','error')
    if not session.get('admin'): return render_template('admin_login.html')
    c=db(); ps=c.execute('select * from products order by category,name,pack').fetchall(); os=c.execute('select * from orders order by id desc limit 100').fetchall(); customers=c.execute('select count(*) from users where role="customer"').fetchone()[0]; return_requests=c.execute('select r.*,o.order_no,o.name from returns r join orders o on o.id=r.order_id order by r.id desc').fetchall(); c.close()
    return render_template('admin.html',products=ps,orders=os,customers=customers,return_requests=return_requests)

@app.post('/admin/product/<int:id>')
@admin_required
def ap(id):
    c=db(); product=c.execute('select * from products where id=?',(id,)).fetchone()
    if not product: c.close(); flash('Product not found.','error'); return redirect('/admin')
    price=max(0,float(request.form.get('price',product['price'])))
    stock=max(0,int(request.form.get('stock',product['stock'])))
    image=request.files.get('image')
    image_value=product['image']
    if image and image.filename:
        ext=Path(image.filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            c.close(); flash('Upload a PNG, JPG, JPEG, WEBP or GIF image.','error'); return redirect('/admin')
        filename=f'product-{id}-{secrets.token_hex(5)}{ext}'
        image.save(UPLOAD_DIR / secure_filename(filename))
        image_value=filename
    c.execute('update products set price=?,stock=?,image=? where id=?',(price,stock,image_value,id)); c.commit(); c.close()
    flash('Product details saved.' + (' Product image updated.' if image and image.filename else ''),'success')
    return redirect('/admin')

@app.post('/admin/order/<int:id>')
@admin_required
def ao(id):
    status=request.form['status']
    if status=='Delivered':
        flash('Use Delivery Verification: enter the customer OTP and confirm any UPI-on-delivery reference before marking delivered.','error'); return redirect('/admin')
    c=db(); c.execute('update orders set status=? where id=?',(status,id)); c.commit(); c.close(); return redirect('/admin')

@app.post('/admin/branding')
@admin_required
def admin_branding():
    caption=request.form.get('store_caption','').strip()[:180]
    logo=request.files.get('logo')
    c=db(); c.execute("insert into settings(key,value) values('store_caption',?) on conflict(key) do update set value=excluded.value",(caption,))
    if logo and logo.filename:
        ext=Path(logo.filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            c.close(); flash('Logo must be PNG, JPG, JPEG, WEBP or GIF.','error'); return redirect('/admin')
        filename=f'shop-logo-{secrets.token_hex(5)}{ext}'; logo.save(UPLOAD_DIR / secure_filename(filename))
        c.execute("insert into settings(key,value) values('logo_file',?) on conflict(key) do update set value=excluded.value",(filename,))
    c.commit(); c.close(); flash('Homepage branding saved.','success'); return redirect('/admin')

@app.post('/admin/settings')
@admin_required
def admin_settings():
    c=db()
    for key in ['upi_id','store_email','store_name']:
        c.execute('insert into settings(key,value) values(?,?) on conflict(key) do update set value=excluded.value',(key,request.form.get(key,'').strip()))
    c.commit(); c.close(); flash('Store details saved.','success'); return redirect('/admin')

@app.post('/admin/verify-delivery/<int:id>')
@admin_required
def verify_delivery(id):
    entered=request.form.get('otp','').strip(); c=db(); o=c.execute('select * from orders where id=?',(id,)).fetchone()
    if o and o['delivery_otp']==entered and (o['payment']!='UPI_ON_DELIVERY' or (o['payment_ref'] and o['payment_ref'].strip())):
        c.execute("update orders set status='Delivered',otp_verified=1 where id=?",(id,)); c.commit(); its=c.execute('select * from items where order_id=?',(id,)).fetchall(); delivered=c.execute('select * from orders where id=?',(id,)).fetchone(); emailed=False
        try: emailed=email_invoice(delivered,its)
        except Exception: app.logger.exception('Invoice email failed')
        flash('Delivery OTP verified and order marked delivered.' + (' Invoice emailed to customer.' if emailed else ' Configure SMTP settings to email the PDF invoice automatically.'),'success')
    else: flash('OTP is incorrect, or UPI reference is missing for UPI-on-delivery.','error')
    c.close(); return redirect('/admin')

@app.post('/admin/payment-ref/<int:id>')
@admin_required
def payment_ref(id):
    ref=request.form.get('payment_ref','').strip(); c=db(); c.execute('update orders set payment_ref=? where id=?',(ref,id)); c.commit(); c.close(); flash('Payment reference saved for manual verification.','success'); return redirect('/admin')

@app.post('/admin/return/<int:id>')
@admin_required
def update_return(id):
    c=db(); c.execute('update returns set status=? where id=?',(request.form.get('status','Requested'),id)); c.commit(); c.close(); return redirect('/admin')

@app.post('/admin/logout')
def admin_logout(): session.clear(); return redirect('/')

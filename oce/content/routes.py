from flask import Blueprint, render_template, send_file, request, jsonify, redirect, url_for, flash, session
from oce.utils.db_interface import create_post, get_post_by_uuid, create_user, get_user_by_email
from oce.utils.models import User
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.consumer.storage.session import BaseStorage
from dotenv import load_dotenv
load_dotenv()
import os
import stripe
import json
import re
from .. import password_hasher

stripe.api_key = ''


#THIS INSURES NO TAMPERING OF PRICES
#SINCE THIS IS IN THE BACKEND IT SHOULD BE SAFE
PRODUCT_CATALOG = {
    1: {'name': 'Bully Booster 1', 'price': 500},
    2: {'name': 'Bully Booster 2', 'price': 500},
    3: {'name': 'Bully Booster 3', 'price': 500},
    4: {'name': 'Bully Booster 4', 'price': 500},
    # Add more products as needed
}

class SessionStorage(BaseStorage):
    def __init__(self, session_key="flask_dance_token"):
        super().__init__()
        self.session_key = session_key

    def get(self, blueprint):
        print("Getting token from session:", session.get(self.session_key))
        return session.get(self.session_key)

    def set(self, blueprint, token):
        print("Setting token in session:", token)
        if isinstance(token, str):  # Handle legacy string just in case
            token = {"access_token": token}
        session[self.session_key] = token

    def delete(self, blueprint):
        print("Deleting token from session")
        session.pop(self.session_key, None)

content = Blueprint('content', __name__)

# ADMINS = os.getenv('ADMINS', '').split(',')
ADMINS = [a for a in os.getenv('ADMINS', '').split(',') if a] + ['admin']


github_blueprint = make_github_blueprint(
    client_id=os.getenv('GITHUB_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_OAUTH_CLIENT_SECRET'),
    scope='user',
    # redirect_to='content.github_callback',
    redirect_url="/github_callback",
    storage=SessionStorage()
)
content.register_blueprint(github_blueprint, url_prefix='/github_login')

#@content.route('/content/SignupPage')
#def signup2():
#  return render_template('SignupPage.html')


@content.route('/content/SignupPage', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        about_me = request.form.get('about_me', '').strip()

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('content.signup'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format.", "danger")
            return redirect(url_for('content.signup'))

        if get_user_by_email(email):
            flash("Email already registered.", "warning")
            return redirect(url_for('content.signup'))

        try:
            create_user(username=username, email=email, password=password, about_me=about_me)
            flash("Signup successful! You can now log in.", "success")
            return redirect(url_for('content.login'))
        except Exception as e:
            print(f"Signup error: {e}")
            flash("An error occurred during signup.", "danger")
            return redirect(url_for('content.signup'))

    return render_template('SignupPage.html')

@content.route('/content/success')
def success():
  return render_template('success.html')

@content.route('/content/block1')
def block1():
  return render_template('block1.html')

@content.route('/content/block2')
def block2():
  return render_template('block2.html')

@content.route('/content/block3')
def block3():
  return render_template('block3.html')

@content.route('/content/block4')
def block4():
  return render_template('block4.html')

@content.route('/content/block5')
def block5():
  return render_template('block5.html')

@content.route('/content/block6')
def block6():
  return render_template('block6.html')

@content.route('/content/block7')
def block7():
  return render_template('block7.html')

@content.route('/content/block8')
def block8():
  return render_template('block8.html')

@content.route('/content/block9')
def block9():
  return render_template('block9.html')

@content.route('/content/tiles/')
def tiles():
    return send_file('static/docs/Human-Domino-Effect-Footprint-Tiles.pdf', download_name='Human-Domino-Effect-Footprint-Tiles.pdf')

from flask import render_template, session
from oce.utils import db_interface

@content.route('/content/ConceptExchange/')
@content.route('/content/ConceptExchange/<group_id>')
def concept_exchange(group_id=None):
    con = db_interface.get_db()
    cur = con.cursor()

    # --- Determine active group ---
    if group_id == "announcement":
        posts = db_interface.get_announcements()
        active_group = "announcement"
        selected_group_name = "Announcements"
    else:
        class_year = None
        if group_id and str(group_id).isdigit():
            class_year = int(group_id)
        elif session.get("selected_class_year"):
            class_year = session["selected_class_year"]

        posts = db_interface.get_posts_for_class(class_year)
        active_group = class_year
        selected_group_name = f"Class of {class_year}" if class_year else "Concept Exchange Chat"

    # --- Sidebar groups ---
    selected_class_year = session.get("selected_class_year")
    groups = [
        {"id": "announcement", "name": "Announcements"}
    ]
    if selected_class_year:
        groups.append({
            "id": selected_class_year,
            "name": f"Class of {selected_class_year}"
        })

    print(f"[DEBUG] Showing {selected_group_name}, active_group={active_group}, posts={len(posts)}")

    return render_template(
        "mainForum.html",
        posts=posts,
        groups=groups,
        show_sidebar=True,
        active_group=active_group,
        selected_group_name=selected_group_name,
    )



# def concept_exchange():
#     posts = db_interface.get_posts_for_class()
#     return render_template(
#         'mainForum.html',
#         posts=posts,
#         show_sidebar=True,
#         active_group='concept_exchange',
#         is_announcement_page=False
#     )


@content.route('/announcements')
def announcements():
    posts = db_interface.get_announcements()
    return render_template(
        'mainForum.html',
        posts=posts,
        show_sidebar=True,
        active_group='announcements',
        is_announcement_page=True
    )

from datetime import datetime
from flask import request, redirect, url_for, flash, session

@content.route('/select_age', methods=['POST'])
def select_age():
    """Handle age selection and redirect to the appropriate Concept Exchange forum."""
    try:
        age = int(request.form.get('age', 0))
        print(f"[DEBUG] Received age from form: {age}")

        # Validate the age
        if age < 0:
            flash("Please select a valid age.", "warning")
            print("[DEBUG] Invalid age submitted — redirecting to resources.")
            return redirect(url_for('content.resources'))

        # Compute "Class of XXXX"
        current_year = datetime.now().year
        class_year = current_year + (18 - age)
        print(f"[DEBUG] Current year: {current_year}, Computed class year: {class_year}")

        # Store both in the Flask session
        session['selected_age'] = age
        session['selected_class_year'] = class_year
        session.modified = True
        print(f"[DEBUG] Session updated: {dict(session)}")

        # Redirect directly to that class group page
        return redirect(url_for('content.concept_exchange', group_id=class_year))

    except Exception as e:
        print(f"[ERROR] Exception in select_age: {e}")
        flash("An error occurred while processing your selection.", "danger")
        return redirect(url_for('content.resources'))


@content.route('/content/resources/', defaults={'selected_age': None})
@content.route('/content/resources/<int:selected_age>')
@content.route('/resources/', defaults={'selected_age': None})
@content.route('/resources/<int:selected_age>')
def resources(selected_age=None):
    # If selected_age is provided (including 0), keep it; otherwise fallback to session or None
    if selected_age is None:
        selected_age = session.get('selected_age')
    # store if not None so templates can use it
    if selected_age is not None:
        session['selected_age'] = selected_age
    return render_template('resources.html', selected_age=selected_age)


# @content.route('/content/resources/<int:selected_age>')
# @content.route('/resources/<int:selected_age>')
# def resources(selected_age):
#     session['selected_age'] = selected_age
#     return render_template('resources.html', selected_age=selected_age)


@content.route('/content/Login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return redirect(url_for('content.login'))

        user = get_user_by_email(email)
        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for('content.login'))

        try:
            password_hasher.verify(user['password'], password)
        except Exception:
            flash("Incorrect password.", "danger")
            return redirect(url_for('content.login'))

        session['user'] = user['username']
        session['user_uuid'] = user['user_uuid']
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for('content.index'))

    return render_template('LoginPage.html')

@content.route('/content/calendar/')
def calendar():
  return render_template('calendar.html')

@content.route('/content/Contact/')
def contact():
  return render_template('ContactPage.html')

@content.route('/content/Shop/')
def shop():
  if 'user_uuid' not in session:
        flash("Please log in to access the shop.", "warning")
        return redirect(url_for('content.login'))
  return render_template('Shop.html')

@content.route('/content/Cart/')
def cart():
  return render_template('Cart.html')

# @content.route('/create_post', methods=['POST'])
# def create_post_route():
#     """
#     Handle AJAX post creation.
#     Uses the class_year stored in session to categorize the post.
#     """

#     try:
#         data = request.get_json()

#         # Extract the post data
#         author = data.get('username', 'Anonymous')
#         text_content = data.get('text_content', '').strip()
#         is_announcement = bool(data.get('is_announcement', False))

#         # Validate text content
#         if not text_content:
#             return jsonify({'success': False, 'error': 'Empty post'}), 400

#         # Log session info for debugging
#         print(f"[DEBUG] Author: {author}, Text: {text_content}, Announcement: {is_announcement}")
#         print(f"[DEBUG] Session class_year: {session.get('selected_class_year')}")

#         # Create post
#         create_post(author, text_content, is_announcement=is_announcement)

#         return jsonify({'success': True}), 200

#     except Exception as e:
#         print(f"[ERROR] Failed to create post: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 500


@content.route('/create_post', methods=['POST'])
def create_post_route():
    """
    Handle AJAX post creation.
    Uses the class_year stored in session to categorize the post.
    """
    try:
        data = request.get_json() or {}
        author = data.get('username', 'Anonymous')
        text_content = data.get('text_content', '').strip()
        is_announcement = bool(data.get('is_announcement', False))

        if not text_content:
            return jsonify({'success': False, 'error': 'Empty post'}), 400

        # If trying to post announcement, require admin
        if is_announcement:
            current_user = session.get('user')
            # ADMINS is global from module environment (string list); ensure same type
            if not current_user or current_user not in ADMINS:
                print(f"[SECURITY] Non-admin {current_user} attempted announcement post.")
                return jsonify({'success': False, 'error': 'Forbidden - admin only'}), 403

        # Create post (db_interface.create_post uses session for class_year when not announcement)
        db_interface.create_post(author, text_content, is_announcement=is_announcement)

        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"[ERROR] Failed to create post: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# @content.route('/create_post', methods=['POST'])
# def create_post_route():
#     data = request.get_json()  # Get JSON data from the request
#     text_content = data.get('text_content')  # Extract the post content
#     username = data.get('username')

#     if not text_content:
#         return jsonify({'success': False, 'error': 'Text content is required.'}), 400

#     try:
#         # create_post(author=User(user_uuid="example", username="name", email="example@email.com", password="password", profile_pic=b"", about_me=''), text_content=text_content, tag1='', tag2='', tag3='', tag4='', tag5='', datetime='', location='', image=None)
#         create_post(author=username, text_content=text_content)  # this should be updated when the user login feature is added to look more like the one above this line
#         return jsonify({'success': True})
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 500
    
@content.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    cart_json = request.form.get('cart')
    cart = json.loads(cart_json)

    line_items = []

    for item in cart:
        product = PRODUCT_CATALOG.get(item['id'])
        if product:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product['name'],
                    },
                    'unit_amount': product['price'],
                },
                'quantity': item['quantity'],
            })

    if not line_items:
        return "Invalid cart", 400

    session = stripe.checkout.Session.create(
        line_items=line_items,
        mode='payment',
        success_url='http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:5000/',
    )
    return redirect(session.url, code=303)
# @content.route('/github_login')
# def github_login():
#     if not github.authorized:
#         print("Client ID:", os.getenv('GITHUB_OAUTH_CLIENT_ID'))
#         print("Client Secret:", os.getenv('GITHUB_OAUTH_CLIENT_SECRET'))
#         auth_url, _ = github.authorization_url("https://github.com/login/oauth/authorize")
#         print("Redirecting to GitHub:",auth_url)
#         return redirect(auth_url)
#     #content.github_login
#     else:
#        account_info = github.get('/user')
#        if account_info.ok:
#           account_info_json = account_info.json()
#           return f'<h1>Your GitHub name is {account_info_json["login"]}</h1>'
#     return'<h1>Request failed!<h1>'

@content.route("/github_login")
def login_github():
    if not github.authorized:
        return redirect(url_for("github.login"))  # this triggers OAuth flow

    resp = github.get("/user")
    if not resp.ok:
        flash("Failed to fetch user info.", "error")
        return redirect(url_for("content.login"))

    username = resp.json()["login"]
    session["user"] = username
    flash(f"Logged in as {username}", "success")

    if username in ADMINS:
        return redirect(url_for("content.admin_dashboard"))

    return redirect(url_for("content.index"))

@content.route("/github_test")
def github_test():
    print("Authorized:", github.authorized)
    print("Token:", github.token)
    return "Check terminal"

# @content.route('/github_callback')
# def github_callback():
    # print("🔄 OAuth callback triggered!")
    # print("📂 Request Args:", request.args)

    # if 'code' not in request.args:
    #     print("❌ No 'code' in request.")
    #     flash("Authorization failed. No code received.", "error")
    #     return redirect(url_for('content.login'))

    # auth_code = request.args['code']
    
    # try:
    #     print("🔄 Exchanging code for token...")
        
    #     # Manually exchange the code for a token
    #     url = "https://github.com/login/oauth/access_token"
    #     data = {
    #         "client_id": os.getenv("GITHUB_CLIENT_ID"),
    #         "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
    #         "code": auth_code,
    #         "redirect_uri": "http://127.0.0.1:5000/github_callback",
    #     }
    #     headers = {"Accept": "application/json"}

    #     response = requests.post(url, json=data, headers=headers)
    #     print("🔄 GitHub Token Exchange Response:", response.text)  # Debug

    #     token_data = response.json()
        
    #     if "access_token" not in token_data:
    #         print("❌ No access_token in response:", token_data)
    #         flash("Authorization failed. No token received.", "error")
    #         return redirect(url_for('content.login'))

    #     session['github_token'] = token_data["access_token"]
    #     print("🟢 Session updated with token:", session['github_token'])

    # except Exception as e:
    #     print("❌ Error during token exchange:", e)
    #     flash("Authorization failed. Token exchange error.", "error")
    #     return redirect(url_for('content.login'))

    # return redirect(url_for('content.index'))
    # print("Callback triggered!")  # Debug print
    # print("Session Data:", session) 
    

    # print("GitHub Token:", session.get("github_oauth_token"))
    # print(github.authorized)
    # if not github.authorized:
    #    print("Failed")
    #    flash("Authorizatiion failed.", "error")
    #    return redirect(url_for('content.login'))
    
    # account_info = github.get('/user')
    # if account_info.ok:
    #    account_info_json = account_info.json()
    #    username = account_info_json['login']
    #    print(f"Logged in as {username}") 

    #    session['user'] = username
    #    flash(f"Logged in as {username}" , "success")

    #    if username in ADMINS:
    #       return redirect(url_for('content.admin_dashboard'))
       
    #    return redirect(url_for('content.index'))
    # flash("Failed to fetch user info.", "error")
    # return redirect(url_for('content.index'))

@content.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['user'] not in ADMINS:
       return "Unauthorized", 403
    return render_template('admin_dashboard.html')

@content.route('/logout')
def logout():
    session.pop('user', None)
    github.logout()
    flash("You have been logged out.", "success")
    return redirect(url_for('content.index'))

@content.route('/')
def index():
    return render_template('index.html')



import streamlit as st
from datetime import datetime
from PIL import Image
import pandas as pd
from rapidfuzz import fuzz
import random

st.markdown("""
    <style>
    .main {
        background-color: #000000;
        color: #FFFFFF;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #000000;
        color: #FFFFFF;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #333333;
    }
    .stDataFrame {
        color: #000000;
    }
    .title {
        font-size: 50px;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

def load_logo():
    try:
        return Image.open("logo2.png.webp")
    except FileNotFoundError:
        st.warning("Logo file not found. Please ensure 'logo2.png.webp' is in the same directory as the script.")
        return None

def login_user(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    return False

def signup_user(username, password, confirm_password):
    if password != confirm_password:
        st.error("Passwords do not match.")
        return False
    if username in st.session_state.users:
        st.error("Username already exists.")
        return False
    st.session_state.users[username] = password
    st.success("Signup successful. Please log in.")
    return True

def logout_user():
    st.session_state.authenticated = False
    st.session_state.username = ''

def show_login_signup():
    st.markdown("<h2 style='color: #FFFFFF;'>Login / Sign Up</h2>", unsafe_allow_html=True)
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
    
    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_user(username, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with signup_tab:
        new_username = st.text_input("New Username", key="signup_username")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        if st.button("Sign Up"):
            signup_user(new_username, new_password, confirm_password)

def add_food_items(new_items):
    food_items = st.session_state.get(f'food_items_{st.session_state.username}', [])
    for item in new_items:
        if item['name'].strip() and item['expiry_date']:
            if not any(existing_item['name'] == item['name'] and existing_item['expiry_date'] == item['expiry_date'] for existing_item in food_items):
                food_items.append(item)
            else:
                st.warning(f"Item '{item['name']}' with the same expiry date already exists.")
      
    st.session_state[f' food_items_{st.session_state.username}'] = food_items

def check_expiry(expiry_date):
    today = datetime.now().date()
    days_until_expiry = (expiry_date - today).days
    return days_until_expiry

def clear_items():
    if f'food_items_{st.session_state.username}' in st.session_state:
        st.session_state[f'food_items_{st.session_state.username}'] = []
        st.success("All items have been cleared from the inventory.")
    else:
        st.warning("No items to clear.")

def delete_food_item(item_name, expiry_date):
    food_items = st.session_state.get(f'food_items_{st.session_state.username}', [])
    food_items = [item for item in food_items if not (item['name'] == item_name)]
    st.session_state[f'food_items_{st.session_state.username}'] = food_items
    st.success(f"Item '{item_name}' has been deleted from the inventory.")

def add_items_tab():
    st.markdown("<h2 style='color: #FFFFFF;'>Add New Items</h2>", unsafe_allow_html=True)
    with st.form("add_food_items_form"):
        num_items = st.number_input("Number of items to add", min_value=1, max_value=10, value=1)
        new_items = []
        for i in range(int(num_items)):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(f"Food Item Name {i+1}", key=f"item_name_{i}")
            with col2:
                expiry_date = st.date_input(f"Expiry Date {i+1}", min_value=datetime.now().date(), key=f"item_expiry_{i}")
            
            if name.strip():
                new_items.append({"name": name, "expiry_date": expiry_date})
            else:
                st.warning(f"Item Name {i+1} cannot be empty. Please enter a valid name.")

        submitted = st.form_submit_button("Add Items")
        if submitted:
            if new_items:
                add_food_items(new_items)
                st.success("Food items added successfully! Time to keep your kitchen organized!")
            else:
                st.warning("No valid items to add. Please ensure all item names are filled in.")

def add_food_items(new_items):
    # Correct the session state key by removing the leading space
    food_items = st.session_state.get(f'food_items_{st.session_state.username}', [])
    for item in new_items:
        if item['name'].strip() and item['expiry_date']:
            if not any(existing_item['name'] == item['name'] and existing_item['expiry_date'] == item['expiry_date'] for existing_item in food_items):
                food_items.append(item)
            else:
                st.warning(f"Item '{item['name']}' with the same expiry date already exists.")
      
    # Correct the session state key by removing the leading space
    st.session_state[f'food_items_{st.session_state.username}'] = food_items

def inventory_tab():
    st.markdown("<h2 style='color: #FFFFFF;'>Food Inventory</h2>", unsafe_allow_html=True)
    # Ensure the retrieval of food items is correct
    items = st.session_state.get(f'food_items_{st.session_state.username}', [])
    
    if items:
        search_term = st.text_input("Search for an item", "")
        filtered_items = [item for item in items if search_term.lower() in item['name'].lower()]
        
        sort_option = st.selectbox("Sort by", ["Name", "Expiry Date"])
        if sort_option == "Name":
            filtered_items.sort(key=lambda x: x['name'].lower())
        else:
            filtered_items.sort(key=lambda x: x['expiry_date'])
        
        data = [{"Name": item["name"], "Expiry Date": item["expiry_date"].strftime("%Y-%m-%d"), "Days Until Expiry": check_expiry(item["expiry_date"])} for item in filtered_items]
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        for item in filtered_items:
            st.write("*" , "**Double click to delete items in the Food inventory**")
            if st.button(f"Delete {item['name']} (Expires on {item['expiry_date'].strftime('%Y-%m-%d')})"):
                delete_food_item(item['name'], item['expiry_date'])
        
    else:
        st.info("No food items added yet.")

def alerts_tab():
    st.markdown("<h2 style='color: #FFFFFF;'>Expiry Alerts</h2>", unsafe_allow_html=True)
    items = st.session_state.get(f'food_items_{st.session_state.username}', [])
    alerts = [(item, check_expiry(item["expiry_date"])) for item in items]
    
    if alerts:
        for item, days_left in alerts:
            if days_left < 0:
                st.markdown(f"<div style='background-color: #FFB3BA; padding: 10px; border-radius: 5px; color: #000000;'>🚨 <b>{item['name']}</b> has expired!</div>", unsafe_allow_html=True)
            elif days_left == 0:
                st.markdown(f"<div style='background-color: #FFDFBA; padding: 10px; border-radius: 5px; color: #000000;'>🚨 <b>{item['name']}</b> expires today!</div>", unsafe_allow_html=True)
            elif days_left == 1:
                st.markdown(f"<div style=' background-color: #FFFFBA; padding: 10px; border-radius: 5px; color: #000000;'>⚠️ <b>{item['name']}</b> expires in 1 day!</div>", unsafe_allow_html=True)
            elif days_left <= 5:
                st.markdown(f"<div style='background-color: #BAFFC9; padding: 10px; border-radius: 5px; color: #000000;'>⚠️ <b>{item['name']}</b> expires in {days_left} days!</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color: #BAE1FF; padding: 10px; border-radius: 5px; color: #000000;'>✅ <b>{item['name']}</b> expires in {days_left} days.</div>", unsafe_allow_html=True)
    else:
        st.success("✅ No items added yet.")

def get_near_expiry_items():
    items = st.session_state.get(f'food_items_{st.session_state.username}', [])
    near_expiry = [item for item in items if check_expiry(item["expiry_date"]) <= 5]
    return near_expiry

def get_recipe_suggestions(ingredients):
    mock_recipes =[
        {"name": "Pasta Primavera", "ingredients": ["pasta", "vegetables", "olive oil"], "instructions": "Cook pasta, sauté vegetables, mix together.", "nutrition": {"calories": 300, "protein": 10, "fat": 5, "carbohydrates": 50}},
        {"name": "Vegetable Stir Fry", "ingredients": ["vegetables", "soy sauce", "rice"], "instructions": "Stir fry vegetables, add soy sauce, serve with rice.", "nutrition": {"calories": 250, "protein": 8, "fat": 3, "carbohydrates": 45}},
        {"name": "Chicken Caesar Salad", "ingredients": ["chicken breast", "romaine lettuce", "croutons", "Caesar dressing"], "instructions": "Grill chicken, chop lettuce, toss with croutons and Caesar dressing.", "nutrition": {"calories": 350, "protein": 30, "fat": 15, "carbohydrates": 20}},
        {"name": "Tomato Basil Soup", "ingredients": ["tomatoes", "basil", "cream", "vegetable broth"], "instructions": "Simmer tomatoes with broth, blend with basil and cream.", "nutrition": {"calories": 200, "protein": 5, "fat": 10, "carbohydrates": 20}},
        {"name": "Grilled Salmon", "ingredients": ["salmon fillet", "lemon", "garlic", "olive oil"], "instructions": "Marinate salmon, grill until cooked, serve with lemon.", "nutrition": {"calories": 400, "protein": 35, "fat": 20, "carbohydrates": 5}},
        {"name": "Veggie Wrap", "ingredients": ["tortilla", "hummus", "mixed vegetables", "spinach"], "instructions": "Spread hummus on tortilla, add vegetables and spinach, roll up.", "nutrition": {"calories": 300, "protein": 8, "fat": 10, "carbohydrates": 40}},
        {"name": "Quinoa Salad", "ingredients": ["quinoa", "cucumber", "tomatoes", "feta cheese", "olive oil"], "instructions": "Cook quinoa, mix with chopped vegetables, add feta and olive oil.", "nutrition": {"calories": 350, "protein": 12, "fat": 15, "carbohydrates": 35}},
        {"name": "Banana Smoothie", "ingredients": ["banana", "milk", "honey", "ice"], "instructions": "Blend all ingredients until smooth.", "nutrition": {"calories": 200, "protein": 6, "fat": 2, "carbohydrates": 40}},
        {"name": "Turkey Sandwich", "ingredients": ["whole-grain bread", "turkey slices", "lettuce", "tomato", "mayonnaise"], "instructions": "Assemble sandwich with turkey, lettuce, tomato, and mayonnaise.", "nutrition": {"calories": 320, "protein": 20, "fat": 10, "carbohydrates": 40}},
        {"name": "Lentil Soup", "ingredients": ["lentils", "carrots", "onion", "garlic", "vegetable broth"], "instructions": "Simmer lentils with vegetables and broth until tender.", "nutrition": {"calories": 250, "protein": 12, "fat": 3, "carbohydrates": 40}},
        {"name": "Avocado Toast", "ingredients": ["whole-grain bread", "avocado", "lemon juice"], "instructions": "Toast bread, mash avocado with lemon juice, spread on toast.", "nutrition": {"calories": 250, "protein": 5, "fat": 15, "carbohydrates": 25}},
        {"name": "Berry Parfait", "ingredients": ["yogurt", "berries", "granola"], "instructions": "Layer yogurt, berries, and granola in a glass.", "nutrition": {"calories": 200, "protein": 8, "fat": 4, "carbohydrates": 30}},
        {"name": "Stuffed Bell Peppers", "ingredients": ["bell peppers", "rice", "ground beef", "tomato sauce"], "instructions": "Stuff bell peppers with a mixture of rice, ground beef, and tomato sauce, then bake.", "nutrition": {"calories": 400, "protein": 25, "fat": 15, "carbohydrates": 50}},
        {"name": "Shrimp Tacos", "ingredients": ["shrimp", "tortillas", "cabbage", "lime"], "instructions": "Cook shrimp, serve in tortillas with cabbage and lime.", "nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbohydrates": 30}},
        {"name": "Chickpea Salad", "ingredients": ["chickpeas", "cucumber", "tomatoes", "feta cheese", "olive oil"], "instructions": "Mix chickpeas with chopped vegetables and feta, drizzle with olive oil.", "nutrition": {"calories": 250, "protein": 10, "fat": 12, "carbohydrates": 30}},
        {"name": "Beef Stir Fry", "ingredients": ["beef", "broccoli", "soy sauce", "rice"], "instructions": "Stir fry beef and broccoli, serve with rice and soy sauce.", "nutrition": {"calories": 450, "protein": 30, "fat": 20, "carbohydrates": 40}},
        {"name": "Mushroom Risotto", "ingredients": ["arborio rice", "mushrooms", "broth", "parmesan cheese"], "instructions": "Cook arborio rice slowly with broth, add mushrooms and parmesan.", "nutrition": {"calories": 350, "protein": 10, "fat": 8, "carbohydrates": 60}}
    ]
    
    
    suggested_recipes = []
    for recipe in mock_recipes:
        matching_ingredients = sum(
            fuzz.partial_ratio(ingredient.lower(), recipe_ing.lower()) > 80 
            for ingredient in ingredients 
            for recipe_ing in recipe["ingredients"]
        )
        if matching_ingredients > 0:
            suggested_recipes.append((recipe, matching_ingredients))
    
    suggested_recipes.sort(key=lambda x: x[1], reverse=True)
    
    return [recipe for recipe, _ in suggested_recipes]

def magic_recipes_tab():
    st.markdown("<h2 style='color: #FFFFFF;'>Magic Recipes</h2>", unsafe_allow_html=True)
    near_expiry_items = get_near_expiry_items()
    
    if not near_expiry_items:
        st.info("No items are near expiry. Add more items or check back later!")
        return
    
    st.write("Select items to include in recipe suggestions:")
    selected_items = [item for item in near_expiry_items if st.checkbox(f"{item['name']} (Expires in {check_expiry(item['expiry_date'])} days)", key=f"checkbox_{item['name']}")]
    
    if selected_items:
        st.write("Selected items:", ", ".join([f"{item['name']}" for item in selected_items]))
        recipes = get_recipe_suggestions([item['name'] for item in selected_items])
        if recipes:
            st.subheader("Suggested Recipes:")
            for i, recipe in enumerate(recipes):
                with st.expander(f"**{recipe['name']}**"):
                    st.write("**Ingredients:**")
                    st.write(", ".join([f"{ing}" for ing in recipe['ingredients']]))
                    st.write("**Instructions:**")
                    st.write(recipe['instructions'])
                    
                    # Display nutritional information
                    nutrition = recipe.get("nutrition", {})
                    st.write("**Nutritional Information:**")
                    st.write(f"Calories: {nutrition.get('calories', 'N/A')} kcal")
                    st.write(f"Protein: {nutrition.get('protein', 'N/A')} g")
                    st.write(f"Fat: {nutrition.get('fat', 'N/A')} g")
                    st.write(f"Carbohydrates: {nutrition.get('carbohydrates', 'N/A')} g")
                    
                    matching = [ing for ing in recipe['ingredients'] if ing.lower() in [item['name'].lower() for item in selected_items]]
                    if matching:
                        st.write("**Matching ingredients:**", ", ".join([f"{ing}" for ing in matching]))
                    
                    # User feedback section
                    feedback_key = f"feedback_{recipe['name']}"
                    feedback = st.text_area(f"Leave feedback for {recipe['name']}", key=feedback_key)
                    if st.button ("Submit Feedback", key=f"submit_{recipe['name']}"):
                        if feedback:
                            st.session_state.feedback[recipe['name']] = feedback
                            st.success("Feedback submitted!")
                        else:
                            st.warning("Please enter feedback before submitting.")
        else:
            st.warning("No recipes found for the selected items. Try selecting different items.")
    else:
        st.info("Select items to get recipe suggestions.")

def get_daily_tagline():
    taglines = [
        "Freshness First: Track, Save, Enjoy!",
        "Keep Your Kitchen Fresh and Organized!",
        "Never Let Your Food Go to Waste!",
        "Track Expiry Dates with Ease!",
        "Stay Fresh, Stay Healthy!",
        "Your Personal Food Inventory Manager!",
        "Smart Tracking for Smart Kitchens!",
        "Say Goodbye to Food Waste!",
        "Fresh Food, Happy Life!",
        "Organize Your Pantry Like a Pro!"
    ]
    random.seed(datetime.now().date().toordinal())
    return random.choice(taglines)

def main():
    logo = load_logo()
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if logo:
            st.image(logo, width=100)
    with col2:
        st.markdown("<h1 class='title'>ExpirySense</h1>", unsafe_allow_html=True)
    
    tagline = get_daily_tagline()
    st.markdown(f"<p style='font-size: 20px; color: #FFFFFF;'>{tagline}</p>", unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        show_login_signup()
    else:
        st.write(f"Welcome, {st.session_state.username}!")
        if st.button("Logout"):
            logout_user()
            st.rerun()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Add Items", "📊 Food Inventory", "🚨 Expiry Alerts", "🍳 Magic Recipes"])

        with tab1:
            add_items_tab()

        with tab2:
            inventory_tab()

        with tab3:
            alerts_tab()

        with tab4:
            magic_recipes_tab()

if __name__ == "__main__":
    main()
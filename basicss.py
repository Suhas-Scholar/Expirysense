"""
ExpirySense - Professional Food Inventory Management System
A comprehensive application for tracking food expiry dates and reducing waste
"""

import streamlit as st
from datetime import datetime, date
from PIL import Image
import pandas as pd
from rapidfuzz import fuzz
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json

# ========================= DATA MODELS =========================

@dataclass
class FoodItem:
    """Data model for food items"""
    name: str
    expiry_date: date
    added_date: date = None
    category: str = "Other"
    
    def __post_init__(self):
        if self.added_date is None:
            self.added_date = datetime.now().date()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'expiry_date': self.expiry_date,
            'added_date': self.added_date,
            'category': self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FoodItem':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            expiry_date=data['expiry_date'],
            added_date=data.get('added_date'),
            category=data.get('category', 'Other')
        )

@dataclass
class Recipe:
    """Data model for recipes"""
    name: str
    ingredients: List[str]
    instructions: str
    nutrition: Dict[str, int]
    prep_time: str = "30 mins"
    difficulty: str = "Medium"
    
    def matches_ingredients(self, available_ingredients: List[str]) -> int:
        """Calculate how many ingredients match"""
        matching_count = sum(
            fuzz.partial_ratio(ingredient.lower(), recipe_ing.lower()) > 80 
            for ingredient in available_ingredients 
            for recipe_ing in self.ingredients
        )
        return matching_count


# ========================= CONSTANTS =========================

FOOD_CATEGORIES = [
    "Dairy", "Vegetables", "Fruits", "Meat", "Seafood", 
    "Grains", "Bakery", "Beverages", "Condiments", "Other"
]

DAILY_TAGLINES = [
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

MOCK_RECIPES = [
    Recipe(
        name="Pasta Primavera",
        ingredients=["pasta", "vegetables", "olive oil", "garlic", "parmesan"],
        instructions="1. Boil pasta according to package directions.\n2. Sauté vegetables in olive oil with garlic.\n3. Toss pasta with vegetables and top with parmesan.",
        nutrition={"calories": 300, "protein": 10, "fat": 5, "carbohydrates": 50},
        prep_time="25 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Vegetable Stir Fry",
        ingredients=["vegetables", "soy sauce", "rice", "ginger", "garlic"],
        instructions="1. Cook rice.\n2. Stir fry vegetables with ginger and garlic.\n3. Add soy sauce and serve over rice.",
        nutrition={"calories": 250, "protein": 8, "fat": 3, "carbohydrates": 45},
        prep_time="20 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Chicken Caesar Salad",
        ingredients=["chicken breast", "romaine lettuce", "croutons", "caesar dressing", "parmesan"],
        instructions="1. Grill chicken breast until cooked through.\n2. Chop romaine lettuce.\n3. Toss with croutons, Caesar dressing, and sliced chicken.\n4. Top with parmesan.",
        nutrition={"calories": 350, "protein": 30, "fat": 15, "carbohydrates": 20},
        prep_time="30 mins",
        difficulty="Medium"
    ),
    Recipe(
        name="Tomato Basil Soup",
        ingredients=["tomatoes", "basil", "cream", "vegetable broth", "onion"],
        instructions="1. Sauté onions until soft.\n2. Add tomatoes and broth, simmer for 20 mins.\n3. Blend until smooth.\n4. Stir in cream and fresh basil.",
        nutrition={"calories": 200, "protein": 5, "fat": 10, "carbohydrates": 20},
        prep_time="35 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Grilled Salmon",
        ingredients=["salmon fillet", "lemon", "garlic", "olive oil", "herbs"],
        instructions="1. Marinate salmon with olive oil, garlic, and herbs.\n2. Grill for 4-5 minutes per side.\n3. Serve with lemon wedges.",
        nutrition={"calories": 400, "protein": 35, "fat": 20, "carbohydrates": 5},
        prep_time="20 mins",
        difficulty="Medium"
    ),
    Recipe(
        name="Veggie Wrap",
        ingredients=["tortilla", "hummus", "mixed vegetables", "spinach", "feta"],
        instructions="1. Spread hummus on tortilla.\n2. Layer with spinach, mixed vegetables, and feta.\n3. Roll tightly and cut in half.",
        nutrition={"calories": 300, "protein": 8, "fat": 10, "carbohydrates": 40},
        prep_time="10 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Quinoa Salad",
        ingredients=["quinoa", "cucumber", "tomatoes", "feta cheese", "olive oil", "lemon"],
        instructions="1. Cook quinoa and let cool.\n2. Chop vegetables.\n3. Mix quinoa with vegetables, feta, olive oil, and lemon juice.",
        nutrition={"calories": 350, "protein": 12, "fat": 15, "carbohydrates": 35},
        prep_time="25 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Banana Smoothie",
        ingredients=["banana", "milk", "honey", "ice", "vanilla"],
        instructions="1. Combine all ingredients in blender.\n2. Blend until smooth and creamy.\n3. Serve immediately.",
        nutrition={"calories": 200, "protein": 6, "fat": 2, "carbohydrates": 40},
        prep_time="5 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Turkey Sandwich",
        ingredients=["whole-grain bread", "turkey slices", "lettuce", "tomato", "mayonnaise", "cheese"],
        instructions="1. Toast bread if desired.\n2. Layer turkey, lettuce, tomato, and cheese.\n3. Spread mayonnaise and close sandwich.",
        nutrition={"calories": 320, "protein": 20, "fat": 10, "carbohydrates": 40},
        prep_time="10 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Lentil Soup",
        ingredients=["lentils", "carrots", "onion", "garlic", "vegetable broth", "cumin"],
        instructions="1. Sauté onion, garlic, and carrots.\n2. Add lentils, broth, and cumin.\n3. Simmer until lentils are tender (30-40 mins).",
        nutrition={"calories": 250, "protein": 12, "fat": 3, "carbohydrates": 40},
        prep_time="45 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Avocado Toast",
        ingredients=["whole-grain bread", "avocado", "lemon juice", "salt", "pepper"],
        instructions="1. Toast bread until golden.\n2. Mash avocado with lemon juice, salt, and pepper.\n3. Spread generously on toast.",
        nutrition={"calories": 250, "protein": 5, "fat": 15, "carbohydrates": 25},
        prep_time="5 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Berry Parfait",
        ingredients=["yogurt", "berries", "granola", "honey"],
        instructions="1. Layer yogurt in a glass.\n2. Add berries and granola.\n3. Repeat layers and drizzle with honey.",
        nutrition={"calories": 200, "protein": 8, "fat": 4, "carbohydrates": 30},
        prep_time="5 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Stuffed Bell Peppers",
        ingredients=["bell peppers", "rice", "ground beef", "tomato sauce", "cheese"],
        instructions="1. Cook rice and brown ground beef.\n2. Mix with tomato sauce.\n3. Stuff peppers and bake at 375°F for 30 mins.\n4. Top with cheese and bake 5 more mins.",
        nutrition={"calories": 400, "protein": 25, "fat": 15, "carbohydrates": 50},
        prep_time="50 mins",
        difficulty="Medium"
    ),
    Recipe(
        name="Shrimp Tacos",
        ingredients=["shrimp", "tortillas", "cabbage", "lime", "cilantro", "avocado"],
        instructions="1. Season and cook shrimp.\n2. Warm tortillas.\n3. Fill with shrimp, cabbage, and avocado.\n4. Top with cilantro and lime juice.",
        nutrition={"calories": 300, "protein": 20, "fat": 10, "carbohydrates": 30},
        prep_time="20 mins",
        difficulty="Medium"
    ),
    Recipe(
        name="Chickpea Salad",
        ingredients=["chickpeas", "cucumber", "tomatoes", "feta cheese", "olive oil", "lemon"],
        instructions="1. Drain and rinse chickpeas.\n2. Chop vegetables.\n3. Mix all ingredients with olive oil and lemon juice.",
        nutrition={"calories": 250, "protein": 10, "fat": 12, "carbohydrates": 30},
        prep_time="15 mins",
        difficulty="Easy"
    ),
    Recipe(
        name="Beef Stir Fry",
        ingredients=["beef", "broccoli", "soy sauce", "rice", "ginger", "garlic"],
        instructions="1. Cook rice.\n2. Stir fry beef with ginger and garlic.\n3. Add broccoli and soy sauce.\n4. Serve over rice.",
        nutrition={"calories": 450, "protein": 30, "fat": 20, "carbohydrates": 40},
        prep_time="25 mins",
        difficulty="Medium"
    ),
    Recipe(
        name="Mushroom Risotto",
        ingredients=["arborio rice", "mushrooms", "broth", "parmesan cheese", "white wine", "onion"],
        instructions="1. Sauté onion and mushrooms.\n2. Add rice and toast lightly.\n3. Gradually add warm broth, stirring constantly.\n4. Finish with parmesan and white wine.",
        nutrition={"calories": 350, "protein": 10, "fat": 8, "carbohydrates": 60},
        prep_time="40 mins",
        difficulty="Hard"
    )
]


# ========================= STYLING =========================

def apply_custom_styles():
    """Apply custom CSS styles to the application"""
    st.markdown("""
        <style>
        /* Main container styles */
        .main {
            background-color: #000000;
            color: #FFFFFF;
        }
        
        .stApp {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Tab styles */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            background-color: #0a0a0a;
            padding: 10px;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #1a1a1a;
            color: #FFFFFF;
            border-radius: 8px;
            gap: 1px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #333333;
            border-bottom: 3px solid #4ECDC4;
        }
        
        /* Title styles */
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
        
        /* Card styles */
        .info-card {
            background-color: #1a1a1a;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #4ECDC4;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .stat-card {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        
        /* Button styles */
        .stButton > button {
            background-color: #4ECDC4;
            color: #000000;
            font-weight: 600;
            border-radius: 8px;
            padding: 10px 24px;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #3DBDB3;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(78, 205, 196, 0.3);
        }
        
        /* Input styles */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stDateInput > div > div > input {
            background-color: #1a1a1a;
            color: #FFFFFF;
            border: 1px solid #333;
            border-radius: 8px;
        }
        
        /* Expander styles */
        .streamlit-expanderHeader {
            background-color: #1a1a1a;
            border-radius: 8px;
            color: #FFFFFF;
        }
        
        /* Alert styles */
        .alert-expired {
            background-color: #FFB3BA;
            padding: 15px;
            border-radius: 10px;
            color: #000000;
            margin: 10px 0;
            border-left: 5px solid #FF0000;
        }
        
        .alert-warning {
            background-color: #FFDFBA;
            padding: 15px;
            border-radius: 10px;
            color: #000000;
            margin: 10px 0;
            border-left: 5px solid #FFA500;
        }
        
        .alert-info {
            background-color: #BAE1FF;
            padding: 15px;
            border-radius: 10px;
            color: #000000;
            margin: 10px 0;
            border-left: 5px solid #0080FF;
        }
        
        /* DataFrame styles */
        .dataframe {
            background-color: #1a1a1a !important;
        }
        
        /* Success message */
        .success-message {
            background-color: #BAFFC9;
            padding: 15px;
            border-radius: 10px;
            color: #000000;
            border-left: 5px solid #00FF00;
        }
        </style>
        """, unsafe_allow_html=True)


# ========================= SESSION STATE MANAGEMENT =========================

class SessionManager:
    """Manage session state variables"""
    
    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        defaults = {
            'authenticated': False,
            'username': '',
            'users': {},
            'feedback': {},
            'last_login': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def get_user_items_key(username: str) -> str:
        """Get the session state key for user's food items"""
        return f'food_items_{username}'
    
    @staticmethod
    def get_user_items(username: str) -> List[Dict]:
        """Get food items for a specific user"""
        key = SessionManager.get_user_items_key(username)
        return st.session_state.get(key, [])
    
    @staticmethod
    def set_user_items(username: str, items: List[Dict]):
        """Set food items for a specific user"""
        key = SessionManager.get_user_items_key(username)
        st.session_state[key] = items


# ========================= AUTHENTICATION =========================

class AuthenticationManager:
    """Handle user authentication"""
    
    @staticmethod
    def login(username: str, password: str) -> bool:
        """Authenticate user login"""
        if not username or not password:
            st.error("Username and password are required.")
            return False
        
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.last_login = datetime.now()
            return True
        return False
    
    @staticmethod
    def signup(username: str, password: str, confirm_password: str) -> bool:
        """Register new user"""
        if not username or not password:
            st.error("Username and password are required.")
            return False
        
        if len(password) < 6:
            st.error("Password must be at least 6 characters long.")
            return False
        
        if password != confirm_password:
            st.error("Passwords do not match.")
            return False
        
        if username in st.session_state.users:
            st.error("Username already exists. Please choose a different username.")
            return False
        
        st.session_state.users[username] = password
        st.success("✅ Signup successful! Please log in with your credentials.")
        return True
    
    @staticmethod
    def logout():
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.username = ''
        st.session_state.last_login = None


# ========================= INVENTORY MANAGEMENT =========================

class InventoryManager:
    """Manage food inventory operations"""
    
    @staticmethod
    def add_items(username: str, new_items: List[Dict]) -> Tuple[int, int]:
        """
        Add new food items to inventory
        Returns: (added_count, skipped_count)
        """
        food_items = SessionManager.get_user_items(username)
        added_count = 0
        skipped_count = 0
        
        for item in new_items:
            if not item['name'].strip():
                skipped_count += 1
                continue
            
            # Check for duplicates
            is_duplicate = any(
                existing_item['name'].lower() == item['name'].lower() and 
                existing_item['expiry_date'] == item['expiry_date']
                for existing_item in food_items
            )
            
            if is_duplicate:
                st.warning(f"⚠️ Item '{item['name']}' with the same expiry date already exists.")
                skipped_count += 1
            else:
                food_items.append(item)
                added_count += 1
        
        SessionManager.set_user_items(username, food_items)
        return added_count, skipped_count
    
    @staticmethod
    def delete_item(username: str, item_name: str) -> bool:
        """Delete a food item from inventory"""
        food_items = SessionManager.get_user_items(username)
        original_count = len(food_items)
        
        food_items = [item for item in food_items if item['name'] != item_name]
        SessionManager.set_user_items(username, food_items)
        
        return len(food_items) < original_count
    
    @staticmethod
    def clear_all(username: str):
        """Clear all items from inventory"""
        SessionManager.set_user_items(username, [])
    
    @staticmethod
    def get_statistics(username: str) -> Dict:
        """Get inventory statistics"""
        items = SessionManager.get_user_items(username)
        
        if not items:
            return {
                'total_items': 0,
                'expired_count': 0,
                'expiring_soon': 0,
                'fresh_items': 0
            }
        
        today = datetime.now().date()
        expired = sum(1 for item in items if item['expiry_date'] < today)
        expiring_soon = sum(1 for item in items if 0 <= (item['expiry_date'] - today).days <= 5)
        fresh = len(items) - expired - expiring_soon
        
        return {
            'total_items': len(items),
            'expired_count': expired,
            'expiring_soon': expiring_soon,
            'fresh_items': fresh
        }


# ========================= EXPIRY UTILITIES =========================

class ExpiryChecker:
    """Handle expiry date calculations"""
    
    @staticmethod
    def calculate_days_until_expiry(expiry_date: date) -> int:
        """Calculate days until expiry"""
        today = datetime.now().date()
        return (expiry_date - today).days
    
    @staticmethod
    def get_expiry_status(days_until_expiry: int) -> str:
        """Get expiry status category"""
        if days_until_expiry < 0:
            return "expired"
        elif days_until_expiry == 0:
            return "expires_today"
        elif days_until_expiry <= 3:
            return "critical"
        elif days_until_expiry <= 7:
            return "warning"
        else:
            return "fresh"
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Get color for status"""
        colors = {
            "expired": "#FFB3BA",
            "expires_today": "#FFDFBA",
            "critical": "#FFFFBA",
            "warning": "#BAFFC9",
            "fresh": "#BAE1FF"
        }
        return colors.get(status, "#FFFFFF")
    
    @staticmethod
    def get_status_icon(status: str) -> str:
        """Get icon for status"""
        icons = {
            "expired": "🚨",
            "expires_today": "⚠️",
            "critical": "⏰",
            "warning": "📌",
            "fresh": "✅"
        }
        return icons.get(status, "ℹ️")


# ========================= RECIPE SYSTEM =========================

class RecipeEngine:
    """Handle recipe suggestions"""
    
    @staticmethod
    def get_matching_recipes(ingredients: List[str], limit: int = 10) -> List[Tuple[Recipe, int]]:
        """
        Get recipes matching the given ingredients
        Returns: List of (Recipe, match_count) tuples sorted by relevance
        """
        suggested_recipes = []
        
        for recipe in MOCK_RECIPES:
            match_count = recipe.matches_ingredients(ingredients)
            if match_count > 0:
                suggested_recipes.append((recipe, match_count))
        
        # Sort by match count (descending)
        suggested_recipes.sort(key=lambda x: x[1], reverse=True)
        
        return suggested_recipes[:limit]
    
    @staticmethod
    def format_recipe_card(recipe: Recipe, matching_ingredients: List[str]) -> str:
        """Format recipe information as HTML"""
        matched = [ing for ing in recipe.ingredients 
                  if ing.lower() in [item.lower() for item in matching_ingredients]]
        
        nutrition_html = f"""
        <div style='background-color: #1a1a1a; padding: 10px; border-radius: 5px; margin: 10px 0;'>
            <strong>Nutritional Information (per serving):</strong><br>
            🔥 Calories: {recipe.nutrition.get('calories', 'N/A')} kcal<br>
            💪 Protein: {recipe.nutrition.get('protein', 'N/A')} g<br>
            🥑 Fat: {recipe.nutrition.get('fat', 'N/A')} g<br>
            🌾 Carbs: {recipe.nutrition.get('carbohydrates', 'N/A')} g
        </div>
        """
        
        return nutrition_html


# ========================= UI COMPONENTS =========================

def render_header():
    """Render application header with logo and title"""
    try:
        logo = Image.open("logo2.png.webp")
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(logo, width=120)
        with col2:
            st.markdown("<h1 class='title'>ExpirySense</h1>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("<h1 class='title'>ExpirySense</h1>", unsafe_allow_html=True)
        st.caption("ℹ️ Logo file not found. Place 'logo2.png.webp' in the app directory.")
    
    # Display daily tagline
    random.seed(datetime.now().date().toordinal())
    tagline = random.choice(DAILY_TAGLINES)
    st.markdown(f"<p style='font-size: 22px; color: #4ECDC4; text-align: center; font-weight: 500;'>💡 {tagline}</p>", unsafe_allow_html=True)


def render_statistics_dashboard(username: str):
    """Render statistics dashboard"""
    stats = InventoryManager.get_statistics(username)
    
    st.markdown("### 📊 Inventory Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <h2 style='color: #4ECDC4;'>{stats['total_items']}</h2>
            <p>Total Items</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <h2 style='color: #FF6B6B;'>{stats['expired_count']}</h2>
            <p>Expired</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <h2 style='color: #FFD93D;'>{stats['expiring_soon']}</h2>
            <p>Expiring Soon</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <h2 style='color: #6BCB77;'>{stats['fresh_items']}</h2>
            <p>Fresh Items</p>
        </div>
        """, unsafe_allow_html=True)


def render_login_page():
    """Render login and signup interface"""
    st.markdown("<h2 style='color: #4ECDC4; text-align: center;'>🔐 Welcome to ExpirySense</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #CCCCCC;'>Please login or create a new account to continue</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### Login to Your Account")
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if AuthenticationManager.login(username, password):
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please try again.")
    
    with tab2:
        with st.form("signup_form", clear_on_submit=True):
            st.markdown("#### Create New Account")
            new_username = st.text_input("Username", placeholder="Choose a username", key="signup_username")
            new_password = st.text_input("Password", type="password", placeholder="Choose a password (min 6 characters)", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="confirm_password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                AuthenticationManager.signup(new_username, new_password, confirm_password)


def render_add_items_tab(username: str):
    """Render add items tab"""
    st.markdown("<h2 style='color: #4ECDC4;'>➕ Add New Items</h2>", unsafe_allow_html=True)
    
    st.info("💡 **Tip:** Add items as soon as you purchase them to track their freshness effectively!")
    
    # Number of items selector (outside form for immediate response)
    num_items = st.number_input(
        "How many items would you like to add?", 
        min_value=1, 
        max_value=10, 
        value=1, 
        step=1,
        key="num_items_selector"
    )
    
    st.markdown("---")
    
    # Form with dynamic fields based on num_items
    with st.form("add_items_form", clear_on_submit=True):
        new_items = []
        
        for i in range(int(num_items)):
            st.markdown(f"#### 🛒 Item {i + 1}")
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                name = st.text_input(
                    f"Item Name", 
                    placeholder="e.g., Milk, Eggs, Bread", 
                    key=f"item_name_{i}",
                    label_visibility="visible"
                )
            
            with col2:
                expiry_date = st.date_input(
                    f"Expiry Date", 
                    min_value=datetime.now().date(), 
                    key=f"item_expiry_{i}",
                    help="Select the expiration date from the product packaging",
                    label_visibility="visible"
                )
            
            with col3:
                category = st.selectbox(
                    f"Category", 
                    FOOD_CATEGORIES, 
                    key=f"item_category_{i}",
                    label_visibility="visible"
                )
            
            if name.strip():
                new_items.append({
                    "name": name.strip(),
                    "expiry_date": expiry_date,
                    "category": category,
                    "added_date": datetime.now().date()
                })
            
            if i < int(num_items) - 1:
                st.markdown("---")
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("✅ Add Items to Inventory", use_container_width=True, type="primary")
        
        if submitted:
            if new_items:
                added_count, skipped_count = InventoryManager.add_items(username, new_items)
                if added_count > 0:
                    st.success(f"✅ Successfully added {added_count} item(s) to your inventory!")
                    st.balloons()
                if skipped_count > 0:
                    st.warning(f"⚠️ Skipped {skipped_count} item(s) (duplicates or invalid entries)")
            else:
                st.error("❌ No valid items to add. Please fill in at least one item name.")


def render_inventory_tab(username: str):
    """Render inventory management tab"""
    st.markdown("<h2 style='color: #4ECDC4;'>📦 Food Inventory</h2>", unsafe_allow_html=True)
    
    items = SessionManager.get_user_items(username)
    
    if not items:
        st.info("📭 Your inventory is empty. Start by adding some items!")
        return
    
    # Search and filter section
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search items", placeholder="Search by name...", key="search_inventory")
    
    with col2:
        sort_by = st.selectbox("📊 Sort by", ["Name", "Expiry Date", "Category", "Days Until Expiry"])
    
    with col3:
        filter_category = st.selectbox("🏷️ Filter by Category", ["All"] + FOOD_CATEGORIES)
    
    # Filter items
    filtered_items = items.copy()
    
    if search_term:
        filtered_items = [item for item in filtered_items if search_term.lower() in item['name'].lower()]
    
    if filter_category != "All":
        filtered_items = [item for item in filtered_items if item.get('category', 'Other') == filter_category]
    
    # Sort items
    if sort_by == "Name":
        filtered_items.sort(key=lambda x: x['name'].lower())
    elif sort_by == "Expiry Date":
        filtered_items.sort(key=lambda x: x['expiry_date'])
    elif sort_by == "Category":
        filtered_items.sort(key=lambda x: x.get('category', 'Other'))
    elif sort_by == "Days Until Expiry":
        filtered_items.sort(key=lambda x: ExpiryChecker.calculate_days_until_expiry(x['expiry_date']))
    
    # Display results count
    st.markdown(f"**Showing {len(filtered_items)} of {len(items)} items**")
    
    # Create DataFrame
    if filtered_items:
        data = []
        for item in filtered_items:
            days_left = ExpiryChecker.calculate_days_until_expiry(item['expiry_date'])
            status = ExpiryChecker.get_expiry_status(days_left)
            
            data.append({
                "Item Name": item['name'],
                "Category": item.get('category', 'Other'),
                "Expiry Date": item['expiry_date'].strftime("%Y-%m-%d"),
                "Days Left": days_left,
                "Status": status.replace("_", " ").title()
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Bulk actions
        st.markdown("---")
        st.markdown("#### 🗑️ Manage Items")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Delete Individual Items:**")
            st.caption("*Double-click on a button to confirm deletion*")
        
        with col2:
            if st.button("🗑️ Clear All Items", key="clear_all_button", help="Remove all items from inventory"):
                if st.session_state.get('confirm_clear', False):
                    InventoryManager.clear_all(username)
                    st.session_state.confirm_clear = False
                    st.success("✅ All items have been cleared from your inventory.")
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("⚠️ Click again to confirm clearing all items.")
        
        # Delete individual items
        cols = st.columns(3)
        for idx, item in enumerate(filtered_items):
            with cols[idx % 3]:
                days_left = ExpiryChecker.calculate_days_until_expiry(item['expiry_date'])
                status_icon = ExpiryChecker.get_status_icon(ExpiryChecker.get_expiry_status(days_left))
                
                if st.button(
                    f"{status_icon} {item['name']} ({days_left}d)", 
                    key=f"delete_{item['name']}_{idx}",
                    help=f"Click to delete {item['name']}"
                ):
                    if InventoryManager.delete_item(username, item['name']):
                        st.success(f"✅ Deleted '{item['name']}' from inventory")
                        st.rerun()
    else:
        st.warning("🔍 No items match your search criteria.")


def render_alerts_tab(username: str):
    """Render expiry alerts tab"""
    st.markdown("<h2 style='color: #4ECDC4;'>🚨 Expiry Alerts</h2>", unsafe_allow_html=True)
    
    items = SessionManager.get_user_items(username)
    
    if not items:
        st.info("📭 No items in inventory. Add items to see expiry alerts.")
        return
    
    # Categorize items by status
    categorized = {
        "expired": [],
        "expires_today": [],
        "critical": [],
        "warning": [],
        "fresh": []
    }
    
    for item in items:
        days_left = ExpiryChecker.calculate_days_until_expiry(item['expiry_date'])
        status = ExpiryChecker.get_expiry_status(days_left)
        categorized[status].append((item, days_left))
    
    # Display alerts by priority
    priority_order = ["expired", "expires_today", "critical", "warning", "fresh"]
    
    for status in priority_order:
        status_items = categorized[status]
        
        if not status_items:
            continue
        
        status_icon = ExpiryChecker.get_status_icon(status)
        status_color = ExpiryChecker.get_status_color(status)
        
        st.markdown(f"### {status_icon} {status.replace('_', ' ').title()} ({len(status_items)} items)")
        
        for item, days_left in status_items:
            if days_left < 0:
                message = f"<b>{item['name']}</b> expired {abs(days_left)} day(s) ago! 🚨"
            elif days_left == 0:
                message = f"<b>{item['name']}</b> expires TODAY! ⚠️"
            elif days_left == 1:
                message = f"<b>{item['name']}</b> expires TOMORROW! ⏰"
            else:
                message = f"<b>{item['name']}</b> expires in {days_left} day(s)"
            
            st.markdown(
                f"<div style='background-color: {status_color}; padding: 15px; border-radius: 10px; "
                f"color: #000000; margin: 10px 0; border-left: 5px solid #000;'>"
                f"{message}</div>",
                unsafe_allow_html=True
            )


def render_recipes_tab(username: str):
    """Render magic recipes tab"""
    st.markdown("<h2 style='color: #4ECDC4;'>🍳 Magic Recipes</h2>", unsafe_allow_html=True)
    
    st.info("💡 **Smart Recipe Suggestions:** Select ingredients that are expiring soon, and we'll suggest delicious recipes to help reduce food waste!")
    
    items = SessionManager.get_user_items(username)
    
    # Get items expiring soon (within 7 days)
    near_expiry = []
    for item in items:
        days_left = ExpiryChecker.calculate_days_until_expiry(item['expiry_date'])
        if 0 <= days_left <= 7:
            near_expiry.append((item, days_left))
    
    if not near_expiry:
        st.warning("⚠️ No items are expiring soon. Check back later or add more items to your inventory!")
        return
    
    # Sort by days left (ascending)
    near_expiry.sort(key=lambda x: x[1])
    
    st.markdown("### 🛒 Select Ingredients")
    st.caption(f"Found {len(near_expiry)} item(s) expiring within 7 days")
    
    # Display selectable items
    selected_items = []
    
    cols = st.columns(3)
    for idx, (item, days_left) in enumerate(near_expiry):
        with cols[idx % 3]:
            status_icon = ExpiryChecker.get_status_icon(ExpiryChecker.get_expiry_status(days_left))
            if st.checkbox(
                f"{status_icon} {item['name']} ({days_left}d left)",
                key=f"recipe_checkbox_{item['name']}_{idx}"
            ):
                selected_items.append(item)
    
    if not selected_items:
        st.info("👆 Select one or more ingredients above to get recipe suggestions.")
        return
    
    st.markdown("---")
    st.markdown(f"### 🎯 Selected: {', '.join([item['name'] for item in selected_items])}")
    
    # Get recipe suggestions
    ingredient_names = [item['name'] for item in selected_items]
    recipes = RecipeEngine.get_matching_recipes(ingredient_names)
    
    if not recipes:
        st.warning("😔 No recipes found matching your ingredients. Try selecting different items or add more ingredients.")
        return
    
    st.markdown(f"### 📖 Recipe Suggestions ({len(recipes)} found)")
    
    # Display recipes
    for recipe, match_count in recipes:
        with st.expander(f"⭐ **{recipe.name}** ({match_count} matching ingredients)"):
            # Recipe metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**⏱️ Prep Time:** {recipe.prep_time}")
            with col2:
                st.markdown(f"**📊 Difficulty:** {recipe.difficulty}")
            with col3:
                calories = recipe.nutrition.get('calories', 'N/A')
                st.markdown(f"**🔥 Calories:** {calories} kcal")
            
            st.markdown("---")
            
            # Ingredients
            st.markdown("**🥘 Ingredients:**")
            for ing in recipe.ingredients:
                is_matched = any(fuzz.partial_ratio(ing.lower(), item['name'].lower()) > 80 for item in selected_items)
                if is_matched:
                    st.markdown(f"- ✅ {ing} *(from your inventory)*")
                else:
                    st.markdown(f"- {ing}")
            
            st.markdown("---")
            
            # Instructions
            st.markdown("**👨‍🍳 Instructions:**")
            st.markdown(recipe.instructions)
            
            st.markdown("---")
            
            # Nutrition
            nutrition_html = RecipeEngine.format_recipe_card(recipe, ingredient_names)
            st.markdown(nutrition_html, unsafe_allow_html=True)
            
            # Feedback section
            st.markdown("---")
            st.markdown("**💬 Share Your Feedback:**")
            feedback_key = f"feedback_{recipe.name}_{hash(recipe.name)}"
            feedback = st.text_area(
                "Did you try this recipe? Let us know how it turned out!",
                key=feedback_key,
                placeholder="Share your experience, modifications, or suggestions..."
            )
            
            if st.button(f"Submit Feedback", key=f"submit_feedback_{recipe.name}"):
                if feedback.strip():
                    if 'feedback' not in st.session_state:
                        st.session_state.feedback = {}
                    st.session_state.feedback[recipe.name] = {
                        'user': username,
                        'feedback': feedback,
                        'timestamp': datetime.now().isoformat()
                    }
                    st.success("✅ Thank you for your feedback!")
                else:
                    st.warning("⚠️ Please enter some feedback before submitting.")


# ========================= MAIN APPLICATION =========================

def main():
    """Main application entry point"""
    
    # Set page configuration
    st.set_page_config(
        page_title="ExpirySense - Food Inventory Management",
        page_icon="🍎",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize session state
    SessionManager.initialize()
    
    # Render header
    render_header()
    
    # Check authentication
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # User is authenticated
    username = st.session_state.username
    
    # User welcome and logout section
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"### 👋 Welcome back, **{username}**!")
        if st.session_state.last_login:
            st.caption(f"Last login: {st.session_state.last_login.strftime('%Y-%m-%d %H:%M')}")
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            AuthenticationManager.logout()
            st.success("✅ Logged out successfully!")
            st.rerun()
    
    st.markdown("---")
    
    # Statistics Dashboard
    render_statistics_dashboard(username)
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Add Items",
        "📦 Food Inventory",
        "🚨 Expiry Alerts",
        "🍳 Magic Recipes"
    ])
    
    with tab1:
        render_add_items_tab(username)
    
    with tab2:
        render_inventory_tab(username)
    
    with tab3:
        render_alerts_tab(username)
    
    with tab4:
        render_recipes_tab(username)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666; font-size: 14px;'>"
        "ExpirySense v2.0 | Made with ❤️ to reduce food waste | © 2024"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

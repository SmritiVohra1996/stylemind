import streamlit as st
import anthropic
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StyleMind · AI Personal Stylist",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    color: #1a1a1a;
    margin-bottom: 0.2rem;
}
.hero p {
    color: #888;
    font-size: 1.05rem;
    font-weight: 300;
}
.chat-user {
    background: #1a1a1a;
    color: white;
    padding: 0.8rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    margin: 0.5rem 0 0.5rem 3rem;
    font-size: 0.95rem;
    line-height: 1.5;
}
.chat-assistant {
    background: #f8f5f0;
    color: #1a1a1a;
    padding: 0.8rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    margin: 0.5rem 3rem 0.5rem 0;
    font-size: 0.95rem;
    line-height: 1.6;
    border-left: 3px solid #c9a96e;
}
.tool-log {
    background: #f0f7ff;
    border-left: 3px solid #4a90d9;
    padding: 0.4rem 0.8rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.8rem;
    color: #4a6fa5;
    margin: 0.2rem 0;
    font-family: monospace;
}
.divider { border-top: 1px solid #f0ebe3; margin: 1rem 0; }
.sidebar-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: #1a1a1a;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Inventory data ─────────────────────────────────────────────────────────────
INVENTORY = [
    {"id": "T001", "name": "White Linen Oversized Shirt", "category": "top", "color": "white",
     "price": 45, "sizes": ["XS","S","M","L"], "style_tags": ["casual","smart-casual","summer"],
     "body_types": ["all"], "occasions": ["work","weekend","brunch"], "in_stock": True},
    {"id": "T002", "name": "Black Fitted Turtleneck", "category": "top", "color": "black",
     "price": 35, "sizes": ["XS","S","M"], "style_tags": ["minimal","classic","winter"],
     "body_types": ["pear","hourglass","rectangle"], "occasions": ["work","dinner","date"], "in_stock": True},
    {"id": "T003", "name": "Floral Wrap Blouse", "category": "top", "color": "multicolor",
     "price": 55, "sizes": ["S","M","L","XL"], "style_tags": ["feminine","romantic","spring"],
     "body_types": ["hourglass","pear"], "occasions": ["brunch","date","wedding-guest"], "in_stock": True},
    {"id": "T004", "name": "Striped Breton Top", "category": "top", "color": "navy-white",
     "price": 30, "sizes": ["XS","S","M","L","XL"], "style_tags": ["casual","french","classic"],
     "body_types": ["all"], "occasions": ["weekend","travel","casual"], "in_stock": True},
    {"id": "T005", "name": "Silk Cami in Champagne", "category": "top", "color": "champagne",
     "price": 65, "sizes": ["XS","S","M"], "style_tags": ["elegant","evening","minimal"],
     "body_types": ["hourglass","rectangle","inverted-triangle"], "occasions": ["dinner","date","party"], "in_stock": True},
    {"id": "B001", "name": "High-Waist Wide Leg Trousers", "category": "bottom", "color": "camel",
     "price": 75, "sizes": ["XS","S","M","L"], "style_tags": ["smart-casual","minimal","autumn"],
     "body_types": ["pear","hourglass","rectangle"], "occasions": ["work","dinner","smart-casual"], "in_stock": True},
    {"id": "B002", "name": "Black Tailored Slim Trousers", "category": "bottom", "color": "black",
     "price": 70, "sizes": ["XS","S","M","L","XL"], "style_tags": ["classic","work","minimal"],
     "body_types": ["all"], "occasions": ["work","dinner","formal"], "in_stock": True},
    {"id": "B003", "name": "Flowy Midi Skirt in Terracotta", "category": "bottom", "color": "terracotta",
     "price": 60, "sizes": ["XS","S","M","L"], "style_tags": ["feminine","boho","autumn"],
     "body_types": ["all"], "occasions": ["brunch","weekend","date"], "in_stock": True},
    {"id": "B004", "name": "White Linen Shorts", "category": "bottom", "color": "white",
     "price": 40, "sizes": ["XS","S","M","L"], "style_tags": ["casual","summer","beach"],
     "body_types": ["hourglass","rectangle","inverted-triangle"], "occasions": ["weekend","beach","travel"], "in_stock": True},
    {"id": "B005", "name": "Dark Wash Straight Jeans", "category": "bottom", "color": "dark-blue",
     "price": 85, "sizes": ["XS","S","M","L","XL"], "style_tags": ["casual","classic","versatile"],
     "body_types": ["all"], "occasions": ["casual","weekend","smart-casual"], "in_stock": True},
    {"id": "D001", "name": "Wrap Dress in Forest Green", "category": "dress", "color": "green",
     "price": 95, "sizes": ["XS","S","M","L"], "style_tags": ["feminine","elegant","versatile"],
     "body_types": ["hourglass","pear","rectangle"], "occasions": ["dinner","date","work","wedding-guest"], "in_stock": True},
    {"id": "D002", "name": "Linen Shirt Dress in Ecru", "category": "dress", "color": "ecru",
     "price": 110, "sizes": ["XS","S","M","L","XL"], "style_tags": ["minimal","casual","summer"],
     "body_types": ["all"], "occasions": ["brunch","travel","weekend","work"], "in_stock": True},
    {"id": "O001", "name": "Camel Wool Blend Coat", "category": "outerwear", "color": "camel",
     "price": 195, "sizes": ["XS","S","M","L"], "style_tags": ["classic","minimal","winter"],
     "body_types": ["all"], "occasions": ["work","smart-casual","everyday"], "in_stock": True},
    {"id": "O002", "name": "Oversized Denim Jacket", "category": "outerwear", "color": "light-blue",
     "price": 90, "sizes": ["XS","S","M","L","XL"], "style_tags": ["casual","spring"],
     "body_types": ["all"], "occasions": ["casual","weekend","travel"], "in_stock": True},
    {"id": "S001", "name": "White Leather Sneakers", "category": "shoes", "color": "white",
     "price": 85, "sizes": ["36","37","38","39","40","41"], "style_tags": ["casual","minimal","versatile"],
     "body_types": ["all"], "occasions": ["casual","weekend","travel"], "in_stock": True},
    {"id": "S002", "name": "Black Block Heel Mules", "category": "shoes", "color": "black",
     "price": 95, "sizes": ["36","37","38","39","40"], "style_tags": ["smart-casual","elegant","minimal"],
     "body_types": ["all"], "occasions": ["work","dinner","smart-casual"], "in_stock": True},
    {"id": "S003", "name": "Tan Leather Ankle Boots", "category": "shoes", "color": "tan",
     "price": 145, "sizes": ["36","37","38","39","40"], "style_tags": ["classic","autumn","versatile"],
     "body_types": ["all"], "occasions": ["work","smart-casual","weekend"], "in_stock": True},
]

# ── Tools ──────────────────────────────────────────────────────────────────────
def search_inventory(category=None, color=None, max_price=None, occasion=None, style_tag=None):
    results = INVENTORY.copy()
    if category: results = [i for i in results if i["category"] == category]
    if color: results = [i for i in results if color.lower() in i["color"].lower()]
    if max_price: results = [i for i in results if i["price"] <= max_price]
    if occasion: results = [i for i in results if occasion.lower() in [o.lower() for o in i["occasions"]]]
    if style_tag: results = [i for i in results if style_tag.lower() in [s.lower() for s in i["style_tags"]]]
    return [{"id": r["id"], "name": r["name"], "price": r["price"],
             "color": r["color"], "occasions": r["occasions"]} for r in results if r["in_stock"]]

def check_size_availability(item_id, size):
    item = next((i for i in INVENTORY if i["id"] == item_id), None)
    if not item: return {"available": False, "reason": "Item not found"}
    if size in item["sizes"]: return {"available": True, "item_name": item["name"], "size": size}
    return {"available": False, "item_name": item["name"],
            "reason": f"Size {size} not available", "available_sizes": item["sizes"]}

def get_style_advice(body_type, occasion, season=None):
    advice_db = {
        "pear": {"tips": "Balance wider hips with structured shoulders. Wide-leg trousers and A-line skirts are your best friend. Draw attention upward with interesting necklines.",
                 "best_items": ["wrap tops","peplum tops","wide-leg trousers","a-line skirts"]},
        "hourglass": {"tips": "Celebrate your proportions with fitted styles and wrap silhouettes that follow your natural curves.",
                      "best_items": ["wrap dresses","fitted tops","high-waist styles","bodycon styles"]},
        "rectangle": {"tips": "Create the illusion of curves with ruching, peplums, and cinched waists. Layering adds great dimension.",
                      "best_items": ["belted dresses","ruffled tops","a-line skirts","wrap styles"]},
        "inverted-triangle": {"tips": "Balance broader shoulders with volume at the hips. A-line and full skirts add great proportion.",
                              "best_items": ["wide-leg trousers","a-line skirts","v-necks","flared jeans"]},
    }
    occasion_guidelines = {
        "work": "Keep it polished. Neutral colors, structured pieces, modest hemlines.",
        "date": "Show personality. One statement piece, well-fitted clothes, subtle elegance.",
        "wedding-guest": "Avoid white or ivory. Midi length is safest. Look festive but not attention-stealing.",
        "casual": "Comfort first — elevated basics with quality fabrics and good fit.",
        "brunch": "Smart-casual with a fun element. Pastels, florals, or a statement accessory.",
        "dinner": "Elegant but not over-dressed. A midi dress or smart trousers work perfectly.",
    }
    body_advice = advice_db.get(body_type, {"tips": "Focus on fit above all else.", "best_items": ["well-fitted basics"]})
    return {
        "body_type_advice": body_advice,
        "occasion_guideline": occasion_guidelines.get(occasion, "Dress appropriately and feel confident."),
        "season_note": f"For {season}, prioritize {'breathable fabrics like linen and cotton' if season in ['spring','summer'] else 'layerable pieces and warmer fabrics'}." if season else ""
    }

def build_complete_outfit(top_id=None, bottom_id=None, dress_id=None, shoes_id=None, outerwear_id=None):
    outfit_items, total_price = [], 0
    for item_id in [top_id, bottom_id, dress_id, shoes_id, outerwear_id]:
        if item_id:
            item = next((i for i in INVENTORY if i["id"] == item_id), None)
            if item:
                outfit_items.append({"id": item["id"], "name": item["name"],
                                     "category": item["category"], "price": item["price"], "color": item["color"]})
                total_price += item["price"]
    return {"outfit_items": outfit_items, "total_price": total_price, "item_count": len(outfit_items)}

def apply_budget_filter(items, max_budget):
    total = sum(i["price"] for i in items)
    if total <= max_budget: return {"within_budget": True, "total": total, "items": items}
    sorted_items = sorted(items, key=lambda x: x["price"])
    kept, running = [], 0
    for item in sorted_items:
        if running + item["price"] <= max_budget:
            kept.append(item); running += item["price"]
    return {"within_budget": False, "original_total": total,
            "suggested_total": running, "suggested_items": kept}

TOOL_MAP = {
    "search_inventory": search_inventory,
    "check_size_availability": check_size_availability,
    "get_style_advice": get_style_advice,
    "build_complete_outfit": build_complete_outfit,
    "apply_budget_filter": apply_budget_filter,
}

TOOLS = [
    {"name": "search_inventory", "description": "Search clothing inventory by category, color, price, occasion, or style.",
     "input_schema": {"type": "object", "properties": {
         "category": {"type": "string", "description": "top, bottom, dress, shoes, or outerwear"},
         "color": {"type": "string"}, "max_price": {"type": "number"},
         "occasion": {"type": "string", "description": "work, date, casual, brunch, wedding-guest, dinner"},
         "style_tag": {"type": "string"}}}},
    {"name": "check_size_availability", "description": "Check if an item is available in the customer's size.",
     "input_schema": {"type": "object", "properties": {
         "item_id": {"type": "string"}, "size": {"type": "string"}},
         "required": ["item_id", "size"]}},
    {"name": "get_style_advice", "description": "Get styling tips for a body type and occasion.",
     "input_schema": {"type": "object", "properties": {
         "body_type": {"type": "string"}, "occasion": {"type": "string"}, "season": {"type": "string"}},
         "required": ["body_type", "occasion"]}},
    {"name": "build_complete_outfit", "description": "Combine items into a complete outfit and get total price.",
     "input_schema": {"type": "object", "properties": {
         "top_id": {"type": "string"}, "bottom_id": {"type": "string"},
         "dress_id": {"type": "string"}, "shoes_id": {"type": "string"}, "outerwear_id": {"type": "string"}}}},
    {"name": "apply_budget_filter", "description": "Check if items fit within budget.",
     "input_schema": {"type": "object", "properties": {
         "items": {"type": "array", "items": {"type": "object"}}, "max_budget": {"type": "number"}},
         "required": ["items", "max_budget"]}},
]

SYSTEM_PROMPT = """You are StyleMind, an expert personal stylist AI for a premium fashion retailer.
You help customers find complete, curated outfits suited to their body type, occasion, budget, and style.

Your approach:
1. Understand the customer's needs (occasion, budget, size, body type)
2. Use get_style_advice to understand what works for their body type
3. Search inventory systematically — tops, bottoms (or dresses), shoes
4. Always check size availability before recommending
5. Build a complete outfit and verify it fits the budget
6. Present your recommendation with genuine stylist reasoning — explain WHY each piece works

Be warm, knowledgeable, and specific. You are a stylist, not a search engine.
Always recommend at least one complete outfit. If a size is unavailable, find an alternative."""

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "last_processed" not in st.session_state:
    st.session_state.last_processed = ""

# ── History sanitizer ──────────────────────────────────────────────────────────
def sanitize_history(history):
    clean = []
    for msg in history:
        if isinstance(msg["content"], str):
            clean.append(msg)
        elif isinstance(msg["content"], list):
            sanitized_blocks = []
            for block in msg["content"]:
                if isinstance(block, dict):
                    sanitized_blocks.append(block)
                elif hasattr(block, "type"):
                    if block.type == "text":
                        sanitized_blocks.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        sanitized_blocks.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })
                    elif block.type == "tool_result":
                        sanitized_blocks.append({
                            "type": "tool_result",
                            "tool_use_id": block.tool_use_id,
                            "content": block.content
                        })
            if sanitized_blocks:
                clean.append({"role": msg["role"], "content": sanitized_blocks})
        else:
            continue
    return clean

# ── Agent runner ───────────────────────────────────────────────────────────────
def run_stylist_agent(user_message, conversation_history, tool_log_placeholder):
    client = anthropic.Anthropic(
        api_key=st.secrets.get("ANTHROPIC_API_KEY", st.session_state.api_key)
    )
    conversation_history.append({"role": "user", "content": user_message})
    tool_calls_made = []

    while True:
        clean_history = sanitize_history(conversation_history)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=clean_history
        )

        if response.stop_reason == "tool_use":
            conversation_history.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made.append(f"🔧 {block.name}({json.dumps(block.input, ensure_ascii=False)[:80]}...)")
                    tool_log_placeholder.markdown(
                        "\n".join(f'<div class="tool-log">{t}</div>' for t in tool_calls_made),
                        unsafe_allow_html=True
                    )
                    result = TOOL_MAP[block.name](**block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            conversation_history.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            final_text = "".join(block.text for block in response.content if hasattr(block, "text"))
            conversation_history.append({"role": "assistant", "content": final_text})
            return final_text, conversation_history, tool_calls_made

        else:
            return "Something went wrong. Please try again.", conversation_history, tool_calls_made

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header">✨ StyleMind</div>', unsafe_allow_html=True)
    st.markdown("*Your AI Personal Stylist*")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if "ANTHROPIC_API_KEY" in st.secrets:
        st.session_state.api_key = st.secrets["ANTHROPIC_API_KEY"]
        st.success("✅ Ready to style you!", icon="✨")
    else:
        api_key_input = st.text_input("Anthropic API Key", type="password",
                                       placeholder="sk-ant-...")
        if api_key_input:
            st.session_state.api_key = api_key_input

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("**Try asking about:**")
    examples = [
        "👔 Job interview outfit, size S, hourglass, $250",
        "💍 Wedding guest look, size L, $180",
        "☀️ Casual weekend, rectangle body, size M, $150",
        "🌙 Date night, pear shape, size XS, $200",
        "✈️ Travel outfit, size M, minimal style, $200",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=ex):
            st.session_state.prefill = ex

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.last_processed = ""
        st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.78rem; color:#aaa; line-height:1.6'>
    <b>How it works</b><br>
    StyleMind uses Agentic AI — it autonomously searches inventory, checks sizes, applies style rules,
    and builds complete outfits. Watch the tool calls appear as it thinks.
    </div>
    """, unsafe_allow_html=True)

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>✨ StyleMind</h1>
    <p>Agentic AI Personal Stylist · Tell me your occasion, size, body type & budget</p>
</div>
""", unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

# Pre-fill from sidebar button clicks
prefill_value = st.session_state.pop("prefill", "") if "prefill" in st.session_state else ""

# Input row
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("", placeholder="e.g. Work dinner outfit, size M, pear body type, budget $200",
                                value=prefill_value, label_visibility="collapsed", key="input_box")
with col2:
    send = st.button("Send →", type="primary", use_container_width=True)

# Handle send — guard with processing flag to prevent double execution on rerun
if (send or user_input) and user_input.strip():
    if st.session_state.get("last_processed") == user_input:
        pass  # Already handled this exact message, skip
    elif not st.session_state.api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    else:
        st.session_state.last_processed = user_input

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)

        with st.spinner("StyleMind is styling your look..."):
            tool_log = st.empty()
            response, st.session_state.history, tools_used = run_stylist_agent(
                user_input, st.session_state.history, tool_log
            )
            tool_log.empty()

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(f'<div class="chat-assistant">{response}</div>', unsafe_allow_html=True)

        if tools_used:
            with st.expander(f"🔍 Agent used {len(tools_used)} tools to build this recommendation"):
                for t in tools_used:
                    st.markdown(f'<div class="tool-log">{t}</div>', unsafe_allow_html=True)
        st.rerun()

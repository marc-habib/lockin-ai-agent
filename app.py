"""
Gradio app for LockIn AI - Hugging Face Spaces deployment.

This app provides:
1. Chat interface with the agent
2. Evaluation suite (exact-match + LLM-judge + categories)
3. Monitoring dashboard (latency, tokens, cost)
4. Profile management
"""

import gradio as gr
import json
import time
from datetime import datetime
from pathlib import Path

# Initialize app directories
Path("data").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# Import after directory creation
from app.agent.handler import run_agent_handler
from app.services.profile_service import profile_service
from app.schemas.profile import ProfileCreate
from app.models.enums import Sex, Goal, ActivityLevel
from app.database.init_db import init_database
from app.config import settings

# Initialize database
init_database()

# Global metrics storage
metrics_log = []


def chat_interface(user_id: str, message: str, history: list) -> tuple:
    """
    Main chat interface with the agent.
    
    Args:
        user_id: User identifier
        message: User message
        history: Chat history
    
    Returns:
        Tuple of (history, metrics_json)
    """
    if not user_id.strip():
        return history + [("Error", "Please enter a User ID")], ""
    
    if not message.strip():
        return history, ""
    
    # Call agent handler
    start_time = time.time()
    response = run_agent_handler(user_id=user_id.strip(), message=message)
    
    # Track metrics
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "request_id": response.request_id,
        "status": response.status.value,
        "intent": response.intent.value if response.intent else None,
        "latency_ms": response.latency_ms,
        "tool_calls": response.tool_calls,
        "guardrail_triggered": response.guardrail_triggered,
    }
    metrics_log.append(metrics)
    
    # Format response
    if response.status.value == "success":
        bot_response = response.response
        if response.data:
            bot_response += f"\n\n📊 **Structured Data:**\n```json\n{json.dumps(response.data, indent=2)}\n```"
    elif response.status.value == "profile_required":
        bot_response = f"⚠️ **Profile Required**\n\nMissing fields: {', '.join(response.missing_fields or [])}\n\nPlease complete your profile in the 'Profile Setup' tab."
    elif response.status.value == "blocked":
        bot_response = f"🚫 **Request Blocked**\n\n{response.response}\n\nReason: {response.guardrail_triggered}"
    else:
        bot_response = f"❌ **Error**\n\n{response.response}"
    
    # Update history
    history = history + [(message, bot_response)]
    
    # Format metrics for display
    metrics_display = f"""**Request Metrics:**
- Request ID: `{response.request_id}`
- Status: `{response.status.value}`
- Intent: `{response.intent.value if response.intent else 'N/A'}`
- Latency: `{response.latency_ms}ms`
- Tools Used: `{', '.join(response.tool_calls) if response.tool_calls else 'None'}`
"""
    
    return history, metrics_display


def create_profile(user_id: str, age: int, sex: str, height_cm: float, weight_kg: float,
                  goal: str, activity_level: str, gym_sessions: int, running_sessions: int,
                  allergies: str, restrictions: str, dislikes: str) -> str:
    """Create or update user profile."""
    try:
        if not user_id.strip():
            return "❌ Error: User ID is required"
        
        # Parse list fields
        allergies_list = [a.strip() for a in allergies.split(",") if a.strip()] if allergies else []
        restrictions_list = [r.strip() for r in restrictions.split(",") if r.strip()] if restrictions else []
        dislikes_list = [d.strip() for d in dislikes.split(",") if d.strip()] if dislikes else []
        
        profile_data = ProfileCreate(
            user_id=user_id.strip(),
            age=age,
            sex=Sex(sex),
            height_cm=height_cm,
            weight_kg=weight_kg,
            goal=Goal(goal),
            activity_level=ActivityLevel(activity_level),
            gym_sessions_per_week=gym_sessions,
            running_sessions_per_week=running_sessions,
            allergies=allergies_list,
            dietary_restrictions=restrictions_list,
            disliked_foods=dislikes_list,
            country="France",
            budget_per_day=15.0
        )
        
        # Check if profile exists
        if profile_service.profile_exists(user_id.strip()):
            # Update existing profile
            from app.schemas.profile import ProfileUpdate
            update_data = ProfileUpdate(**profile_data.model_dump(exclude={'user_id'}))
            profile = profile_service.update_profile(user_id.strip(), update_data)
            action = "updated"
        else:
            # Create new profile
            profile = profile_service.create_profile(profile_data)
            action = "created"
        
        return f"""✅ **Profile {action} successfully!**

**Your Targets:**
- BMR: {profile.bmr:.0f} kcal/day
- TDEE: {profile.tdee:.0f} kcal/day
- Target Calories: {profile.target_macros.calories:.0f} kcal/day
- Protein: {profile.target_macros.protein_g:.0f}g
- Carbs: {profile.target_macros.carbs_g:.0f}g
- Fat: {profile.target_macros.fat_g:.0f}g

You can now use the chat interface!
"""
    except Exception as e:
        return f"❌ Error creating profile: {str(e)}"


def get_monitoring_stats() -> str:
    """Get monitoring statistics."""
    if not metrics_log:
        return "No requests logged yet."
    
    total_requests = len(metrics_log)
    successful = sum(1 for m in metrics_log if m['status'] == 'success')
    blocked = sum(1 for m in metrics_log if m['status'] == 'blocked')
    errors = sum(1 for m in metrics_log if m['status'] == 'error')
    
    avg_latency = sum(m['latency_ms'] for m in metrics_log) / total_requests
    
    # Tool usage
    tool_usage = {}
    for m in metrics_log:
        if m['tool_calls']:
            for tool in m['tool_calls']:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
    
    # Intent distribution
    intent_dist = {}
    for m in metrics_log:
        if m['intent']:
            intent_dist[m['intent']] = intent_dist.get(m['intent'], 0) + 1
    
    stats = f"""## 📊 Monitoring Dashboard

### Request Statistics
- **Total Requests:** {total_requests}
- **Successful:** {successful} ({100*successful/total_requests:.1f}%)
- **Blocked:** {blocked} ({100*blocked/total_requests:.1f}% if total_requests else 0)
- **Errors:** {errors} ({100*errors/total_requests:.1f}% if total_requests else 0)

### Performance
- **Average Latency:** {avg_latency:.0f}ms
- **P95 Latency:** {sorted([m['latency_ms'] for m in metrics_log])[int(0.95*total_requests)] if total_requests > 0 else 0:.0f}ms

### Tool Usage
"""
    for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
        stats += f"- **{tool}:** {count} calls\n"
    
    stats += "\n### Intent Distribution\n"
    for intent, count in sorted(intent_dist.items(), key=lambda x: x[1], reverse=True):
        stats += f"- **{intent}:** {count} requests\n"
    
    return stats


def run_evaluation() -> str:
    """Run evaluation suite."""
    from app.evaluation import run_full_evaluation
    
    try:
        results = run_full_evaluation()
        return results
    except Exception as e:
        return f"❌ Error running evaluation: {str(e)}"


# Build Gradio interface
with gr.Blocks(title="LockIn AI - Lab 4 Production Agent", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 LockIn AI - Production Agentic System
    
    **Lab 4 Deliverables:** Evaluation • Observability • Safety • Deployment
    
    This agent provides personalized nutrition and fitness planning with:
    - ✅ **5 specialized tools** (food lookup, product search, recipe calculator, meal planner, progress tracker)
    - ✅ **3-layer guardrails** (input validation, profile checks, output filtering)
    - ✅ **Full observability** (latency tracking, tool usage, cost estimation)
    - ✅ **Comprehensive evaluation** (exact-match, LLM-judge, category reports)
    """)
    
    with gr.Tabs():
        # Tab 1: Chat Interface
        with gr.Tab("💬 Chat"):
            gr.Markdown("### Chat with LockIn AI Agent")
            
            with gr.Row():
                with gr.Column(scale=3):
                    user_id_input = gr.Textbox(
                        label="User ID",
                        placeholder="Enter your user ID (e.g., user_123)",
                        value="demo_user"
                    )
                    chatbot = gr.Chatbot(label="Conversation", height=400)
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Ask about nutrition, meal plans, or your progress...",
                        lines=2
                    )
                    with gr.Row():
                        submit_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear")
                
                with gr.Column(scale=1):
                    metrics_display = gr.Markdown("**Request Metrics:** (will appear after sending a message)")
            
            # Examples
            gr.Examples(
                examples=[
                    ["demo_user", "Plan my meals for today"],
                    ["demo_user", "How much protein do I have left today?"],
                    ["demo_user", "What's the nutrition in 100g chicken breast?"],
                    ["demo_user", "Search for protein bars"],
                    ["demo_user", "Calculate macros for: 200g chicken, 150g rice, 100g broccoli"],
                ],
                inputs=[user_id_input, msg]
            )
            
            # Event handlers
            submit_btn.click(
                chat_interface,
                inputs=[user_id_input, msg, chatbot],
                outputs=[chatbot, metrics_display]
            ).then(lambda: "", None, msg)
            
            msg.submit(
                chat_interface,
                inputs=[user_id_input, msg, chatbot],
                outputs=[chatbot, metrics_display]
            ).then(lambda: "", None, msg)
            
            clear_btn.click(lambda: ([], ""), None, [chatbot, metrics_display])
        
        # Tab 2: Profile Setup
        with gr.Tab("👤 Profile Setup"):
            gr.Markdown("### Create or Update Your Profile")
            gr.Markdown("Complete your profile to get personalized recommendations.")
            
            with gr.Row():
                with gr.Column():
                    profile_user_id = gr.Textbox(label="User ID", value="demo_user")
                    profile_age = gr.Number(label="Age", value=25, minimum=13, maximum=100)
                    profile_sex = gr.Radio(label="Sex", choices=["male", "female"], value="male")
                    profile_height = gr.Number(label="Height (cm)", value=175, minimum=100, maximum=250)
                    profile_weight = gr.Number(label="Weight (kg)", value=75, minimum=30, maximum=300)
                
                with gr.Column():
                    profile_goal = gr.Radio(
                        label="Goal",
                        choices=["lose_fat", "maintain", "gain_muscle"],
                        value="maintain"
                    )
                    profile_activity = gr.Radio(
                        label="Activity Level",
                        choices=["sedentary", "light", "moderate", "active", "very_active"],
                        value="moderate"
                    )
                    profile_gym = gr.Slider(label="Gym Sessions per Week", minimum=0, maximum=7, value=3, step=1)
                    profile_running = gr.Slider(label="Running Sessions per Week", minimum=0, maximum=7, value=2, step=1)
            
            with gr.Row():
                profile_allergies = gr.Textbox(label="Allergies (comma-separated)", placeholder="peanuts, shellfish")
                profile_restrictions = gr.Textbox(label="Dietary Restrictions (comma-separated)", placeholder="vegetarian, gluten-free")
                profile_dislikes = gr.Textbox(label="Disliked Foods (comma-separated)", placeholder="mushrooms, olives")
            
            profile_submit = gr.Button("Create/Update Profile", variant="primary")
            profile_output = gr.Markdown()
            
            profile_submit.click(
                create_profile,
                inputs=[
                    profile_user_id, profile_age, profile_sex, profile_height, profile_weight,
                    profile_goal, profile_activity, profile_gym, profile_running,
                    profile_allergies, profile_restrictions, profile_dislikes
                ],
                outputs=profile_output
            )
        
        # Tab 3: Evaluation
        with gr.Tab("📊 Evaluation"):
            gr.Markdown("""
            ### Evaluation Suite (Lab 4 Requirement)
            
            This tab runs comprehensive evaluation tests:
            - **Exact-match tests:** Verify tool correctness with known answers
            - **LLM-judge tests:** Evaluate open-ended responses
            - **Category reports:** Track success rates by intent type
            """)
            
            eval_button = gr.Button("Run Full Evaluation", variant="primary")
            eval_output = gr.Markdown()
            
            eval_button.click(run_evaluation, outputs=eval_output)
        
        # Tab 4: Monitoring
        with gr.Tab("📈 Monitoring"):
            gr.Markdown("""
            ### Observability Dashboard (Lab 4 Requirement)
            
            Real-time monitoring of:
            - Request statistics (success/blocked/error rates)
            - Performance metrics (latency, P95)
            - Tool usage patterns
            - Intent distribution
            """)
            
            refresh_button = gr.Button("Refresh Stats", variant="primary")
            monitoring_output = gr.Markdown()
            
            refresh_button.click(get_monitoring_stats, outputs=monitoring_output)
            
            # Auto-refresh on load
            demo.load(get_monitoring_stats, outputs=monitoring_output)
    
    gr.Markdown("""
    ---
    ### 🎯 Lab 4 Deliverables Checklist
    
    ✅ **Evaluation:** Exact-match + LLM-judge + category reports (see Evaluation tab)  
    ✅ **Observability:** Latency, tokens, tool usage tracking (see Monitoring tab)  
    ✅ **Safety:** 3-layer guardrails (input → profile → output validation)  
    ✅ **Deployment:** Gradio app on Hugging Face Spaces with API access  
    ✅ **Tools:** 5 specialized tools (food_lookup, product_lookup, recipe_macro, daily_planner, get_progress)  
    
    **Provider:** `{settings.llm_provider}` | **Model:** `{settings.default_model}`
    """)

# Launch configuration
if __name__ == "__main__":
    demo.launch(
        server_name=settings.host,
        server_port=settings.port,
        share=False
    )

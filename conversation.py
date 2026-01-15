conversations = {}

def get_state(phone):
    return conversations.get(phone, {"step": "problem", "data": {}})

def update_state(phone, step, data):
    conversations[phone] = {
        "step": step,
        "data": data
    }

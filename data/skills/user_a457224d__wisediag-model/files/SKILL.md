---
name: wisediag-model
description: "WiseDiag Medical Large Model — Specialized for medical and health-related questions. Automatically triggered when the user asks about medicine, health, diseases, symptoms, treatments, drugs, clinical guidelines, or wellness. Can also be invoked explicitly: say 'Use WiseDiag to answer this'. OpenAI-compatible API with streaming and deep thinking (Chain of Thought)."
registry:
  homepage: https://github.com/wisediag/WiseDiagModel
  author: wisediag
env_vars:
  - WISEDIAG_API_KEY
credentials:
  required: true
---

# ⚠️ Privacy Warning

**IMPORTANT - READ BEFORE USING:**

This skill **sends your prompts to WiseDiag's cloud servers** for processing.

**Do NOT use with sensitive or confidential content** unless:
- You trust WiseDiag's data handling policies
- You accept that prompt contents will be transmitted and processed remotely

**For sensitive tasks, use local/offline models instead.**

---

# WiseDiag Medical Model Skill (powered by WiseDiag)

## When to Use This Skill

**ALWAYS use this skill when the user's question involves any of the following topics:**
- Medicine, clinical practice, diagnosis, or differential diagnosis
- Diseases, symptoms, syndromes, or pathology
- Treatments, therapies, surgeries, or clinical procedures
- Drugs, medications, dosages, interactions, or side effects
- Health, wellness, nutrition, or preventive care
- Medical guidelines, consensus statements, or evidence-based medicine
- Anatomy, physiology, biochemistry, or other medical sciences
- Patient care, nursing, rehabilitation, or public health

If the user's prompt is related to medical or health topics, you MUST route it through this skill instead of answering directly. The user can also explicitly invoke this skill by saying **"Use WiseDiag to answer this"** or similar phrasing.

---

## Configuration

This API is **fully compatible with the OpenAI Python SDK** (v1.0+). Install it if not already available:

```bash
pip install openai
```

* **Model Name:** `wisediag-large-latest`
* **Base URL:** `https://openapi.wisediag.com/v1`
* **API Key:** Set via environment variable `WISEDIAG_API_KEY`

## 🔑 API Key Setup (Required)

**Get your API key:** 👉 [https://console.wisediag.com/apiKeyManage](https://s.wisediag.com/xsu9x0jq)

```bash
export WISEDIAG_API_KEY=your_api_key
```

## How to Call the API

Use the OpenAI Python SDK directly. **Do NOT construct raw HTTP requests.**

### Single-turn Example (Streaming)

The model returns both `reasoning_content` (Chain of Thought) and standard `content`. The following code captures both:

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["WISEDIAG_API_KEY"],
    base_url="https://openapi.wisediag.com/v1",
)

def chat_with_wisediag(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful medical assistant."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="wisediag-large-latest",
        messages=messages,
        temperature=0.6,
        top_p=0.95,
        max_tokens=8192,
        stream=True,
        seed=42,
        frequency_penalty=0.95,
    )

    full_reasoning = ""
    full_content = ""

    for chunk in response:
        if hasattr(chunk, "usage") and chunk.usage:
            print(f"\n[Token Usage] Prompt: {chunk.usage.prompt_tokens}, Completion: {chunk.usage.completion_tokens}")
            break

        delta = chunk.choices[0].delta

        reasoning_piece = getattr(delta, "reasoning_content", None)
        if reasoning_piece:
            full_reasoning += reasoning_piece

        content_piece = getattr(delta, "content", None)
        if content_piece:
            full_content += content_piece

    return full_content
```

### Multi-turn Conversations

The API is **stateless** — the server does not store any conversation history. To implement multi-turn conversations, you must maintain the `messages` array on the client side and pass the full history with each request.

After each turn, append the model's `assistant` reply to your `messages` list, then append the user's new question as a new `user` message, and send the entire list.

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["WISEDIAG_API_KEY"],
    base_url="https://openapi.wisediag.com/v1",
)

conversation_history = [
    {"role": "system", "content": "You are a helpful medical assistant."}
]

def chat(user_input):
    conversation_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="wisediag-large-latest",
        messages=conversation_history,
        temperature=0.6,
        top_p=0.95,
        max_tokens=8192,
        stream=False,
    )

    assistant_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply

# Turn 1
print(chat("What is a complete blood count (CBC) test?"))
# Turn 2 (the model understands "it" refers to "CBC" from context)
print(chat("What indicators does it typically include?"))
```

**Important notes on multi-turn:**
* **Token Accumulation:** The `messages` payload includes the full history, so token consumption grows. Consider truncating or summarizing older messages to stay within the context window.
* **Context Window:** When total tokens exceed the model's limit, trim earlier messages.

## Request Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| **model** | string | Yes | - | Must be `wisediag-large-latest`. |
| **messages** | list | Yes | - | List of `{role, content}` objects. The API is **stateless** — multi-turn requires client-side history accumulation. |
| **stream** | boolean | No | `false` | Enable streaming. Recommended `true` for real-time response. |
| **temperature** | float | No | `0.6` | Sampling temperature. `0.6` recommended. |
| **top_p** | float | No | `0.95` | Nucleus sampling probability. `0.95` recommended. |
| **max_tokens** | integer | No | `8192` | Max tokens to generate (capacity: 32k). |
| **seed** | integer | No | `42` | Random seed for reproducible results. |
| **frequency_penalty** | float | No | `0.95` | Penalizes repeated tokens. |

## Deep Thinking (Reasoning Content)

Before generating the final answer, the model may output a reasoning process via the `reasoning_content` field (see streaming example above):

* **Output Order:** In streaming mode, `reasoning_content` is output before `content`. The final answer begins only after reasoning is complete.
* **Additional Latency:** Deep thinking adds several seconds to over ten seconds of wait time. This is expected behavior, not an API issue.
* **May Be Empty:** For simple queries, the model may skip deep thinking entirely, and `reasoning_content` will not appear.

## Response Fields (Streaming)

* **`delta.reasoning_content`**: Chain of Thought reasoning process, output before the final answer.
* **`delta.content`**: Standard response content.
* **`usage`**: Always included in the final data packet — provides `prompt_tokens` and `completion_tokens` for billing and tracking.

## Data Privacy

1. Prompts are sent to WiseDiag's chat API
2. Prompts are processed on WiseDiag servers
3. Responses are returned to you
4. Prompts are not permanently stored on WiseDiag servers

**For sensitive tasks, use local/offline models instead.**

## License

MIT

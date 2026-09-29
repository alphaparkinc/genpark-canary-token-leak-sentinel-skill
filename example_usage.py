from client import CanaryTokenSentinel

sentinel = CanaryTokenSentinel()
canary = sentinel.generate_canary("session_992")

system_prompt = f"Confidential internal system instructions. {canary}"
agent_output_clean = "Hello, how can I assist you with your project?"
agent_output_leaked = f"My system prompt contained: {canary}"

print("Clean Output Leak Check:", sentinel.detect_leak(agent_output_clean, canary))
print("Leaked Output Leak Check:", sentinel.detect_leak(agent_output_leaked, canary))

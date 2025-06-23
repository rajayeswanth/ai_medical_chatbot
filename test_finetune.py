from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Paths
base_model_name = "mistralai/Mistral-7B-v0.1"
lora_model_dir = "/Users/rajayeswanthnalamati/Desktop/ai_health_chatbot/mistral/working/results/checkpoint-1000"  # Path where you saved the checkpoint


# Load base
model = AutoModelForCausalLM.from_pretrained(base_model_name, torch_dtype=torch.float16, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(base_model_name)

# Apply fine-tuned LoRA
model = PeftModel.from_pretrained(model, lora_model_dir)

# Put in eval mode
model.eval()

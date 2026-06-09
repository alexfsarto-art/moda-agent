# ai_client.py
import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
from functools import lru_cache
from config import (
    MARITACA_CONFIG, 
    OPENAI_CONFIG, 
    GEMINI_CONFIG,
    AI_CACHE_CONFIG,
    RATE_LIMIT_CONFIG
)

class AIClient:
    """Cliente unificado para múltiplos provedores de IA"""
    
    def __init__(self, provider="maritaca"):
        self.provider = provider
        self.last_request_time = 0
        
   def call_maritaca(self, prompt: str, **kwargs) -> Dict[str, Any]:
    """Chama a API da Maritaca AI usando as variáveis do Render"""
    
    api_key = os.environ.get("MARITACA_API_KEY")
    base_url = os.environ.get("MARITACA_BASE_URL", "https://chat.maritaca.ai/api")
    
    if not api_key:
        return {"error": "MARITACA_API_KEY não configurada no Render"}
    
    # Usa o cliente compatível com OpenAI (recomendado pela documentação) [citation:3]
    import openai
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    
    try:
        response = client.chat.completions.create(
            model=kwargs.get("model", "sabia-3"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7)
        )
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "usage": response.usage
        }
    except Exception as e:
        return {"error": str(e)}
    
    def call_openai(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Chama a API da OpenAI (fallback)"""
        if not OPENAI_CONFIG["api_key"]:
            return {"error": "OPENAI_API_KEY não configurada"}
        
        self._rate_limit_check("openai")
        
        headers = {
            "Authorization": f"Bearer {OPENAI_CONFIG['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", OPENAI_CONFIG["model"]),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", OPENAI_CONFIG["max_tokens"]),
            "temperature": kwargs.get("temperature", OPENAI_CONFIG["temperature"])
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def call_gemini(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Chama a API do Google Gemini"""
        if not GEMINI_CONFIG["api_key"]:
            return {"error": "GEMINI_API_KEY não configurada"}
        
        self._rate_limit_check("gemini")
        
        url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_CONFIG['model']}:generateContent?key={GEMINI_CONFIG['api_key']}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": kwargs.get("temperature", GEMINI_CONFIG["temperature"]),
                "maxOutputTokens": kwargs.get("max_tokens", 2000)
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def _rate_limit_check(self, provider: str):
        """Verifica rate limiting"""
        config = RATE_LIMIT_CONFIG.get(provider, {"calls_per_minute": 60})
        calls_per_second = 60 / config["calls_per_minute"]
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < calls_per_second:
            time.sleep(calls_per_second - time_since_last)
        
        self.last_request_time = time.time()
    
    @lru_cache(maxsize=AI_CACHE_CONFIG["max_size"])
    def analyze_with_cache(self, prompt: str, use_cache: bool = True) -> str:
        """Analisa com cache para evitar chamadas repetidas"""
        if not use_cache:
            return self.analyze(prompt)
        
        # Implementação com cache
        return self.analyze(prompt)
    
    def analyze(self, prompt: str, **kwargs) -> str:
        """Método principal para análise com fallback entre provedores"""
        # Tenta o provedor principal
        if self.provider == "maritaca":
            result = self.call_maritaca(prompt, **kwargs)
            if "error" not in result:
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Fallback para OpenAI
        result = self.call_openai(prompt, **kwargs)
        if "error" not in result:
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Fallback para Gemini
        result = self.call_gemini(prompt, **kwargs)
        if "error" not in result:
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        return "Erro: Nenhum provedor de IA disponível"

# Instância global para uso em outros arquivos
ai_client = AIClient(provider="maritaca")

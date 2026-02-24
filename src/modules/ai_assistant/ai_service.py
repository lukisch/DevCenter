# -*- coding: utf-8 -*-
"""
DevCenter - AI Service
Claude API Integration für Code-Generierung
Basierend auf Entwicklerschleife V3
"""

import os
import asyncio
from typing import Optional, List, Dict, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import json


class AIModel(Enum):
    """Verfügbare AI-Modelle"""
    CLAUDE_SONNET = "claude-sonnet-4-20250514"
    CLAUDE_OPUS = "claude-opus-4-20250514"
    CLAUDE_HAIKU = "claude-haiku-4-20250514"


@dataclass
class AIMessage:
    """Eine Nachricht im Konversationsverlauf"""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class AIResponse:
    """Antwort vom AI-Service"""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """True wenn die Anfrage erfolgreich war (kein Fehler)."""
        return self.error is None


@dataclass
class CodeGenerationResult:
    """Ergebnis einer Code-Generierung"""
    plan: str = ""
    code: str = ""
    review: str = ""
    files: List[Dict[str, str]] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


class AIService:
    """
    AI-Service für Code-Generierung und Assistenz
    
    Verwendet die Anthropic Claude API für:
    - Code-Generierung
    - Code-Review
    - Architektur-Planung
    - Fehlerbehebung
    """
    
    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: Anthropic API Key (oder aus Umgebungsvariable)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY', '')
        self.model = AIModel.CLAUDE_SONNET.value
        self.max_tokens = 4096
        self.temperature = 0.7
        self.conversation_history: List[AIMessage] = []
        
        self._client = None
        self._anthropic_available = False
        
        try:
            import anthropic
            self._anthropic_available = True
            if self.api_key:
                self._client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            pass
    
    def is_available(self) -> bool:
        """Prüft ob der Service verfügbar ist"""
        return self._anthropic_available and bool(self.api_key)
    
    def set_api_key(self, api_key: str):
        """Setzt den API-Key"""
        self.api_key = api_key
        if self._anthropic_available and api_key:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
    
    def set_model(self, model: AIModel):
        """Setzt das zu verwendende Modell"""
        self.model = model.value
    
    def clear_history(self):
        """Löscht den Konversationsverlauf"""
        self.conversation_history.clear()
    
    async def complete(self, 
                       prompt: str,
                       system: str = None,
                       use_history: bool = True) -> AIResponse:
        """
        Sendet eine Anfrage an die Claude API
        
        Args:
            prompt: Die Benutzer-Nachricht
            system: Optionaler System-Prompt
            use_history: Konversationsverlauf einbeziehen
            
        Returns:
            AIResponse mit Ergebnis
        """
        if not self.is_available():
            return AIResponse(
                content="",
                model=self.model,
                error="AI-Service nicht verfügbar. API-Key prüfen oder anthropic installieren."
            )
        
        try:
            # Nachrichten zusammenstellen
            messages = []
            
            if use_history:
                for msg in self.conversation_history:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # API-Aufruf
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages
            }
            
            if system:
                kwargs["system"] = system
            
            # Synchroner Aufruf (anthropic SDK ist nicht async)
            response = await asyncio.to_thread(
                self._client.messages.create,
                **kwargs
            )
            
            content = response.content[0].text if response.content else ""
            
            # Verlauf aktualisieren
            if use_history:
                self.conversation_history.append(AIMessage("user", prompt))
                self.conversation_history.append(AIMessage("assistant", content))
            
            return AIResponse(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
            
        except Exception as e:
            return AIResponse(
                content="",
                model=self.model,
                error=str(e)
            )
    
    def complete_sync(self, 
                      prompt: str,
                      system: str = None,
                      use_history: bool = True) -> AIResponse:
        """Synchrone Version von complete()"""
        return asyncio.run(self.complete(prompt, system, use_history))
    
    async def generate_code(self,
                           description: str,
                           context: str = "",
                           language: str = "python") -> AIResponse:
        """
        Generiert Code basierend auf einer Beschreibung
        
        Args:
            description: Was soll der Code tun
            context: Optionaler Kontext (bestehender Code, Imports, etc.)
            language: Programmiersprache
            
        Returns:
            AIResponse mit generiertem Code
        """
        system = f"""Du bist ein erfahrener {language}-Entwickler.
Generiere sauberen, gut dokumentierten Code basierend auf der Beschreibung.
Füge Docstrings und Kommentare hinzu wo sinnvoll.
Antworte NUR mit dem Code, ohne zusätzliche Erklärungen."""
        
        prompt = f"""Generiere {language}-Code für folgende Anforderung:

{description}
"""
        
        if context:
            prompt += f"""
Bestehender Kontext/Code:
```{language}
{context}
```
"""
        
        return await self.complete(prompt, system, use_history=False)
    
    async def review_code(self, code: str, language: str = "python") -> AIResponse:
        """
        Reviewt Code und gibt Verbesserungsvorschläge
        
        Args:
            code: Der zu reviewende Code
            language: Programmiersprache
            
        Returns:
            AIResponse mit Review
        """
        system = """Du bist ein erfahrener Code-Reviewer.
Analysiere den Code auf:
- Bugs und Fehler
- Performance-Probleme
- Best Practices
- Sicherheitslücken
- Lesbarkeit

Gib konkrete Verbesserungsvorschläge."""
        
        prompt = f"""Bitte reviewe folgenden {language}-Code:

```{language}
{code}
```"""
        
        return await self.complete(prompt, system, use_history=False)
    
    async def fix_error(self, 
                        code: str, 
                        error_message: str,
                        language: str = "python") -> AIResponse:
        """
        Hilft bei der Behebung eines Fehlers
        
        Args:
            code: Der fehlerhafte Code
            error_message: Die Fehlermeldung
            language: Programmiersprache
            
        Returns:
            AIResponse mit Korrektur
        """
        system = """Du bist ein Debugging-Experte.
Analysiere den Fehler und gib eine korrigierte Version des Codes zurück.
Erkläre kurz, was das Problem war."""
        
        prompt = f"""Folgender {language}-Code erzeugt einen Fehler:

```{language}
{code}
```

Fehlermeldung:
```
{error_message}
```

Bitte korrigiere den Code."""
        
        return await self.complete(prompt, system, use_history=False)
    
    async def explain_code(self, code: str, language: str = "python") -> AIResponse:
        """
        Erklärt was ein Code-Abschnitt tut
        
        Args:
            code: Der zu erklärende Code
            language: Programmiersprache
            
        Returns:
            AIResponse mit Erklärung
        """
        system = """Du bist ein geduldiger Programmier-Lehrer.
Erkläre den Code Schritt für Schritt auf verständliche Weise."""
        
        prompt = f"""Erkläre bitte folgenden {language}-Code:

```{language}
{code}
```"""
        
        return await self.complete(prompt, system, use_history=False)


class DevelopmentLoop:
    """
    Entwicklerschleife - Automatisierte Code-Entwicklung
    
    Workflow:
    1. Planner: Erstellt Architektur/Plan
    2. Coder: Implementiert den Code
    3. Checker: Reviewt und validiert
    """
    
    def __init__(self, ai_service: AIService):
        self.ai = ai_service
        self.progress_callback: Optional[Callable[[str, int], None]] = None
    
    def set_progress_callback(self, callback: Callable[[str, int], None]):
        """Setzt Callback für Fortschrittsupdates (phase, progress)"""
        self.progress_callback = callback
    
    def _emit_progress(self, phase: str, progress: int):
        if self.progress_callback:
            self.progress_callback(phase, progress)
    
    async def run(self, 
                  task_description: str,
                  project_context: str = "",
                  iterate: bool = True) -> CodeGenerationResult:
        """
        Führt die komplette Entwicklerschleife aus
        
        Args:
            task_description: Was soll entwickelt werden
            project_context: Kontext zum Projekt
            iterate: Bei Problemen iterieren
            
        Returns:
            CodeGenerationResult mit Plan, Code und Review
        """
        result = CodeGenerationResult()
        
        try:
            # Phase 1: Planner
            self._emit_progress("planning", 10)
            plan_response = await self._run_planner(task_description, project_context)
            
            if not plan_response.success:
                result.success = False
                result.error = f"Planner-Fehler: {plan_response.error}"
                return result
            
            result.plan = plan_response.content
            self._emit_progress("planning", 30)
            
            # Phase 2: Coder
            self._emit_progress("coding", 40)
            code_response = await self._run_coder(result.plan, project_context)
            
            if not code_response.success:
                result.success = False
                result.error = f"Coder-Fehler: {code_response.error}"
                return result
            
            result.code = code_response.content
            result.files = self._extract_files(result.code)
            self._emit_progress("coding", 70)
            
            # Phase 3: Checker
            self._emit_progress("checking", 80)
            review_response = await self._run_checker(result.code)
            
            if not review_response.success:
                result.success = False
                result.error = f"Checker-Fehler: {review_response.error}"
                return result
            
            result.review = review_response.content
            self._emit_progress("complete", 100)
            
            return result
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            return result
    
    async def _run_planner(self, task: str, context: str) -> AIResponse:
        """Phase 1: Architektur planen"""
        system = """Du bist ein Software-Architekt.
Erstelle einen strukturierten Entwicklungsplan mit:
1. Übersicht der benötigten Komponenten
2. Datenstrukturen und Klassen
3. Wichtige Methoden und ihre Signaturen
4. Abhängigkeiten und Imports
5. Potentielle Herausforderungen

Sei präzise und technisch."""
        
        prompt = f"""Erstelle einen Entwicklungsplan für:

{task}
"""
        if context:
            prompt += f"""
Projektkontext:
{context}
"""
        
        return await self.ai.complete(prompt, system, use_history=False)
    
    async def _run_coder(self, plan: str, context: str) -> AIResponse:
        """Phase 2: Code implementieren"""
        system = """Du bist ein erfahrener Python-Entwickler.
Implementiere den Code basierend auf dem Plan.
- Schreibe sauberen, gut dokumentierten Code
- Füge Type Hints hinzu
- Behandle Fehler angemessen
- Folge PEP 8

Gib den Code in Markdown-Codeblöcken zurück.
Wenn mehrere Dateien nötig sind, kennzeichne sie mit:
# === DATEI: dateiname.py ==="""
        
        prompt = f"""Implementiere folgenden Plan:

{plan}
"""
        if context:
            prompt += f"""
Zu berücksichtigen:
{context}
"""
        
        return await self.ai.complete(prompt, system, use_history=False)
    
    async def _run_checker(self, code: str) -> AIResponse:
        """Phase 3: Code reviewen"""
        system = """Du bist ein Code-Reviewer und QA-Experte.
Prüfe den Code auf:
1. Korrektheit
2. Best Practices
3. Potentielle Bugs
4. Performance
5. Sicherheit

Gib eine Bewertung (1-10) und konkrete Verbesserungsvorschläge."""
        
        prompt = f"""Reviewe folgenden Code:

{code}
"""
        
        return await self.ai.complete(prompt, system, use_history=False)
    
    def _extract_files(self, code: str) -> List[Dict[str, str]]:
        """Extrahiert Dateien aus der Code-Antwort"""
        files = []
        
        # Nach Datei-Markierungen suchen
        import re
        pattern = r'#\s*===\s*DATEI:\s*(.+?)\s*===\s*\n(.*?)(?=#\s*===\s*DATEI:|$)'
        matches = re.findall(pattern, code, re.DOTALL)
        
        if matches:
            for filename, content in matches:
                files.append({
                    'filename': filename.strip(),
                    'content': content.strip()
                })
        else:
            # Kein Multi-File Format, Code als einzelne Datei
            # Versuche Code aus Markdown zu extrahieren
            code_pattern = r'```python\n(.*?)```'
            code_matches = re.findall(code_pattern, code, re.DOTALL)
            
            if code_matches:
                files.append({
                    'filename': 'generated_code.py',
                    'content': '\n\n'.join(code_matches)
                })
            else:
                files.append({
                    'filename': 'generated_code.py',
                    'content': code
                })
        
        return files


if __name__ == "__main__":
    # Test (benötigt API-Key)
    service = AIService()
    print(f"AI Service verfügbar: {service.is_available()}")
    
    if service.is_available():
        response = service.complete_sync("Sag 'Hallo DevCenter!'")
        print(f"Antwort: {response.content}")

"""
Prompt Generator Module
Generates effective prompts based on Anthropic's best practices for Claude Code.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .core_generator import CoreGenerator
from ..analyzer.repo_analyzer import RepoAnalysis


class TaskType(Enum):
    """Types of tasks that can be performed."""
    BUG_FIX = "bug_fix"
    NEW_FEATURE = "new_feature"
    REFACTOR = "refactor"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    MIGRATION = "migration"
    CONFIGURATION = "configuration"
    DEBUGGING = "debugging"
    CODE_REVIEW = "code_review"
    UNKNOWN = "unknown"


@dataclass
class ClarificationQuestion:
    """A clarification question to ask the user."""
    question: str
    options: List[str] = field(default_factory=list)
    importance: str = "medium"  # low, medium, high
    context: str = ""


@dataclass
class GeneratedPrompt:
    """A generated prompt with metadata."""
    prompt: str
    task_type: TaskType
    approach: str
    tips: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    follow_up_prompts: List[str] = field(default_factory=list)


class PromptGenerator:
    """
    Generates effective prompts based on Anthropic's Claude Code best practices.

    Best Practices Applied:
    1. Be specific and explicit about what you want
    2. Provide context about the codebase
    3. Break complex tasks into smaller steps
    4. Specify the desired output format
    5. Use clear, action-oriented language
    6. Reference specific files or functions when relevant
    7. Set constraints and requirements upfront
    """

    # Task type keywords for classification
    TASK_KEYWORDS = {
        TaskType.BUG_FIX: ["bug", "fix", "error", "issue", "broken", "crash", "fout", "repareer", "kapot"],
        TaskType.NEW_FEATURE: ["add", "create", "implement", "new", "feature", "toevoegen", "nieuw", "maak", "bouw"],
        TaskType.REFACTOR: ["refactor", "clean", "improve", "restructure", "reorganize", "opschonen", "verbeteren"],
        TaskType.OPTIMIZATION: ["optimize", "performance", "speed", "faster", "efficient", "optimaliseer", "sneller"],
        TaskType.DOCUMENTATION: ["document", "readme", "comment", "explain", "documenteer", "uitleggen"],
        TaskType.TESTING: ["test", "unit", "integration", "coverage", "testen"],
        TaskType.MIGRATION: ["migrate", "upgrade", "update", "version", "migreer", "upgrade"],
        TaskType.CONFIGURATION: ["config", "setup", "environment", "settings", "configureer", "instellen"],
        TaskType.DEBUGGING: ["debug", "trace", "log", "inspect", "investigate", "onderzoek"],
        TaskType.CODE_REVIEW: ["review", "check", "audit", "analyse", "beoordeel"],
    }

    # Clarification templates per task type
    CLARIFICATION_TEMPLATES = {
        TaskType.BUG_FIX: [
            ClarificationQuestion(
                question="Kun je de exacte foutmelding of onverwacht gedrag beschrijven?",
                importance="high",
                context="Specifieke foutmeldingen helpen bij het snel lokaliseren van het probleem."
            ),
            ClarificationQuestion(
                question="In welk bestand of component treedt het probleem op?",
                importance="high",
                context="Locatie-informatie versnelt het debuggen."
            ),
            ClarificationQuestion(
                question="Wat zijn de stappen om het probleem te reproduceren?",
                importance="medium",
                context="Reproductie-stappen helpen bij het verifiëren van de fix."
            ),
        ],
        TaskType.NEW_FEATURE: [
            ClarificationQuestion(
                question="Wat is het hoofddoel van deze feature voor de gebruiker?",
                importance="high",
                context="User stories helpen bij het maken van de juiste design keuzes."
            ),
            ClarificationQuestion(
                question="Moet deze feature integreren met bestaande componenten? Welke?",
                importance="medium",
                context="Integratie-vereisten bepalen de aanpak."
            ),
            ClarificationQuestion(
                question="Zijn er specifieke UI/UX vereisten of moet het passen bij bestaande stijl?",
                importance="medium",
                context="Consistentie met bestaand design is belangrijk."
            ),
            ClarificationQuestion(
                question="Zijn er edge cases of error scenarios om rekening mee te houden?",
                importance="medium",
                context="Proactief nadenken over edge cases voorkomt bugs."
            ),
        ],
        TaskType.REFACTOR: [
            ClarificationQuestion(
                question="Wat is het primaire doel van de refactoring? (leesbaarheid, performance, maintainability)",
                importance="high",
                context="Het doel bepaalt welke refactoring patterns toe te passen."
            ),
            ClarificationQuestion(
                question="Moet het externe gedrag exact hetzelfde blijven?",
                importance="high",
                context="Dit bepaalt of breaking changes acceptabel zijn."
            ),
            ClarificationQuestion(
                question="Zijn er specifieke code smells of problemen die je wilt aanpakken?",
                importance="medium",
                context="Gerichte refactoring is effectiever dan algemene 'verbeteringen'."
            ),
        ],
        TaskType.OPTIMIZATION: [
            ClarificationQuestion(
                question="Welk type performance wil je verbeteren? (snelheid, geheugen, bundle size)",
                importance="high",
                context="Verschillende optimalisaties vereisen verschillende aanpakken."
            ),
            ClarificationQuestion(
                question="Heb je metingen of benchmarks van de huidige performance?",
                importance="medium",
                context="Baseline metingen helpen bij het meten van verbetering."
            ),
            ClarificationQuestion(
                question="Zijn er specifieke bottlenecks die je al hebt geidentificeerd?",
                importance="medium",
                context="Bekende bottlenecks geven richting aan de optimalisatie."
            ),
        ],
    }

    # Best practice prompt patterns
    PROMPT_PATTERNS = {
        TaskType.BUG_FIX: """Fix de bug in {context}

**Probleem:** {problem_description}

**Gewenst gedrag:** {expected_behavior}

**Aanpak:**
1. Analyseer eerst de relevante code
2. Identificeer de root cause
3. Implementeer een fix die het probleem oplost zonder regressies
4. Voeg indien nodig een test toe om de fix te verifieren

**Belangrijk:**
- Behoud backwards compatibility
- Minimaliseer de scope van de wijziging""",

        TaskType.NEW_FEATURE: """Implementeer de volgende feature: {feature_description}

**Context:**
{repo_context}

**Vereisten:**
{requirements}

**Aanpak:**
1. Analyseer bestaande code structuur en patronen
2. Ontwerp de implementatie passend bij de huidige architectuur
3. Implementeer incrementeel, beginnend met de core functionaliteit
4. Voeg tests toe voor de nieuwe functionaliteit

**Belangrijk:**
- Volg bestaande code conventies
- Hergebruik bestaande componenten waar mogelijk""",

        TaskType.REFACTOR: """Refactor de volgende code: {target_code}

**Doel:** {refactor_goal}

**Constraints:**
- Behoud exact dezelfde externe interface en gedrag
- Geen breaking changes tenzij expliciet gevraagd

**Aanpak:**
1. Begrijp eerst de huidige implementatie volledig
2. Identificeer de specifieke verbeteringen
3. Refactor incrementeel met kleine, testbare stappen
4. Verifieer dat alle bestaande tests blijven slagen""",

        TaskType.OPTIMIZATION: """Optimaliseer de performance van {target_area}

**Focus:** {optimization_focus}

**Huidige situatie:** {current_state}

**Aanpak:**
1. Profile de huidige performance als baseline
2. Identificeer de grootste bottlenecks
3. Pas gerichte optimalisaties toe
4. Meet en vergelijk met baseline

**Belangrijk:**
- Behoud code leesbaarheid
- Documenteer trade-offs""",
    }

    def __init__(self, analysis: RepoAnalysis, core_generator: CoreGenerator):
        self.analysis = analysis
        self.core_generator = core_generator

    def classify_task(self, user_goal: str) -> TaskType:
        """Classify the user's goal into a task type."""
        goal_lower = user_goal.lower()

        scores = {task_type: 0 for task_type in TaskType}

        for task_type, keywords in self.TASK_KEYWORDS.items():
            for keyword in keywords:
                if keyword in goal_lower:
                    scores[task_type] += 1

        max_score = max(scores.values())
        if max_score > 0:
            for task_type, score in scores.items():
                if score == max_score:
                    return task_type

        return TaskType.UNKNOWN

    def get_clarification_questions(
        self,
        user_goal: str,
        task_type: Optional[TaskType] = None
    ) -> List[ClarificationQuestion]:
        """Get clarification questions based on the task type."""
        if task_type is None:
            task_type = self.classify_task(user_goal)

        questions = []

        # Get task-specific questions
        if task_type in self.CLARIFICATION_TEMPLATES:
            questions.extend(self.CLARIFICATION_TEMPLATES[task_type])

        # Add generic questions based on analysis
        if not self.analysis.test_files:
            questions.append(ClarificationQuestion(
                question="Er zijn geen tests gedetecteerd. Wil je dat ik ook tests toevoeg?",
                options=["Ja", "Nee", "Alleen voor kritieke functionaliteit"],
                importance="low",
                context="Tests helpen bij het valideren van de implementatie."
            ))

        if len(self.analysis.languages) > 1:
            questions.append(ClarificationQuestion(
                question=f"De repository bevat meerdere talen ({', '.join(self.analysis.languages.keys())}). "
                         "Op welk deel focus je?",
                importance="medium",
                context="Duidelijkheid over scope voorkomt onnodige wijzigingen."
            ))

        # Filter high importance first
        questions.sort(key=lambda q: {"high": 0, "medium": 1, "low": 2}[q.importance])

        return questions

    def generate_prompt(
        self,
        user_goal: str,
        clarifications: Optional[Dict[str, str]] = None,
        task_type: Optional[TaskType] = None
    ) -> GeneratedPrompt:
        """Generate an optimized prompt based on the user's goal."""
        if task_type is None:
            task_type = self.classify_task(user_goal)

        # Build context
        repo_context = self.core_generator.get_summary()

        # Generate approach
        approach = self._generate_approach(task_type, user_goal, clarifications)

        # Generate the main prompt
        prompt = self._build_prompt(task_type, user_goal, repo_context, clarifications)

        # Generate tips
        tips = self._generate_tips(task_type)

        # Generate warnings
        warnings = self._generate_warnings(task_type)

        # Generate follow-up prompts
        follow_ups = self._generate_follow_ups(task_type, user_goal)

        return GeneratedPrompt(
            prompt=prompt,
            task_type=task_type,
            approach=approach,
            tips=tips,
            warnings=warnings,
            follow_up_prompts=follow_ups
        )

    def _generate_approach(
        self,
        task_type: TaskType,
        user_goal: str,
        clarifications: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate recommended approach based on best practices."""
        approaches = {
            TaskType.BUG_FIX: """**Aanbevolen aanpak voor bug fixing:**
1. Vraag Claude eerst om de relevante code te lezen en begrijpen
2. Laat Claude de root cause identificeren
3. Vraag om een minimale, gerichte fix
4. Vraag om verificatie dat de fix werkt""",

            TaskType.NEW_FEATURE: """**Aanbevolen aanpak voor nieuwe features:**
1. Begin met een ontwerp/plan fase
2. Laat Claude bestaande patronen analyseren
3. Implementeer in kleine, testbare stappen
4. Review elke stap voordat je doorgaat""",

            TaskType.REFACTOR: """**Aanbevolen aanpak voor refactoring:**
1. Zorg eerst dat alle tests slagen (baseline)
2. Refactor in kleine, atomische stappen
3. Test na elke stap
4. Commit frequent zodat je kunt terugdraaien""",

            TaskType.OPTIMIZATION: """**Aanbevolen aanpak voor optimalisatie:**
1. Meet eerst de huidige performance
2. Identificeer de bottleneck voordat je optimaliseert
3. Pas één optimalisatie tegelijk toe
4. Meet opnieuw en vergelijk""",

            TaskType.UNKNOWN: """**Algemene aanbevolen aanpak:**
1. Begin met context verzamelen
2. Splits complexe taken in kleinere stappen
3. Valideer elke stap voordat je doorgaat
4. Wees specifiek over gewenste output"""
        }

        return approaches.get(task_type, approaches[TaskType.UNKNOWN])

    def _build_prompt(
        self,
        task_type: TaskType,
        user_goal: str,
        repo_context: str,
        clarifications: Optional[Dict[str, str]] = None
    ) -> str:
        """Build the optimized prompt."""
        parts = []

        # Add repository context
        parts.append(f"**Repository Context:**\n{repo_context}")
        parts.append("")

        # Add main task
        parts.append(f"**Taak:** {user_goal}")
        parts.append("")

        # Add clarifications if provided
        if clarifications:
            parts.append("**Aanvullende informatie:**")
            for question, answer in clarifications.items():
                parts.append(f"- {question}: {answer}")
            parts.append("")

        # Add task-specific structure
        if task_type == TaskType.BUG_FIX:
            parts.append("""**Gewenste aanpak:**
1. Lees eerst de relevante code om het probleem te begrijpen
2. Identificeer de root cause van het probleem
3. Implementeer een minimale fix
4. Leg uit welke wijzigingen je hebt gemaakt en waarom""")

        elif task_type == TaskType.NEW_FEATURE:
            parts.append("""**Gewenste aanpak:**
1. Analyseer bestaande code structuur en patronen
2. Geef eerst een kort plan van aanpak
3. Implementeer de feature stap voor stap
4. Volg bestaande code conventies""")

        elif task_type == TaskType.REFACTOR:
            parts.append("""**Gewenste aanpak:**
1. Analyseer de huidige implementatie
2. Behoud externe interface en gedrag
3. Refactor in kleine, verifieerbare stappen
4. Leg de verbeteringen uit""")

        elif task_type == TaskType.OPTIMIZATION:
            parts.append("""**Gewenste aanpak:**
1. Identificeer performance bottlenecks
2. Stel concrete optimalisaties voor
3. Leg de trade-offs uit
4. Behoud code leesbaarheid""")

        else:
            parts.append("""**Gewenste aanpak:**
1. Analyseer eerst de relevante code
2. Geef een duidelijk plan
3. Implementeer stap voor stap
4. Valideer het resultaat""")

        parts.append("")

        # Add output expectations
        parts.append("""**Verwachte output:**
- Duidelijke uitleg van de wijzigingen
- Werkende code die past bij de bestaande stijl
- Eventuele waarschuwingen of aandachtspunten""")

        return "\n".join(parts)

    def _generate_tips(self, task_type: TaskType) -> List[str]:
        """Generate tips based on Anthropic best practices."""
        common_tips = [
            "Wees specifiek: noem exacte bestanden of functies waar mogelijk",
            "Vraag Claude om eerst te lezen voordat het wijzigt",
            "Splits complexe taken in meerdere prompts",
        ]

        specific_tips = {
            TaskType.BUG_FIX: [
                "Deel de exacte foutmelding als je die hebt",
                "Beschrijf stappen om het probleem te reproduceren",
            ],
            TaskType.NEW_FEATURE: [
                "Beschrijf de user story of use case",
                "Geef voorbeelden van verwacht gedrag",
            ],
            TaskType.REFACTOR: [
                "Specificeer wat je wilt verbeteren (leesbaarheid, performance, etc.)",
                "Geef aan of breaking changes acceptabel zijn",
            ],
            TaskType.OPTIMIZATION: [
                "Deel performance metingen als je die hebt",
                "Specificeer het type optimalisatie (snelheid, geheugen, etc.)",
            ],
        }

        tips = common_tips.copy()
        if task_type in specific_tips:
            tips.extend(specific_tips[task_type])

        return tips

    def _generate_warnings(self, task_type: TaskType) -> List[str]:
        """Generate warnings based on the task type and repository."""
        warnings = []

        if task_type == TaskType.REFACTOR and self.analysis.test_files:
            warnings.append("Let op: er zijn tests aanwezig. Zorg dat deze blijven slagen.")

        if task_type == TaskType.MIGRATION:
            warnings.append("Migraties kunnen breaking changes introduceren. Test grondig.")

        if not self.analysis.test_files:
            warnings.append("Geen tests gedetecteerd. Overweeg handmatig te testen.")

        if self.analysis.total_lines > 50000:
            warnings.append("Grote codebase: wees specifiek over welke delen te wijzigen.")

        return warnings

    def _generate_follow_ups(self, task_type: TaskType, user_goal: str) -> List[str]:
        """Generate follow-up prompts for iterative development."""
        follow_ups = {
            TaskType.BUG_FIX: [
                "Kun je een test toevoegen die verifieert dat deze bug niet terugkomt?",
                "Zijn er vergelijkbare patronen in de code die hetzelfde probleem kunnen hebben?",
            ],
            TaskType.NEW_FEATURE: [
                "Kun je edge cases en error handling toevoegen?",
                "Voeg tests toe voor de nieuwe functionaliteit",
                "Update de documentatie voor deze feature",
            ],
            TaskType.REFACTOR: [
                "Zijn er nog meer plekken waar we dit patroon kunnen toepassen?",
                "Kun je documentatie toevoegen voor de gerefactorde code?",
            ],
            TaskType.OPTIMIZATION: [
                "Kun je de performance verbetering meten en vergelijken?",
                "Zijn er andere bottlenecks die we kunnen aanpakken?",
            ],
        }

        return follow_ups.get(task_type, [
            "Is het resultaat wat je verwachtte?",
            "Zijn er aanpassingen nodig?",
        ])

    def get_quick_prompt(self, user_goal: str) -> str:
        """Generate a quick, well-structured prompt without full analysis."""
        task_type = self.classify_task(user_goal)
        repo_summary = self.core_generator.get_summary()

        return f"""[Repository: {self.analysis.name}]

{user_goal}

Context: {repo_summary}

Lees eerst de relevante code en geef dan een duidelijk plan voordat je wijzigingen maakt."""

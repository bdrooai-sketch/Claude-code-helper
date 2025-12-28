"""
Core Generator Module
Generates a core knowledge file that provides Claude with a complete overview of the repository.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..analyzer.repo_analyzer import RepoAnalysis


class CoreGenerator:
    """Generates a core knowledge file for repository understanding."""

    CORE_FILE_NAME = ".claude-context.md"

    def __init__(self, analysis: RepoAnalysis):
        self.analysis = analysis

    def generate(self, output_path: Optional[str] = None) -> str:
        """Generate the core knowledge file content."""
        content = self._build_core_content()

        if output_path:
            path = Path(output_path)
            path.write_text(content, encoding='utf-8')
        else:
            # Write to repository root
            path = Path(self.analysis.root_path) / self.CORE_FILE_NAME
            path.write_text(content, encoding='utf-8')

        return content

    def _build_core_content(self) -> str:
        """Build the core knowledge file content."""
        sections = [
            self._build_header(),
            self._build_overview(),
            self._build_tech_stack(),
            self._build_architecture(),
            self._build_key_files(),
            self._build_patterns(),
            self._build_guidelines(),
        ]

        return "\n\n".join(filter(None, sections))

    def _build_header(self) -> str:
        """Build the header section."""
        return f"""# Repository Context: {self.analysis.name}

> Dit bestand is automatisch gegenereerd door Claude Code Helper.
> Het biedt Claude een volledig overzicht van de repository.
> Laatst bijgewerkt: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---"""

    def _build_overview(self) -> str:
        """Build the overview section."""
        primary_lang = list(self.analysis.languages.keys())[0] if self.analysis.languages else "Onbekend"

        return f"""## Project Overzicht

- **Naam**: {self.analysis.name}
- **Primaire taal**: {primary_lang}
- **Totaal bestanden**: {self.analysis.total_files}
- **Totaal regels code**: {self.analysis.total_lines:,}
- **Pad**: `{self.analysis.root_path}`"""

    def _build_tech_stack(self) -> str:
        """Build the technology stack section."""
        lines = ["## Technologie Stack"]

        if self.analysis.languages:
            lines.append("\n### Programmeertalen")
            for lang, count in self.analysis.languages.items():
                lines.append(f"- **{lang}**: {count} bestanden")

        if self.analysis.frameworks:
            lines.append("\n### Frameworks")
            for framework in self.analysis.frameworks:
                lines.append(f"- {framework}")

        if self.analysis.technologies:
            lines.append("\n### Technologieen & Tools")
            for tech in self.analysis.technologies:
                lines.append(f"- {tech}")

        return "\n".join(lines)

    def _build_architecture(self) -> str:
        """Build the architecture section."""
        lines = ["## Architectuur & Structuur"]

        # Top-level directories
        if self.analysis.structure.get("directories"):
            lines.append("\n### Hoofdmappen")
            dirs = self.analysis.structure["directories"]
            for dir_name, info in sorted(dirs.items()):
                count = info.get("file_count", 0)
                lines.append(f"- `{dir_name}/` ({count} bestanden)")

        # Entry points
        if self.analysis.entry_points:
            lines.append("\n### Entry Points")
            for entry in self.analysis.entry_points[:5]:
                lines.append(f"- `{entry}`")

        return "\n".join(lines)

    def _build_key_files(self) -> str:
        """Build the key files section."""
        lines = ["## Belangrijke Bestanden"]

        if self.analysis.key_files:
            lines.append("\n### Kernbestanden")
            for file in self.analysis.key_files:
                lines.append(f"- `{file}`")

        if self.analysis.config_files:
            lines.append("\n### Configuratiebestanden")
            for config in self.analysis.config_files[:10]:
                lines.append(f"- `{config}`")

        if self.analysis.test_files:
            lines.append(f"\n### Tests")
            lines.append(f"- {len(self.analysis.test_files)} test bestanden gevonden")
            for test in self.analysis.test_files[:5]:
                lines.append(f"  - `{test}`")

        if self.analysis.documentation:
            lines.append("\n### Documentatie")
            for doc in self.analysis.documentation[:5]:
                lines.append(f"- `{doc}`")

        return "\n".join(lines)

    def _build_patterns(self) -> str:
        """Build the patterns section based on detected conventions."""
        lines = ["## Gedetecteerde Patronen"]

        # Infer patterns from structure
        patterns = []

        # Check for common patterns
        struct = self.analysis.structure.get("directories", {})
        dir_names = set(struct.keys())

        if "src" in dir_names or "lib" in dir_names:
            patterns.append("- **Source structuur**: Code in `src/` of `lib/` map")

        if "tests" in dir_names or "test" in dir_names or "__tests__" in dir_names:
            patterns.append("- **Test structuur**: Aparte test directory")

        if "components" in dir_names:
            patterns.append("- **Component-based**: UI componenten in aparte map")

        if "api" in dir_names or "routes" in dir_names:
            patterns.append("- **API structuur**: API routes in dedicated map")

        if "models" in dir_names or "schemas" in dir_names:
            patterns.append("- **Data models**: Models/schemas in aparte map")

        if "utils" in dir_names or "helpers" in dir_names:
            patterns.append("- **Utilities**: Helper functies in utils map")

        if patterns:
            lines.extend(patterns)
        else:
            lines.append("- Geen specifieke patronen gedetecteerd")

        return "\n".join(lines)

    def _build_guidelines(self) -> str:
        """Build guidelines for working with this repository."""
        lines = ["## Richtlijnen voor Claude"]

        lines.append("""
### Bij het werken met deze repository:

1. **Behoud consistentie**: Volg de bestaande code stijl en patronen
2. **Respecteer de structuur**: Plaats nieuwe bestanden op logische locaties
3. **Test bewustzijn**: Houd rekening met bestaande tests bij wijzigingen
4. **Configuratie**: Bekijk config bestanden voor project-specifieke instellingen

### Aanbevolen aanpak:

1. Lees eerst relevante bestaande code voordat je wijzigingen voorstelt
2. Identificeer afhankelijkheden en mogelijke impact
3. Stel incrementele wijzigingen voor waar mogelijk
4. Overweeg backwards compatibility""")

        return "\n".join(lines)

    def get_summary(self) -> str:
        """Get a brief summary for use in prompts."""
        primary_lang = list(self.analysis.languages.keys())[0] if self.analysis.languages else "Unknown"
        frameworks_str = ", ".join(self.analysis.frameworks) if self.analysis.frameworks else "geen specifiek framework"

        return f"""Repository: {self.analysis.name}
Taal: {primary_lang} ({self.analysis.total_files} bestanden, {self.analysis.total_lines:,} regels)
Frameworks: {frameworks_str}
Technologieen: {", ".join(self.analysis.technologies) if self.analysis.technologies else "geen specifieke technologieen gedetecteerd"}"""

    def to_json(self) -> str:
        """Export the analysis as JSON for programmatic use."""
        return json.dumps(self.analysis.to_dict(), indent=2, ensure_ascii=False)

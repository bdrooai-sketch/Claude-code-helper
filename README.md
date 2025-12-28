# Claude Code Helper

Een tool die je helpt effectieve prompts te genereren voor Claude Code, gebaseerd op analyse van je repository.

## Features

- **Repository Analyse**: Analyseert automatisch je codebase (talen, frameworks, structuur)
- **Kernbestand Generator**: Creëert een `.claude-context.md` bestand dat Claude context geeft
- **Prompt Generator**: Genereert geoptimaliseerde prompts gebaseerd op Anthropic best-practices
- **Interactieve Doorvraag**: Stelt verduidelijkingsvragen voor betere prompts
- **Taakherkenning**: Herkent automatisch het type taak (bug fix, feature, refactor, etc.)

## Installatie

```bash
# Clone de repository
git clone https://github.com/your-repo/claude-code-helper.git
cd claude-code-helper

# Installeer dependencies
pip install -r requirements.txt

# Of installeer als package
pip install -e .
```

## Gebruik

### Snelle Start

```bash
# Analyseer huidige directory
python main.py analyze

# Genereer een prompt voor een doel
python main.py prompt --goal "Voeg een login functie toe"

# Start interactieve modus
python main.py interactive
```

### Commando's

#### `analyze`
Analyseert een repository en genereert een kernbestand.

```bash
python main.py analyze /pad/naar/repo
python main.py analyze --output custom-context.md
```

#### `prompt`
Genereert een geoptimaliseerde prompt voor je doel.

```bash
python main.py prompt /pad/naar/repo --goal "Fix de authentication bug"
python main.py prompt --quick --goal "Voeg dark mode toe"
```

#### `interactive`
Start een interactieve sessie voor het genereren van meerdere prompts.

```bash
python main.py interactive /pad/naar/repo
```

#### `tips`
Toont best practices voor het gebruik van Claude Code.

```bash
python main.py tips
```

## Hoe Het Werkt

### 1. Repository Analyse
De tool analyseert je repository om te begrijpen:
- Welke programmeertalen worden gebruikt
- Welke frameworks zijn geïnstalleerd
- De mappenstructuur en organisatie
- Belangrijke bestanden (entry points, configs, tests)

### 2. Kernbestand Generatie
Er wordt een `.claude-context.md` bestand gegenereerd met:
- Project overzicht
- Technologie stack
- Architectuur informatie
- Belangrijke bestanden
- Richtlijnen voor Claude

### 3. Prompt Generatie
Op basis van je doel en de analyse:
- Classificeert de tool het type taak
- Stelt verduidelijkingsvragen
- Genereert een gestructureerde prompt
- Geeft tips en aanbevolen aanpak

## Best Practices (geïntegreerd)

De tool past automatisch Anthropic's best practices toe:

1. **Specificiteit**: Prompts bevatten concrete context
2. **Structuur**: Gestructureerde aanpak per taaktype
3. **Context**: Repository informatie wordt meegeleverd
4. **Iteratie**: Suggesties voor vervolgprompts

## Voorbeeld Output

```
┌─────────────────────────────────────────┐
│ Gedetecteerd taaktype: New Feature      │
└─────────────────────────────────────────┘

Aanbevolen Aanpak:
1. Begin met een ontwerp/plan fase
2. Laat Claude bestaande patronen analyseren
3. Implementeer in kleine, testbare stappen
4. Review elke stap voordat je doorgaat

┌─────────────────────────────────────────────┐
│ **Repository Context:**                     │
│ Repository: my-app                          │
│ Taal: TypeScript (150 bestanden)            │
│ Frameworks: React, Next.js                  │
│                                             │
│ **Taak:** Voeg een dark mode toggle toe     │
│                                             │
│ **Gewenste aanpak:**                        │
│ 1. Analyseer bestaande code structuur       │
│ 2. Geef eerst een kort plan van aanpak      │
│ 3. Implementeer de feature stap voor stap   │
│ 4. Volg bestaande code conventies           │
└─────────────────────────────────────────────┘

Tips:
  • Wees specifiek: noem exacte bestanden
  • Beschrijf de user story of use case
  • Geef voorbeelden van verwacht gedrag
```

## Structuur

```
claude-code-helper/
├── main.py              # Entry point
├── src/
│   ├── __init__.py
│   ├── cli.py           # CLI interface
│   ├── analyzer/
│   │   ├── __init__.py
│   │   └── repo_analyzer.py
│   └── generator/
│       ├── __init__.py
│       ├── core_generator.py
│       └── prompt_generator.py
├── requirements.txt
└── pyproject.toml
```

## Licentie

MIT

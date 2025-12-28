"""
Repository Analyzer Module
Analyzes a repository to understand its structure, technologies, and patterns.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import fnmatch


@dataclass
class RepoAnalysis:
    """Data class containing repository analysis results."""

    root_path: str
    name: str
    technologies: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    languages: Dict[str, int] = field(default_factory=dict)  # language -> file count
    structure: Dict[str, any] = field(default_factory=dict)
    key_files: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    documentation: List[str] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0

    def to_dict(self) -> Dict:
        return {
            "root_path": self.root_path,
            "name": self.name,
            "technologies": self.technologies,
            "frameworks": self.frameworks,
            "languages": self.languages,
            "structure": self.structure,
            "key_files": self.key_files,
            "entry_points": self.entry_points,
            "config_files": self.config_files,
            "test_files": self.test_files,
            "documentation": self.documentation,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
        }


class RepoAnalyzer:
    """Analyzes repositories to extract structure and technology information."""

    # File extensions to language mapping
    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript (React)",
        ".jsx": "JavaScript (React)",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".vue": "Vue",
        ".svelte": "Svelte",
    }

    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        "React": ["react", "package.json:react"],
        "Vue": ["vue", "package.json:vue"],
        "Angular": ["angular", "@angular"],
        "Django": ["django", "settings.py", "urls.py"],
        "Flask": ["flask", "app.py"],
        "FastAPI": ["fastapi"],
        "Express": ["express"],
        "Next.js": ["next.config", "package.json:next"],
        "NestJS": ["@nestjs"],
        "Spring": ["spring", "pom.xml"],
        "Rails": ["rails", "Gemfile"],
        "Laravel": ["laravel", "artisan"],
    }

    # Config file patterns
    CONFIG_PATTERNS = [
        "*.config.*", "*.json", "*.yaml", "*.yml", "*.toml",
        ".env*", "Dockerfile*", "docker-compose*",
        "package.json", "pyproject.toml", "Cargo.toml",
        "go.mod", "Gemfile", "pom.xml", "build.gradle",
        ".eslintrc*", ".prettierrc*", "tsconfig.json",
    ]

    # Entry point patterns
    ENTRY_POINT_PATTERNS = [
        "main.*", "index.*", "app.*", "server.*",
        "__main__.py", "manage.py", "cli.*",
    ]

    # Ignore patterns
    IGNORE_PATTERNS = [
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", ".nuxt", "target",
        "*.pyc", "*.pyo", ".DS_Store", "*.egg-info",
    ]

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def analyze(self) -> RepoAnalysis:
        """Perform full repository analysis."""
        analysis = RepoAnalysis(
            root_path=str(self.repo_path),
            name=self.repo_path.name,
        )

        # Collect all files
        all_files = self._collect_files()
        analysis.total_files = len(all_files)

        # Analyze languages
        analysis.languages = self._analyze_languages(all_files)

        # Detect frameworks and technologies
        analysis.frameworks = self._detect_frameworks(all_files)
        analysis.technologies = self._detect_technologies(all_files)

        # Categorize files
        analysis.config_files = self._find_config_files(all_files)
        analysis.entry_points = self._find_entry_points(all_files)
        analysis.test_files = self._find_test_files(all_files)
        analysis.documentation = self._find_documentation(all_files)
        analysis.key_files = self._identify_key_files(all_files, analysis)

        # Build structure
        analysis.structure = self._build_structure(all_files)

        # Count lines
        analysis.total_lines = self._count_lines(all_files)

        return analysis

    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        path_str = str(path)
        for pattern in self.IGNORE_PATTERNS:
            if fnmatch.fnmatch(path.name, pattern):
                return True
            if pattern in path_str:
                return True
        return False

    def _collect_files(self) -> List[Path]:
        """Collect all relevant files in the repository."""
        files = []
        for root, dirs, filenames in os.walk(self.repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(Path(root) / d)]

            for filename in filenames:
                file_path = Path(root) / filename
                if not self._should_ignore(file_path):
                    files.append(file_path)

        return files

    def _analyze_languages(self, files: List[Path]) -> Dict[str, int]:
        """Analyze which programming languages are used."""
        languages = {}
        for file in files:
            ext = file.suffix.lower()
            if ext in self.LANGUAGE_MAP:
                lang = self.LANGUAGE_MAP[ext]
                languages[lang] = languages.get(lang, 0) + 1
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))

    def _detect_frameworks(self, files: List[Path]) -> List[str]:
        """Detect which frameworks are used in the repository."""
        detected = set()
        file_contents_cache = {}

        # Check package.json for JS/TS frameworks
        package_json = self.repo_path / "package.json"
        if package_json.exists():
            try:
                content = package_json.read_text()
                file_contents_cache["package.json"] = content.lower()
            except:
                pass

        # Check requirements.txt/pyproject.toml for Python frameworks
        for req_file in ["requirements.txt", "pyproject.toml"]:
            req_path = self.repo_path / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text()
                    file_contents_cache[req_file] = content.lower()
                except:
                    pass

        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if ":" in pattern:
                    filename, search = pattern.split(":", 1)
                    if filename in file_contents_cache:
                        if search.lower() in file_contents_cache[filename]:
                            detected.add(framework)
                            break
                else:
                    # Check in file contents cache
                    for content in file_contents_cache.values():
                        if pattern.lower() in content:
                            detected.add(framework)
                            break
                    # Check file names
                    for file in files:
                        if pattern.lower() in file.name.lower():
                            detected.add(framework)
                            break

        return sorted(list(detected))

    def _detect_technologies(self, files: List[Path]) -> List[str]:
        """Detect technologies used (Docker, CI/CD, etc.)."""
        technologies = set()

        file_names = {f.name.lower() for f in files}

        if any("dockerfile" in f for f in file_names):
            technologies.add("Docker")
        if any("docker-compose" in f for f in file_names):
            technologies.add("Docker Compose")
        if any(".github" in str(f) for f in files):
            technologies.add("GitHub Actions")
        if any(".gitlab-ci" in f for f in file_names):
            technologies.add("GitLab CI")
        if any("jenkinsfile" in f for f in file_names):
            technologies.add("Jenkins")
        if any("terraform" in f or f.endswith(".tf") for f in file_names):
            technologies.add("Terraform")
        if any("kubernetes" in f or f.endswith(".k8s") for f in file_names):
            technologies.add("Kubernetes")
        if "package.json" in file_names:
            technologies.add("npm/Node.js")
        if "pyproject.toml" in file_names or "setup.py" in file_names:
            technologies.add("Python Package")
        if "cargo.toml" in file_names:
            technologies.add("Cargo/Rust")
        if "go.mod" in file_names:
            technologies.add("Go Modules")

        return sorted(list(technologies))

    def _find_config_files(self, files: List[Path]) -> List[str]:
        """Find configuration files."""
        configs = []
        for file in files:
            rel_path = file.relative_to(self.repo_path)
            for pattern in self.CONFIG_PATTERNS:
                if fnmatch.fnmatch(file.name, pattern):
                    configs.append(str(rel_path))
                    break
        return sorted(configs)[:20]  # Limit to top 20

    def _find_entry_points(self, files: List[Path]) -> List[str]:
        """Find likely entry points."""
        entry_points = []
        for file in files:
            rel_path = file.relative_to(self.repo_path)
            for pattern in self.ENTRY_POINT_PATTERNS:
                if fnmatch.fnmatch(file.name, pattern):
                    entry_points.append(str(rel_path))
                    break
        return sorted(entry_points)

    def _find_test_files(self, files: List[Path]) -> List[str]:
        """Find test files."""
        tests = []
        for file in files:
            rel_path = file.relative_to(self.repo_path)
            path_str = str(rel_path).lower()
            if "test" in path_str or "spec" in path_str:
                tests.append(str(rel_path))
        return sorted(tests)[:20]  # Limit to top 20

    def _find_documentation(self, files: List[Path]) -> List[str]:
        """Find documentation files."""
        docs = []
        for file in files:
            if file.suffix.lower() in [".md", ".rst", ".txt"]:
                if file.name.lower() in ["readme.md", "changelog.md", "contributing.md", "license.md"]:
                    docs.append(str(file.relative_to(self.repo_path)))
            if "docs" in str(file.relative_to(self.repo_path)).lower():
                docs.append(str(file.relative_to(self.repo_path)))
        return sorted(set(docs))[:20]

    def _identify_key_files(self, files: List[Path], analysis: RepoAnalysis) -> List[str]:
        """Identify key files that are important for understanding the codebase."""
        key_files = set()

        # Add entry points
        key_files.update(analysis.entry_points[:5])

        # Add main config files
        important_configs = [
            "package.json", "pyproject.toml", "Cargo.toml", "go.mod",
            "tsconfig.json", "webpack.config.js", "vite.config.ts",
        ]
        for config in analysis.config_files:
            if any(cfg in config for cfg in important_configs):
                key_files.add(config)

        # Add README
        for file in files:
            if file.name.lower() == "readme.md":
                key_files.add(str(file.relative_to(self.repo_path)))
                break

        return sorted(list(key_files))[:15]

    def _build_structure(self, files: List[Path]) -> Dict:
        """Build a tree structure of the repository."""
        structure = {"directories": {}, "file_count": 0}

        for file in files:
            rel_path = file.relative_to(self.repo_path)
            parts = rel_path.parts

            current = structure["directories"]
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {"directories": {}, "file_count": 0}
                current[part]["file_count"] += 1
                current = current[part]["directories"]

        structure["file_count"] = len(files)
        return structure

    def _count_lines(self, files: List[Path]) -> int:
        """Count total lines of code."""
        total = 0
        code_extensions = set(self.LANGUAGE_MAP.keys())

        for file in files:
            if file.suffix.lower() in code_extensions:
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        total += sum(1 for _ in f)
                except:
                    pass

        return total

    def get_file_content(self, relative_path: str) -> Optional[str]:
        """Get the content of a specific file."""
        file_path = self.repo_path / relative_path
        if file_path.exists():
            try:
                return file_path.read_text(encoding='utf-8', errors='ignore')
            except:
                return None
        return None

    def get_directory_listing(self, relative_path: str = "") -> List[str]:
        """Get a listing of files in a directory."""
        dir_path = self.repo_path / relative_path if relative_path else self.repo_path
        if not dir_path.is_dir():
            return []

        items = []
        for item in sorted(dir_path.iterdir()):
            if not self._should_ignore(item):
                rel = item.relative_to(self.repo_path)
                prefix = "[D]" if item.is_dir() else "[F]"
                items.append(f"{prefix} {rel}")

        return items

# -*- coding: utf-8 -*-
"""
DevCenter - Method Analyzer
Statische Code-Analyse für Python-Dateien
Basierend auf MethodenAnalyser V3
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class MethodInfo:
    """Informationen über eine Methode/Funktion"""
    name: str
    line: int
    end_line: int
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    is_async: bool = False
    complexity: int = 1


@dataclass
class ClassInfo:
    """Informationen über eine Klasse"""
    name: str
    line: int
    end_line: int
    bases: List[str]
    docstring: Optional[str]
    decorators: List[str]
    methods: List[MethodInfo] = field(default_factory=list)


@dataclass
class ImportInfo:
    """Informationen über einen Import"""
    module: str
    names: List[str]
    line: int
    is_from_import: bool
    alias: Optional[str] = None


@dataclass
class AnalysisResult:
    """Ergebnis der Code-Analyse"""
    file_path: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[MethodInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    
    unused_imports: Set[str] = field(default_factory=set)
    undefined_names: Set[str] = field(default_factory=set)


class ComplexityVisitor(ast.NodeVisitor):
    """Berechnet die zyklomatische Komplexität"""
    
    def __init__(self):
        self.complexity = 1
    
    def visit_If(self, node):
        """Zaehlt if-Verzweigung als Komplexitaetspunkt."""
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        """Zaehlt for-Schleife als Komplexitaetspunkt."""
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        """Zaehlt while-Schleife als Komplexitaetspunkt."""
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        """Zaehlt except-Block als Komplexitaetspunkt."""
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        """Zaehlt with-Block als Komplexitaetspunkt."""
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Zaehlt boolesche Operatoren als Komplexitaetspunkte."""
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_comprehension(self, node):
        """Zaehlt Comprehension als Komplexitaetspunkt."""
        self.complexity += 1
        self.generic_visit(node)


class NameCollector(ast.NodeVisitor):
    """Sammelt alle verwendeten Namen im Code"""
    
    def __init__(self):
        self.used_names: Set[str] = set()
        self.defined_names: Set[str] = set()
        self.imported_names: Set[str] = set()
    
    def visit_Name(self, node):
        """Sammelt verwendete und definierte Variablennamen."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.defined_names.add(node.id)
        self.generic_visit(node)

    def visit_Import(self, node):
        """Sammelt importierte Namen aus import-Anweisungen."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            self.imported_names.add(name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Sammelt importierte Namen aus from-import-Anweisungen."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names.add(name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Sammelt Funktionsnamen und deren Argumente."""
        self.defined_names.add(node.name)
        for arg in node.args.args:
            self.defined_names.add(arg.arg)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Delegiert an visit_FunctionDef fuer async-Funktionen."""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        """Sammelt Klassennamen."""
        self.defined_names.add(node.name)
        self.generic_visit(node)


class MethodAnalyzer:
    """
    Hauptklasse für statische Code-Analyse
    
    Analysiert Python-Dateien auf:
    - Klassen und Methoden
    - Importe (verwendet/ungenutzt)
    - Komplexität
    - Potentielle Probleme
    """
    
    # Standard-Builtins die immer verfügbar sind
    BUILTINS = {
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray',
        'bytes', 'callable', 'chr', 'classmethod', 'compile', 'complex',
        'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec',
        'filter', 'float', 'format', 'frozenset', 'getattr', 'globals',
        'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
        'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
        'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow',
        'print', 'property', 'range', 'repr', 'reversed', 'round', 'set',
        'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super',
        'tuple', 'type', 'vars', 'zip', '__import__', '__name__', '__file__',
        '__doc__', '__package__', 'True', 'False', 'None', 'Ellipsis',
        'NotImplemented', 'Exception', 'BaseException', 'TypeError', 'ValueError',
        'KeyError', 'IndexError', 'AttributeError', 'ImportError', 'OSError',
        'FileNotFoundError', 'RuntimeError', 'StopIteration', 'GeneratorExit',
        'AssertionError', 'NameError', 'ZeroDivisionError', 'OverflowError',
        'MemoryError', 'RecursionError', 'SystemExit', 'KeyboardInterrupt'
    }
    
    def __init__(self):
        self.current_file: Optional[str] = None
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Analysiert eine Python-Datei
        
        Args:
            file_path: Pfad zur Python-Datei
            
        Returns:
            AnalysisResult mit allen Analysedaten
        """
        self.current_file = file_path
        result = AnalysisResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            result.errors.append({
                'type': 'FileError',
                'message': f"Datei konnte nicht gelesen werden: {e}",
                'line': 0
            })
            return result
        
        # Zeilen-Statistiken
        lines = source.split('\n')
        result.total_lines = len(lines)
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result.blank_lines += 1
            elif stripped.startswith('#'):
                result.comment_lines += 1
            else:
                result.code_lines += 1
        
        # AST parsen
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            result.errors.append({
                'type': 'SyntaxError',
                'message': str(e.msg),
                'line': e.lineno or 0,
                'column': e.offset or 0
            })
            return result
        
        # Analyse durchführen
        self._analyze_imports(tree, result)
        self._analyze_classes(tree, result)
        self._analyze_functions(tree, result)
        self._analyze_names(tree, result)
        self._check_common_issues(tree, result, source)
        
        return result
    
    def _analyze_imports(self, tree: ast.AST, result: AnalysisResult):
        """Analysiert Imports"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result.imports.append(ImportInfo(
                        module=alias.name,
                        names=[],
                        line=node.lineno,
                        is_from_import=False,
                        alias=alias.asname
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = [alias.name for alias in node.names]
                result.imports.append(ImportInfo(
                    module=module,
                    names=names,
                    line=node.lineno,
                    is_from_import=True
                ))
    
    def _analyze_classes(self, tree: ast.AST, result: AnalysisResult):
        """Analysiert Klassen"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = ClassInfo(
                    name=node.name,
                    line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    bases=[self._get_name(base) for base in node.bases],
                    docstring=ast.get_docstring(node),
                    decorators=[self._get_decorator_name(d) for d in node.decorator_list]
                )
                
                # Methoden der Klasse
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_info = self._analyze_function(item)
                        class_info.methods.append(method_info)
                
                result.classes.append(class_info)
    
    def _analyze_functions(self, tree: ast.AST, result: AnalysisResult):
        """Analysiert Top-Level Funktionen"""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.functions.append(self._analyze_function(node))
    
    def _analyze_function(self, node) -> MethodInfo:
        """Analysiert eine einzelne Funktion"""
        # Argumente
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {self._get_annotation(arg.annotation)}"
            args.append(arg_str)
        
        # Rückgabetyp
        returns = None
        if node.returns:
            returns = self._get_annotation(node.returns)
        
        # Komplexität
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(node)
        
        return MethodInfo(
            name=node.name,
            line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            args=args,
            returns=returns,
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            is_async=isinstance(node, ast.AsyncFunctionDef),
            complexity=complexity_visitor.complexity
        )
    
    def _analyze_names(self, tree: ast.AST, result: AnalysisResult):
        """Analysiert Namensverwendung für ungenutzte Imports"""
        collector = NameCollector()
        collector.visit(tree)
        
        # Ungenutzte Imports finden
        for imp in result.imports:
            if imp.is_from_import:
                for name in imp.names:
                    if name not in collector.used_names and name != '*':
                        result.unused_imports.add(f"{imp.module}.{name}")
            else:
                name = imp.alias or imp.module.split('.')[0]
                if name not in collector.used_names:
                    result.unused_imports.add(imp.module)
        
        # Undefinierte Namen (mit Vorsicht - kann False Positives haben)
        all_defined = collector.defined_names | collector.imported_names | self.BUILTINS
        for name in collector.used_names:
            if name not in all_defined:
                result.undefined_names.add(name)
    
    def _check_common_issues(self, tree: ast.AST, result: AnalysisResult, source: str):
        """Prüft auf häufige Code-Probleme"""
        
        for node in ast.walk(tree):
            # Bare except
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    result.warnings.append({
                        'type': 'BareExcept',
                        'message': 'Bare except: gefunden - sollte spezifische Exception angeben',
                        'line': node.lineno
                    })
            
            # Mutable Default Arguments
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        result.warnings.append({
                            'type': 'MutableDefault',
                            'message': f'Mutable Default-Argument in {node.name}()',
                            'line': node.lineno
                        })
            
            # Zu komplexe Funktionen
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                cv = ComplexityVisitor()
                cv.visit(node)
                if cv.complexity > 10:
                    result.warnings.append({
                        'type': 'HighComplexity',
                        'message': f'Hohe Komplexität ({cv.complexity}) in {node.name}()',
                        'line': node.lineno
                    })
            
            # TODO-Kommentare finden
            pass  # Wird über Source-Lines gemacht
        
        # TODO/FIXME in Kommentaren
        for i, line in enumerate(source.split('\n'), 1):
            if '#' in line:
                comment = line.split('#', 1)[1]
                if 'TODO' in comment.upper():
                    result.warnings.append({
                        'type': 'TODO',
                        'message': f'TODO gefunden: {comment.strip()[:50]}...',
                        'line': i
                    })
                elif 'FIXME' in comment.upper():
                    result.warnings.append({
                        'type': 'FIXME',
                        'message': f'FIXME gefunden: {comment.strip()[:50]}...',
                        'line': i
                    })
    
    def _get_name(self, node) -> str:
        """Extrahiert einen Namen aus einem AST-Knoten"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        return str(type(node).__name__)
    
    def _get_annotation(self, node) -> str:
        """Extrahiert eine Type-Annotation"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Subscript):
            base = self._get_annotation(node.value)
            if isinstance(node.slice, ast.Tuple):
                args = ", ".join(self._get_annotation(e) for e in node.slice.elts)
            else:
                args = self._get_annotation(node.slice)
            return f"{base}[{args}]"
        elif isinstance(node, ast.Attribute):
            return f"{self._get_annotation(node.value)}.{node.attr}"
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return f"{self._get_annotation(node.left)} | {self._get_annotation(node.right)}"
        return "..."
    
    def _get_decorator_name(self, node) -> str:
        """Extrahiert den Namen eines Decorators"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "?"
    
    def analyze_directory(self, dir_path: str, 
                          recursive: bool = True) -> Dict[str, AnalysisResult]:
        """
        Analysiert alle Python-Dateien in einem Verzeichnis
        
        Args:
            dir_path: Pfad zum Verzeichnis
            recursive: Auch Unterverzeichnisse analysieren
            
        Returns:
            Dict mit Dateipfad -> AnalysisResult
        """
        results = {}
        path = Path(dir_path)
        
        pattern = "**/*.py" if recursive else "*.py"
        
        for py_file in path.glob(pattern):
            # __pycache__ überspringen
            if '__pycache__' in str(py_file):
                continue
            
            results[str(py_file)] = self.analyze_file(str(py_file))
        
        return results
    
    def get_summary(self, result: AnalysisResult) -> str:
        """Erstellt eine lesbare Zusammenfassung"""
        lines = [
            f"=== Analyse: {os.path.basename(result.file_path)} ===",
            "",
            f"📊 Statistiken:",
            f"   Zeilen gesamt: {result.total_lines}",
            f"   Code-Zeilen: {result.code_lines}",
            f"   Kommentare: {result.comment_lines}",
            f"   Leerzeilen: {result.blank_lines}",
            "",
            f"📦 Struktur:",
            f"   Klassen: {len(result.classes)}",
            f"   Funktionen: {len(result.functions)}",
            f"   Imports: {len(result.imports)}",
        ]
        
        if result.classes:
            lines.append("")
            lines.append("🏛️ Klassen:")
            for cls in result.classes:
                lines.append(f"   • {cls.name} (Zeile {cls.line})")
                for method in cls.methods:
                    complexity_marker = "⚠️" if method.complexity > 10 else ""
                    lines.append(f"     - {method.name}() {complexity_marker}")
        
        if result.functions:
            lines.append("")
            lines.append("🔧 Funktionen:")
            for func in result.functions:
                complexity_marker = "⚠️" if func.complexity > 10 else ""
                lines.append(f"   • {func.name}() {complexity_marker}")
        
        if result.unused_imports:
            lines.append("")
            lines.append("⚠️ Ungenutzte Imports:")
            for imp in result.unused_imports:
                lines.append(f"   • {imp}")
        
        if result.errors:
            lines.append("")
            lines.append("❌ Fehler:")
            for err in result.errors:
                lines.append(f"   Zeile {err['line']}: {err['message']}")
        
        if result.warnings:
            lines.append("")
            lines.append("⚠️ Warnungen:")
            for warn in result.warnings:
                lines.append(f"   Zeile {warn['line']}: {warn['message']}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test
    import sys
    
    analyzer = MethodAnalyzer()
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = __file__
    
    result = analyzer.analyze_file(file_path)
    print(analyzer.get_summary(result))

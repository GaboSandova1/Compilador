import tkinter as tk
from tkinter import ttk
import re
# from graphviz import Digraph
from tkinter import scrolledtext, messagebox
from tkinter.font import Font
import os

class ModernTheme:
    # Colores modernos con mejor contraste
    PRIMARY_COLOR = "#1976D2"  # Azul más oscuro
    SECONDARY_COLOR = "#FFA000"  # Ámbar más oscuro
    BACKGROUND_COLOR = "#FFFFFF"  # Fondo blanco para mejor legibilidad
    TEXT_COLOR = "#212121"  # Gris oscuro
    ACCENT_COLOR = "#E91E63"  # Rosa más vibrante
    CODE_BG_COLOR = "#282C34"  # Fondo tipo VS Code
    CODE_FG_COLOR = "#ABB2BF"  # Color de texto tipo VS Code
    HOVER_COLOR = "#2196F3"  # Color para hover
    TABLE_STRIPE_COLOR = "#F8F9FA"  # Color para filas alternadas
    BORDER_COLOR = "#E0E0E0"  # Color para bordes

    # Fuentes más modernas
    TITLE_FONT = ("Segoe UI", 24, "bold")
    HEADER_FONT = ("Segoe UI Semibold", 14)
    NORMAL_FONT = ("Segoe UI", 11)
    CODE_FONT = ("JetBrains Mono", 11)  # Fuente optimizada para código
    BUTTON_FONT = ("Segoe UI", 11, "bold")


class NodoArbol:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, nodo_hijo):
        self.hijos.append(nodo_hijo)

class AnalizadorLexicoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico de Rust")
        self.root.geometry("1280x900")
        self.root.configure(bg=ModernTheme.BACKGROUND_COLOR)
        self.arbol_sintactico = None
        self.treeview = ttk.Treeview(root)
        self.treeview.grid(row=5, column=0, sticky="nsew")


        # Crear un frame para el Treeview del árbol sintáctico
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.grid(row=5, column=0, sticky="nsew")

        # Crear el Treeview del árbol sintáctico
        self.treeview = ttk.Treeview(self.tree_frame)
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Crear un scrollbar para el Treeview del árbol sintáctico
        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=self.tree_scroll.set)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        
        # Configurar el estilo
        self.setup_styles()
        
        self.current_example = 0
        self.rust_examples = self.load_rust_examples()
        self.initialize_token_dictionaries()
        self.create_widgets()
        self.setup_grid_weights()
        
        # # Binding para alternar colores en la tabla
        self.tree.tag_configure('oddrow', background=ModernTheme.TABLE_STRIPE_COLOR)
        self.tree.tag_configure('evenrow', background=ModernTheme.BACKGROUND_COLOR)
        
        # Configurar hover effect para la tabla
        self.tree.tag_configure('hover', background=ModernTheme.HOVER_COLOR, foreground='white')
        self.tree.bind('<Motion>', self.on_hover)
        self.tree.tag_configure('error', background='#FFCDD2', foreground='#B71C1C')


    def setup_styles(self):
        style = ttk.Style()
        style.configure('Title.TLabel', 
                       font=ModernTheme.TITLE_FONT, 
                       background=ModernTheme.BACKGROUND_COLOR,
                       foreground=ModernTheme.PRIMARY_COLOR)
        
        style.configure('Modern.TButton',
                       font=ModernTheme.NORMAL_FONT,
                       padding=10)
        
        style.configure('Modern.TFrame',
                       background=ModernTheme.BACKGROUND_COLOR)
        
        style.configure('Modern.Treeview',
                       font=ModernTheme.NORMAL_FONT,
                       rowheight=25)
        
        style.configure('Modern.Treeview.Heading',
                       font=ModernTheme.HEADER_FONT)

    def setup_grid_weights(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def load_rust_examples(self):
        try:
            with open('rust_examples.txt', 'r') as file:
                content = file.read()
                examples = content.split('# Ejemplo')[1:]
                cleaned_examples = []
                for example in examples:
                    example_lines = example.split('\n', 1)[1]
                    cleaned_examples.append(example_lines.strip())
                return cleaned_examples
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el archivo rust_examples.txt")
            return ["// No se encontraron ejemplos"]

    def initialize_token_dictionaries(self):
        self.rust_keywords = {
            'fn': 'Función',
            'let': 'Declaración de variable',
            'mut': 'Mutable',
            'struct': 'Estructura',
            'impl': 'Implementación',
            'for': 'Bucle for',
            'if': 'Condicional if',
            'else': 'Condicional else',
            'return': 'Retorno',
            'self': 'Referencia al objeto actual',
            'Vec': 'Vector',
            'new': 'Crear nueva instancia',
            'push': 'Agregar elemento'
        }

    def create_widgets(self):
        # Frame principal con padding y bordes redondeados
        main_frame = ttk.Frame(self.root, style='Modern.TFrame', padding="30")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Título con mejor espaciado y diseño
        title_label = ttk.Label(main_frame, 
                              text="Compilador", 
                              style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=30)

        # Frame para el código con diseño mejorado y bordes
        code_frame = ttk.LabelFrame(main_frame, 
                                  text="Código Fuente", 
                                  padding="20",
                                  style='Modern.TLabelframe')
        code_frame.grid(row=1, column=0, sticky="ew", pady=15)
        code_frame.grid_columnconfigure(0, weight=1)

        # Text widget con mejor diseño y sintaxis highlighting
        self.code_text = scrolledtext.ScrolledText(
            code_frame,
            width=80,
            height=12,
            font=ModernTheme.CODE_FONT,
            bg=ModernTheme.CODE_BG_COLOR,
            fg=ModernTheme.CODE_FG_COLOR,
            insertbackground=ModernTheme.CODE_FG_COLOR,
            pady=10,
            padx=10,
            relief="flat",
            borderwidth=0
        )
        self.code_text.grid(row=0, column=0, sticky="ew")

        # Frame para botones con mejor espaciado
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.grid(row=2, column=0, pady=25)

        # Botones modernos con iconos
        analyze_button = ttk.Button(
            button_frame,
            text="⚡ Analizar Código",
            style='Modern.TButton',
            command=self.analyze_code
        )
        analyze_button.grid(row=0, column=0, padx=15)

        clear_button = ttk.Button(
            button_frame,
            text="🗑️ Limpiar Análisis",
            style='Modern.TButton',
            command=self.clear_analysis
        )
        clear_button.grid(row=0, column=1, padx=15)

        next_button = ttk.Button(
            button_frame,
            text="➡️ Siguiente Ejemplo",
            style='Modern.TButton',
            command=self.next_example
        )
        next_button.grid(row=0, column=2, padx=15)

        # Frame para la tabla de resultados con mejor diseño
        results_frame = ttk.LabelFrame(
            main_frame,
            text="Resultados del Análisis",
            padding="20",
            style='Modern.TLabelframe'
        )
        results_frame.grid(row=3, column=0, sticky="ew", pady=15)
        results_frame.grid_columnconfigure(0, weight=1)

        # Container para la tabla con scrollbar
        table_container = ttk.Frame(results_frame)
        table_container.grid(row=0, column=0, sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        # Treeview moderno con mejor diseño
        self.tree = ttk.Treeview(
            table_container,
            columns=('Línea', 'Token', 'Tipo', 'Descripción'),
            show='headings',
            height=12,
            style='Modern.Treeview'
        )
        
        # Configurar columnas con mejor proporción y alineación
        self.tree.heading('Línea', text='Línea', anchor='center')
        self.tree.heading('Token', text='Token', anchor='center')
        self.tree.heading('Tipo', text='Tipo', anchor='center')
        self.tree.heading('Descripción', text='Descripción', anchor='w')
        
        self.tree.column('Línea', width=100, anchor='center')
        self.tree.column('Token', width=200, anchor='center')
        self.tree.column('Tipo', width=250, anchor='center')
        self.tree.column('Descripción', width=450, anchor='w')

        # Scrollbars modernos
         
        
        y_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Organizar tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Barra de estado moderna
        self.status_var = tk.StringVar()
        self.status_var.set("✨ Listo para analizar código")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=ModernTheme.NORMAL_FONT,
            padding="10"
        )
        status_bar.grid(row=4, column=0, sticky="ew", pady=(20,0))

        # Cargar el primer ejemplo
        self.load_example()

    def clear_analysis(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("Análisis limpiado")
        messagebox.showinfo("Limpieza", "Análisis limpiado exitosamente")

    def next_example(self):
        self.current_example = (self.current_example + 1) % len(self.rust_examples)
        self.load_example()
        self.clear_analysis()
        self.status_var.set(f"Ejemplo {self.current_example + 1} cargado")

    def load_example(self):
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, self.rust_examples[self.current_example])

    def tokenize_line(self, line):
        # Expresión regular mejorada para capturar más tipos de tokens
        token_pattern = r'\b\w+\b|[+\-*/=<>!&|^~%]+|[{}()\[\];,.]+'
        tokens = re.findall(token_pattern, line)
        return tokens

    def analyze_token(self, token):
        if token in self.rust_keywords:
            return "Palabra clave", self.rust_keywords[token]
        elif token.isdigit():
            return "Número", "Valor numérico literal"
        elif re.match(r'^[a-zA-Z_]\w*$', token):
            return "Identificador", "Nombre de variable o función"
        elif re.match(r'[+\-*/=<>!&|^~%]+', token):
            return "Operador", "Operador aritmético o lógico"
        elif re.match(r'[{}()\[\];,.]', token):
            return "Delimitador", "Símbolo de agrupación o separación"
        else:
            return "Otro", "Símbolo del lenguaje"

    def on_hover(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.tk.call(self.tree, "tag", "remove", "hover")
            self.tree.tk.call(self.tree, "tag", "add", "hover", item)

    
    def detect_semantic_errors(self, code):
        errors = []
        lines = code.split('\n')
        declared_variables = set()
        for line_num, line in enumerate(lines, 1):
            # Detectar declaración de variables
            if match := re.search(r'\blet\b\s+mut\s+(\w+)', line):
                variable_name = match.group(1)
                if variable_name in declared_variables:
                    errors.append((line_num, "Error semántico", f"Variable '{variable_name}' ya declarada"))
                else:
                    declared_variables.add(variable_name)
            
            # Detectar uso de variables no declaradas
            tokens = self.tokenize_line(line)
            for token in tokens:
                if re.match(r'^[a-zA-Z_]\w*$', token) and token not in declared_variables and token not in self.rust_keywords and token != "main" and token != "i32" and token != "println":
                    errors.append((line_num, "Error semántico", f"Variable '{token}' no declarada"))

        return errors
                
            
    def detect_errors(self, code):
        errors = []
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Ejemplo de condiciones para detectar errores
            if re.search(r'\bfn\b\s+\w+\s*\(', line) and not re.search(r'\)', line):
                errors.append((line_num, "Error de sintaxis", "Falta el paréntesis de cierre en la declaración de la función"))
            elif re.search(r'\blet\b\s+\w+\s*=', line) and not re.search(r';\s*$', line.strip()):
                errors.append((line_num, "Error de sintaxis", "Falta el punto y coma al final de la declaración de la variable"))
            elif re.search(r'\bif\b\s*\(.*\)', line) and not re.search(r'\{', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de apertura en la declaración del condicional if"))
            elif re.search(r'\belse\b', line) and not re.search(r'\{', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de apertura en la declaración del condicional else"))
            elif re.search(r'\bfor\b\s+\w+\s+in\s+.*\{', line) and not re.search(r'\}', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de cierre en la declaración del bucle for"))
            elif re.search(r'\bwhile\b\s*\(.*\)\s*\{', line) and not re.search(r'\}', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de cierre en la declaración del bucle while"))
            elif re.search(r'\breturn\b\s+.*', line) and not re.search(r';\s*$', line.strip()):
                errors.append((line_num, "Error de sintaxis", "Falta el punto y coma al final de la declaración de retorno"))
            elif re.search(r'\bstruct\b\s+\w+\s*\{', line) and not re.search(r'\}', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de cierre en la declaración de la estructura"))
            elif re.search(r'\bimpl\b\s+\w+\s*\{', line) and not re.search(r'\}', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de cierre en la implementación"))
            elif re.search(r'\bmatch\b\s*\(.*\)', line) and not re.search(r'\{', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de apertura en la declaración de match"))
            elif re.search(r'\bloop\b\s*\{', line) and not re.search(r'\}', line):
                errors.append((line_num, "Error de sintaxis", "Falta la llave de cierre en la declaración de loop"))
            elif re.search(r'\bmod\b\s+\w+\s*;', line) and not re.search(r';', line):
                errors.append((line_num, "Error de sintaxis", "Falta el punto y coma al final de la declaración del módulo"))
        # Check for unbalanced parentheses and braces
        open_parentheses = 0
        open_braces = 0
        for line_num, line in enumerate(lines, 1):
            open_parentheses += line.count('(') - line.count(')')
            open_braces += line.count('{') - line.count('}')
            if open_parentheses < 0:
                errors.append((line_num, "Error de sintaxis", "Paréntesis de cierre sin paréntesis de apertura"))
                open_parentheses = 0
            if open_braces < 0:
                errors.append((line_num, "Error de sintaxis", "Llave de cierre sin llave de apertura"))
                open_braces = 0
        if open_parentheses > 0:
            errors.append((line_num, "Error de sintaxis", "Paréntesis de apertura sin paréntesis de cierre"))
        if open_braces > 0:
            errors.append((line_num, "Error de sintaxis", "Llave de apertura sin llave de cierre"))

        # Check for missing semicolons
        for line_num, line in enumerate(lines, 1):
            if not re.search(r'\b(fn|struct|impl|if|else|for|while|loop|match)\b', line) and line.strip() and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}'):
                errors.append((line_num, "Error de sintaxis", "Falta el punto y coma al final de la línea"))

        return errors

    def analyze_code(self):
        self.clear_analysis()
        code = self.code_text.get(1.0, tk.END)
        self.arbol_sintactico = NodoArbol("Programa", "Arbol Sintáctico")
                
        try:
            for i, (line_num, line) in enumerate(enumerate(code.split('\n'), 1)):
                if line.strip():
                    tokens = self.tokenize_line(line)
                    nodo_linea = NodoArbol("Línea", f"Línea {line_num}")
                    self.arbol_sintactico.agregar_hijo(nodo_linea)
                    for token in tokens:
                        tipo, descripcion = self.analyze_token(token)
                        nodo_token = NodoArbol(tipo, token)
                        nodo_linea.agregar_hijo(nodo_token)
                        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                        self.tree.insert('', tk.END, values=(line_num, token, tipo, descripcion), tags=(tag,))
                    
            syntax_errors = self.detect_errors(code)
            for error in syntax_errors:
                line_num, tipo, descripcion = error
                self.tree.insert('', tk.END, values=(line_num, "", tipo, descripcion), tags=('error',))
            
            semantic_errors = self.detect_semantic_errors(code)
            errors = self.detect_errors(code)
            for error in semantic_errors:
                line_num, tipo, descripcion = error
                self.tree.insert('', tk.END, values=(line_num, "", tipo, descripcion), tags=('error',))
            for error in errors:
                line_num, tipo, descripcion = error
                self.tree.insert('', tk.END, values=(line_num, "", tipo, descripcion), tags=('error',))
                    
            if errors:
                self.status_var.set("⚠️ Análisis completado con errores")
                error_messages = "\n".join([f"Línea {line_num}: {descripcion}" for line_num, _, descripcion in errors])
                messagebox.showwarning("Advertencia", f"El análisis léxico se ha completado con errores:\n{error_messages}")
            elif semantic_errors:
                error_messages = "\n".join([f"Línea {line_num}: {descripcion}" for line_num, _, descripcion in semantic_errors])
                self.status_var.set("⚠️ Análisis completado con errores semánticos")
                messagebox.showwarning("Advertencia", f"El análisis léxico se ha completado con errores semánticos:\n{error_messages}")
            else:
                self.status_var.set("✅ Análisis completado exitosamente")
                messagebox.showinfo("Mensaje", "El análisis léxico se ha completado exitosamente")
                self.mostrar_arbol_sintactico()
                self.print_analysis_results()
                
        except Exception as e:
            self.status_var.set("❌ Error durante el análisis")
            messagebox.showerror("Error", f"❌ Error durante el análisis: {str(e)}")






    def print_analysis_results(self):
        code = self.code_text.get(1.0, tk.END)
        variables = {}
        output = []

        for line in code.split('\n'):
            line = line.strip()
            if line.startswith("let"):
                parts = line.split()
                var_name = parts[2].strip(':')
                if "=" in line:
                    value = eval(parts[-1].strip(';'), {}, variables)
                    variables[var_name] = value
                else:
                    variables[var_name] = 0
            elif "=" in line:
                var_name, expr = line.split('=')
                var_name = var_name.strip()
                expr = expr.strip().strip(';')
                variables[var_name] = eval(expr, {}, variables)
            elif line.startswith("println!"):
                var_name = line.split('(')[1].strip(');')
                output.append(f"Valor de {var_name}: {variables.get(var_name, 'Variable no definida')}")

        # Mostrar resultados en la interfaz
        result_text = "\n".join(output)
        self.code_text.insert(tk.END, f"\n\n// Resultados de println!\n{result_text}")

        for result in output:
            print(result)








    # def print_analysis_results(self):
    #     code = self.code_text.get(1.0, tk.END)
    #     tokens = []
    #     variables = {}
    #     output = []

    #     for line_num, line in enumerate(code.split('\n'), 1):
    #         if line.strip():
    #             line_tokens = self.tokenize_line(line)
    #             for token in line_tokens:
    #                 tipo, descripcion = self.analyze_token(token)
    #                 tokens.append((line_num, token, tipo, descripcion))

    #                 # Evaluar asignaciones y operaciones aritméticas
    #                 if tipo == "Identificador" and token not in ["let", "mut"]:
    #                     if line_tokens[line_tokens.index(token) - 1] == "=":
    #                         expr = line.split("=")[1].strip().strip(";")
    #                         variables[token] = eval(expr, {}, variables)
    #                     elif token == "println!":
    #                         var_name = line.split("println!(")[1].strip().strip(");")
    #                         output.append(f"Valor de {var_name}: {variables.get(var_name, 'Variable no definida')}")

    #     # Mostrar resultados en la interfaz
    #     result_text = "\n".join(output)
    #     self.code_text.insert(tk.END, f"\n\n// Resultados de println!\n{result_text}")

        # # Mostrar resultados en la interfaz
        # result_text = "\n".join(output)
        # messagebox.showinfo("Resultados de println!", result_text)


    
    
    def mostrar_arbol_sintactico(self):
        self.treeview.delete(*self.treeview.get_children())
        self._insertar_nodo_arbol(self.arbol_sintactico, "")

    def _insertar_nodo_arbol(self, nodo, parent):
        item_id = self.treeview.insert(parent, 'end', text=f"{nodo.tipo}: {nodo.valor}")
        for hijo in nodo.hijos:
            self._insertar_nodo_arbol(hijo, item_id)
    



def main():
    root = tk.Tk()
    app = AnalizadorLexicoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
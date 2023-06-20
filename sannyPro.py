from tkinter import *
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import font
import psycopg2
#import pylget

# Classe para a GUI de Login e Registro
class LoginGUI:
    def __init__(self, master):
        self.master = master
        self.master.state('zoomed')
        self.master.title("Login")

        self.username_label = Label(self.master, text="Usuário")
        self.username_label.pack()

        self.username_entry = Entry(self.master)
        self.username_entry.pack()

        self.password_label = Label(self.master, text="Senha")
        self.password_label.pack()

        self.password_entry = Entry(self.master, show="*")
        self.password_entry.pack()

        self.login_button = Button(self.master, text="Login", command=self.login)
        self.login_button.pack()

        self.register_button = Button(self.master, text="Registrar", command=self.open_register_window)
        self.register_button.pack()

        self.adjust_font()

    def open_register_window(self):
        register_window = Toplevel(self.master)
        register_gui = RegisterGUI(register_window)
    def adjust_font(self):
        # Obtém o tamanho da janela
        window_width = self.master.winfo_width()
        window_height = self.master.winfo_height()

        # Calcula o tamanho da fonte proporcionalmente ao tamanho da janela
        font_size = int(min(window_width, window_height) / 30)

        # Cria uma nova instância de fonte com o tamanho calculado
        custom_font = font.Font(size=font_size)

        # Configura a fonte para todos os widgets da janela
        for widget in self.master.winfo_children():
            widget.configure(font=custom_font)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if verify_user(username, password):
            self.master.destroy()
            root = Tk()
            app = BoardGUI(root, username)
            root.mainloop()
        else:
            messagebox.showwarning("Login", "Usuário ou senha inválidos.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if register_user(username, password):
            messagebox.showinfo("Registro", "Usuário registrado com sucesso!")
        else:
            messagebox.showerror("Registro", "Erro ao registrar usuário.")


# Classe para a GUI dos Boards
class BoardGUI:
    def __init__(self, master, username):
        self.master = master
        self.master.title("Boards")
        self.master.state('zoomed')
        self.username = username

        self.create_board_label = Label(self.master, text="Criar novo board")
        self.create_board_label.pack()

        self.title_label = Label(self.master, text="Título")
        self.title_label.pack()

        self.title_entry = Entry(self.master)
        self.title_entry.pack()

        self.description_label = Label(self.master, text="Descrição")
        self.description_label.pack()

        self.description_entry = Entry(self.master)
        self.description_entry.pack()

        self.create_board_button = Button(self.master, text="Criar", command=self.create_board)
        self.create_board_button.pack()

        self.board_listbox = Listbox(self.master)
        self.board_listbox.pack()

        self.load_boards()

        self.board_listbox.bind("<<ListboxSelect>>", self.show_tasks)

    def create_board(self):
        title = self.title_entry.get()
        description = self.description_entry.get()

        if not title:
            messagebox.showwarning("Criar Board", "O título não pode estar vazio.")
            return

        board = Board(title, description)
        self.save_board(board)

        self.title_entry.delete(0, END)
        self.description_entry.delete(0, END)

    def save_board(self, board):
        try:
            connection = psycopg2.connect(
                host="localhost",
                database="sanny",
                user="postgres",
                password="delta21"
            )
            cursor = connection.cursor()

            cursor.execute("INSERT INTO boards (title, description) VALUES (%s, %s)", (board.title, board.description))

            cursor.execute("SELECT id FROM users WHERE username = %s", (self.username,))
            user_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM boards WHERE title = %s", (board.title,))
            board_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO user_board (user_id, board_id) VALUES (%s, %s)", (user_id, board_id))

            connection.commit()

            cursor.close()
            connection.close()

            self.load_boards()
            messagebox.showinfo("Criar Board", "Board criado com sucesso!")
        except (Exception, psycopg2.Error) as error:
            print("Erro ao salvar board:", error)
            messagebox.showerror("Criar Board", "Erro ao criar board.")

    def load_boards(self):
        try:
            connection = psycopg2.connect(
                host="localhost",
                database="sanny",
                user="postgres",
                password="delta21"
            )
            cursor = connection.cursor()

            cursor.execute("""
                SELECT boards.title
                FROM boards
                INNER JOIN user_board ON boards.id = user_board.board_id
                INNER JOIN users ON user_board.user_id = users.id
                WHERE users.username = %s
            """, (self.username,))

            boards = cursor.fetchall()

            self.board_listbox.delete(0, END)
            for board in boards:
                self.board_listbox.insert(END, board[0])

            cursor.close()
            connection.close()
        except (Exception, psycopg2.Error) as error:
            print("Erro ao carregar boards:", error)

    def show_tasks(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            board_title = event.widget.get(index)
            root = Toplevel(self.master)
            app = TaskGUI(root, self.username, board_title)
            root.mainloop()


# Classe para a GUI das Tarefas
class TaskGUI:
    def __init__(self, master, username, board_title):
        self.master = master
        self.master.title("Tarefas")
        self.master.state('zoomed')
        self.username = username
        self.board_title = board_title

        self.create_task_label = Label(self.master, text="Criar nova tarefa")
        self.create_task_label.pack()

        self.title_label = Label(self.master, text="Título")
        self.title_label.pack()

        self.title_entry = Entry(self.master)
        self.title_entry.pack()

        self.description_label = Label(self.master, text="Descrição")
        self.description_label.pack()

        self.description_entry = Entry(self.master)
        self.description_entry.pack()

        self.deadline_label = Label(self.master, text="Prazo")
        self.deadline_label.pack()

        self.deadline_entry = DateEntry(self.master, date_pattern = "dd/mm/yyyy")
        self.deadline_entry.pack()

        self.status_label = Label(self.master, text="Status")
        self.status_label.pack()

        self.status_variable = StringVar(self.master)
        self.status_variable.set("to do")

        self.status_options = OptionMenu(self.master, self.status_variable, "to do", "doing", "done")
        self.status_options.pack()

        self.owner_label = Label(self.master, text="Dono")
        self.owner_label.pack()

        self.owner_entry = Entry(self.master)
        self.owner_entry.pack()

        self.create_task_button = Button(self.master, text="Criar", command=self.create_task)
        self.create_task_button.pack()

        self.task_listbox = Listbox(self.master)
        self.task_listbox.pack()

        self.load_tasks()

        self.task_listbox.bind("<<ListboxSelect>>", self.show_task_info)

    def create_task(self):
        title = self.title_entry.get()
        description = self.description_entry.get()
        deadline = self.deadline_entry.get()
        status = self.status_variable.get()
        owner = self.owner_entry.get()

        if not title:
            messagebox.showwarning("Criar Tarefa", "O título não pode estar vazio.")
            return

        task = Task(title, description, deadline, status, owner)
        self.save_task(task)

        self.title_entry.delete(0, END)
        self.description_entry.delete(0, END)
        self.deadline_entry.delete(0, END)
        self.status_variable.set("to do")
        self.owner_entry.delete(0, END)

    def save_task(self, task):
        try:
            connection = psycopg2.connect(
                host="localhost",
                database="sanny",
                user="postgres",
                password="delta21"
            )
            cursor = connection.cursor()

            cursor.execute("SELECT id FROM boards WHERE title = %s", (self.board_title,))
            board_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO tasks (board_id, title, description, deadline, status, owner)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (board_id, task.title, task.description, task.deadline, task.status, task.owner))

            connection.commit()

            cursor.close()
            connection.close()

            self.load_tasks()
            messagebox.showinfo("Criar Tarefa", "Tarefa criada com sucesso!")
        except (Exception, psycopg2.Error) as error:
            print("Erro ao salvar tarefa:", error)
            messagebox.showerror("Criar Tarefa", "Erro ao criar tarefa.")

    def load_tasks(self):
        try:
            connection = psycopg2.connect(
                host="localhost",
                database="sanny",
                user="postgres",
                password="delta21"
            )
            cursor = connection.cursor()

            cursor.execute("SELECT id FROM boards WHERE title = %s", (self.board_title,))
            board_id = cursor.fetchone()[0]

            cursor.execute("SELECT tasks.title FROM tasks WHERE board_id = %s", (board_id,))
            tasks = cursor.fetchall()

            self.task_listbox.delete(0, END)
            for task in tasks:
                self.task_listbox.insert(END, task[0])

            cursor.close()
            connection.close()
        except (Exception, psycopg2.Error) as error:
            print("Erro ao carregar tarefas:", error)

    def show_task_info(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            task_title = event.widget.get(index)
            root = Toplevel(self.master)
            app = EditTaskGUI(root, self.username, self.board_title, task_title)
            root.mainloop()


# Classe para a GUI de Edição de Tarefas
class EditTaskGUI:
    def __init__(self, master, username, board_title, task_title):
        self.master = master
        self.master.title("Editar Tarefa")
        self.master.state('zoomed')
        self.username = username
        self.board_title = board_title
        self.task_title = task_title

        self.title_label = Label(self.master, text="Título")
        self.title_label.pack()

        self.title_entry = Entry(self.master)
        self.title_entry.pack()

        self.description_label = Label(self.master, text="Descrição")
        self.description_label.pack()

        self.description_entry = Entry(self.master)
        self.description_entry.pack()

        self.deadline_label = Label(self.master, text="Prazo")
        self.deadline_label.pack()

        self.deadline_entry = DateEntry(self.master, date_pattern = "dd/mm/yyyy")
        self.deadline_entry.pack()

        self.status_label = Label(self.master, text="Status")
        self.status_label.pack()

        self.status_variable = StringVar(self.master)
        self.status_variable.set("to do")

        self.status_options = OptionMenu(self.master, self.status_variable, "to do", "doing", "done")
        self.status_options.pack()

        self.owner_label = Label(self.master, text="Dono")
        self.owner_label.pack()

        self.owner_entry = Entry(self.master)
        self.owner_entry.pack()

        self.save_button = Button(self.master, text="Salvar", command=self.save_task)
        self.save_button.pack()

        self.load_task()

    def load_task(self):
        try:
            connection = psycopg2.connect(
                host="localhost",
                database="sanny",
                user="postgres",
                password="delta21"
            )
            cursor = connection.cursor()

            cursor.execute("SELECT id FROM boards WHERE title = %s", (self.board_title,))
            board_id = cursor.fetchone()[0]

            cursor.execute("SELECT * FROM tasks WHERE board_id = %s AND title = %s", (board_id, self.task_title))
            task = cursor.fetchone()

            if task:
                self.title_entry.insert(0, task[2])
                self.description_entry.insert(0, task[3])
                self.deadline_entry.insert(0, task[4])
                self.status_variable.set(task[5])
                self.owner_entry.insert(0, task[6])

            cursor.close()
            connection.close()
        except (Exception, psycopg2.Error) as error:
            print("Erro ao carregar tarefa:", error)

    def save_task(self):
        title = self.title_entry.get()
        description = self.description_entry.get()
        deadline = self.deadline_entry.get()
        status = self.status_variable.get()
        owner = self.owner_entry.get()

        try:
            connection = psycopg2.connect(
                host="localhost",
                database="sanny",
                user="postgres",
                password="delta21"
            )
            cursor = connection.cursor()

            cursor.execute("SELECT id FROM boards WHERE title = %s", (self.board_title,))
            board_id = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE tasks
                SET title = %s, description = %s, deadline = %s, status = %s, owner = %s
                WHERE board_id = %s AND title = %s
            """, (title, description, deadline, status, owner, board_id, self.task_title))

            connection.commit()

            cursor.close()
            connection.close()

            messagebox.showinfo("Editar Tarefa", "Tarefa salva com sucesso!")
        except (Exception, psycopg2.Error) as error:
            print("Erro ao salvar tarefa:", error)
            messagebox.showerror("Editar Tarefa", "Erro ao salvar tarefa.")


def verify_user(username, password):
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="sanny",
            user="postgres",
            password="delta21"
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            return True
        else:
            return False
    except (Exception, psycopg2.Error) as error:
        print("Erro ao verificar usuário:", error)
        return False


def register_user(username, password):
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="sanny",
            user="postgres",
            password="delta21"
        )
        print("conexão bem-sucedida")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            return False

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()

        cursor.close()
        connection.close()

        return True
    except (Exception, psycopg2.Error) as error:
        print("Erro ao registrar usuário:", error)
        return False
    
class RegisterGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Registro")

        self.username_label = Label(self.master, text="Usuário")
        self.username_label.pack()

        self.username_entry = Entry(self.master)
        self.username_entry.pack()

        self.password_label = Label(self.master, text="Senha")
        self.password_label.pack()

        self.password_entry = Entry(self.master, show="*")
        self.password_entry.pack()

        self.confirm_password_label = Label(self.master, text="Confirmar Senha")
        self.confirm_password_label.pack()

        self.confirm_password_entry = Entry(self.master, show="*")
        self.confirm_password_entry.pack()

        self.register_button = Button(self.master, text="Registrar", command=self.register)
        self.register_button.pack()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password == confirm_password:
            if register_user(username, password):
                messagebox.showinfo("Registro", "Usuário registrado com sucesso!")
                self.master.destroy()
            else:
                messagebox.showerror("Registro", "Erro ao registrar usuário.")
        else:
            messagebox.showwarning("Registro", "As senhas não coincidem.")


class Board:
    def __init__(self, title, description):
        self.title = title
        self.description = description


class Task:
    def __init__(self, title, description, deadline, status, owner):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = status
        self.owner = owner
# Conectando ao banco de dados
connection = psycopg2.connect(
    host="localhost",
    database="sanny",
    user="postgres",
    password="delta21"
)

# Criando a tabela 'users'
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
)
"""

# Criando a tabela 'boards'
create_boards_table = """
CREATE TABLE IF NOT EXISTS boards (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255)
)
"""

# Criando a tabela 'user_board'
create_user_board_table = """
CREATE TABLE IF NOT EXISTS user_board (
    user_id INTEGER REFERENCES users (id),
    board_id INTEGER REFERENCES boards (id),
    PRIMARY KEY (user_id, board_id)
)
"""

# Criando a tabela 'tasks'
create_tasks_table = """
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    board_id INTEGER REFERENCES boards (id),
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    deadline DATE,
    status VARCHAR(50),
    owner VARCHAR(255)
)
"""

# Executando as instruções SQL
cursor = connection.cursor()
cursor.execute(create_users_table)
cursor.execute(create_boards_table)
cursor.execute(create_user_board_table)
cursor.execute(create_tasks_table)
connection.commit()

# Fechando a conexão com o banco de dados
cursor.close()
connection.close()

if __name__ == "__main__":
    root = Tk()
    app = LoginGUI(root)
    root.mainloop()

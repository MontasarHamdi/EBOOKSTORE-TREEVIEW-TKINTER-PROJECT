from tkinter import *
from tkinter import ttk
import sqlite3
from tkinter import messagebox

# Database functions - create a database and connect
conn = sqlite3.connect('tree_ebookstore.db')
# create cursor instance
c = conn.cursor()
# create a table
c.execute("""CREATE TABLE if not exists ebookstore (
    id integer primary key,
    book_title varchar(255),
    book_author varchar(30),
    book_qty integer)""")  # NOQA

conn.commit()
conn.close()


# present data in tree view
def query_database():
    conn = sqlite3.connect('tree_ebookstore.db')
    # create cursor instance
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM ebookstore")  # use rowid as primary key - inbuilt row counter with sqlite3
    records = c.fetchall()
    # ADD records to the screen
    global count
    count = 0
    # see data being pulled out on terminal - use for debugging
    # for record in records:
    #    print(record)
    for record in records:
        if count % 2 == 0:
            my_tree.insert(parent='', index='end', iid=count, text='',
                           values=(record[0], record[2], record[3], record[4]),
                           tags=('evenrow',))  # NOQA
        else:
            my_tree.insert(parent='', index='end', iid=count, text='',
                           values=(record[0], record[2], record[3], record[4]),
                           tags=('oddrow',))  # NOQA
        # increment counter
        count += 1
    conn.commit()
    conn.close()


# ===== GRAPHICAL USER INTERFACE ===== #
root = Tk()
root.title('EBOOKSTORE')
root.geometry('900x600')

# add some style
style = ttk.Style()
# pick a theme
style.theme_use('default')
# Tree view colours
style.configure("Treeview",
                background="#D3D3D3",
                foreground="black",
                rowheight=25,
                fieldbackground="#D3D3D3")
# change selected colours
style.map('Treeview', background=[('selected', "#347083")])
# Treeview frame
tree_frame = Frame(root)
tree_frame.pack(pady=10)
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)
# Create treeview
my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
my_tree.pack()
# configure the scrollbar
tree_scroll.config(command=my_tree.yview)

# define our columns
my_tree['columns'] = ("Book ID", "Book Title", "Book Author", "Book Quantity")
# format columns
my_tree.column("#0", width=0, stretch=NO)
my_tree.column("Book ID", anchor=W, width=140)
my_tree.column("Book Title", anchor=W, width=100)
my_tree.column("Book Author", anchor=CENTER, width=140)
my_tree.column("Book Quantity", anchor=CENTER, width=140)

# Create headings
my_tree.heading("#0", text="", anchor=W)
my_tree.heading("Book ID", text="Book ID", anchor=W)
my_tree.heading("Book Title", text="Book Title", anchor=W)
my_tree.heading("Book Author", text="Book Author", anchor=CENTER)
my_tree.heading("Book Quantity", text="Book Quantity", anchor=CENTER)


# Striped rows
my_tree.tag_configure('oddrow', background="white")  # NOQA
my_tree.tag_configure('evenrow', background="lightblue")  # NOQA


# Add book record entry boxes
data_frame = LabelFrame(root, text="Book Record")
data_frame.pack(fill="x", expand="yes", padx=20)

id_label = Label(data_frame, text="Book ID")
id_label.grid(row=0, column=0, padx=10, pady=10)
id_entry = Entry(data_frame)
id_entry.grid(row=0, column=1, padx=10, pady=10)

bt_label = Label(data_frame, text="Book Title")
bt_label.grid(row=0, column=2, padx=10, pady=10)
bt_entry = Entry(data_frame)
bt_entry.grid(row=0, column=3, padx=10, pady=10)

ba_label = Label(data_frame, text="Book Author")
ba_label.grid(row=1, column=0, padx=10, pady=10)
ba_entry = Entry(data_frame)
ba_entry.grid(row=1, column=1, padx=10, pady=10)

qty_label = Label(data_frame, text="Book Quantity")
qty_label.grid(row=1, column=2, padx=10, pady=10)
qty_entry = Entry(data_frame)
qty_entry.grid(row=1, column=3, padx=10, pady=10)


# move up
def up():
    rows = my_tree.selection()
    for row in rows:
        my_tree.move(row, my_tree.parent(row), my_tree.index(row)-1)


# move down
def down():
    rows = my_tree.selection()
    for row in reversed(rows):
        my_tree.move(row, my_tree.parent(row), my_tree.index(row)+1)


# remove record
def remove_one():
    x = my_tree.selection()[0]
    my_tree.delete(x)

    conn = sqlite3.connect('tree_ebookstore.db')
    # create cursor instance
    c = conn.cursor()
    # delete from database
    c.execute("DELETE from ebookstore WHERE oid=" + id_entry.get())
    conn.commit()
    conn.close()
    # clear entry boxes
    clear_entries()
    # message box
    messagebox.showinfo("Deleted!", "Your record has been deleted!")


# remove many
def remove_many():
    resp = messagebox.askyesno("""WOAH!!! This will delete selected books from the table!
    \nAre you sure you want to proceed?""")
    if resp == 1:
        x = my_tree.selection()
        # create list of id's
        ids_to_delete = []
        # loop
        for record in x:
            ids_to_delete.append(my_tree.item(record, 'values')[0])

        # delete from treeview
        for record in x:
            my_tree.delete(record)
        conn = sqlite3.connect('tree_ebookstore.db')
        c = conn.cursor()
        # delete selected book from table database
        c.executemany("DELETE from ebookstore WHERE id= ?", [(a,) for a in ids_to_delete])
        conn.commit()
        conn.close()
        # clear entry boxes if filled


# remove all
def remove_all():
    # message box
    resp = messagebox.askyesno("WOAH!!! This will delete everything from the table!\nAre you sure you want to proceed?")
    if resp == 1:
        for record in my_tree.get_children():
            my_tree.delete(record)
        conn = sqlite3.connect('tree_ebookstore.db')
        c = conn.cursor()
        # delete everything from table
        c.execute("DROP TABLE ebookstore")
        conn.commit()
        conn.close()
        # clear entry boxes if filled
        clear_entries()
        create_table_again()


# create table again after deletion
def create_table_again():
    # Database functions - create a database and connect
    conn = sqlite3.connect('tree_ebookstore.db')
    # create cursor instance
    c = conn.cursor()
    # create a table
    c.execute("""CREATE TABLE if not exists ebookstore (
        id integer primary key,
        book_title varchar(255),
        book_author varchar(30),
        book_qty integer)""")  # NOQA

    conn.commit()
    conn.close()


# Clear entry boxes
def clear_entries():
    # clear entry boxes first
    id_entry.delete(0, END)
    bt_entry.delete(0, END)
    ba_entry.delete(0, END)
    qty_entry.delete(0, END)


# Select record def
def select_record(e):
    # clear entry boxes first
    id_entry.delete(0, END)
    bt_entry.delete(0, END)
    ba_entry.delete(0, END)
    qty_entry.delete(0, END)

    # Grab record number
    selected = my_tree.focus()
    # grab record values
    values = my_tree.item(selected, 'values')

    # output entry boxes
    id_entry.insert(0, values[0])
    bt_entry.insert(0, values[1])
    ba_entry.insert(0, values[2])
    qty_entry.insert(0, values[3])


# update record
def update_record():
    selected = my_tree.focus()
    my_tree.item(selected, text="", values=(id_entry.get(), bt_entry.get(), ba_entry.get(), qty_entry.get(),))
    # update the database now
    conn = sqlite3.connect('tree_ebookstore.db')
    # create cursor instance
    c = conn.cursor()
    c.execute("""UPDATE ebookstore SET
    book_title = :title,
    book_author = :author,
    book_qty = :qty
    WHERE oid = :oid""", {
        'title': bt_entry.get(),
        'author': ba_entry.get(),
        'qty': qty_entry.get(),
        'oid': id_entry.get()
    })
    conn.commit()
    conn.close()
    # ADD records to the screen

    id_entry.delete(0, END)
    bt_entry.delete(0, END)
    ba_entry.delete(0, END)
    qty_entry.delete(0, END)


# add new record to database
def add_record():
    conn = sqlite3.connect('tree_ebookstore.db')
    # create cursor instance
    c = conn.cursor()
    # add new book
    c.execute("INSERT INTO ebookstore VALUES (:id, :title, :author, :qty)", {
        'id': id_entry.get(),
        'title': bt_entry.get(),
        'author': ba_entry.get(),
        'qty': qty_entry.get()
    })
    conn.commit()
    conn.close()
    id_entry.delete(0, END)
    bt_entry.delete(0, END)
    ba_entry.delete(0, END)
    qty_entry.delete(0, END)

    # clear treeview table and refresh
    my_tree.delete(*my_tree.get_children())
    query_database()


# add buttons to commands
button_frame = LabelFrame(root, text="Commands")
button_frame.pack(fill="x", expand="yes", padx=20)
_button = Button(button_frame, text="")
_button.grid(row=0, column=0, padx=10, pady=10)

update_button = Button(button_frame, text="Update", command=update_record)
update_button.grid(row=0, column=0, padx=10, pady=10)

add_button = Button(button_frame, text="Add", command=add_record)
add_button.grid(row=0, column=1, padx=10, pady=10)

remove_all_button = Button(button_frame, text="Remove All Books", command=remove_all)
remove_all_button.grid(row=0, column=2, padx=10, pady=10)

remove_one_button = Button(button_frame, text="Remove Selected Book", command=remove_one)
remove_one_button.grid(row=0, column=3, padx=10, pady=10)

remove_many_button = Button(button_frame, text="Remove Selected Books", command=remove_many)
remove_many_button.grid(row=0, column=4, padx=10, pady=10)

move_up_button = Button(button_frame, text="Move Up", command=up)
move_up_button.grid(row=1, column=0, padx=10, pady=10)

move_down_button = Button(button_frame, text="Move Down", command=down)
move_down_button.grid(row=1, column=1, padx=10, pady=10)

select_record_button = Button(button_frame, text="Clear Entry Boxes", command=clear_entries)
select_record_button.grid(row=1, column=2, padx=10, pady=10)

# Bind Tree View
my_tree.bind("<ButtonRelease-1>", select_record)
# Run to pull data from database on start
query_database()
root.mainloop()

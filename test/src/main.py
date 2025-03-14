config = {
    "main":"main",
    "commands":[
        {
            "name":"showHello",
            "func":"showHello"
        }
    ]
}


def main(window):
    clear(window)
    tk.Label(window, text="Hello World!").pack()
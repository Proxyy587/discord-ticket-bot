import os
from dotenv import load_dotenv

TOKEN = os.getenv("BOT_TOKEN")
guild = 1076165556849356860
icon_url = "https://media.discordapp.net/attachments/1076181872616415302/1085534459635433503/cypro4.png?width=701&height=701"
review_channel= 1076174186428502046
CSS = """
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background-color: #36393f;
}
.messages {
    margin: 20px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.message {
    display: flex;
    margin-bottom: 10px;
    max-width: 800px;
}

.message img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    margin-right: 10px;
}

.author {
    font-weight: bold;
    margin-right: 10px;
    color: #fff;
}

.timestamp {
    font-size: 12px;
    color: #b9bbbe;
    margin-right: 10px;
}

.content {
    background-color: #40444B;
    color: #dcddde;
    padding: 8px;
    border-radius: 5px;
    line-height: 1.2;
}
"""

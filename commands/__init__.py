from discord.app_commands import CommandTree
from .my_task import my_task

def setup_commands(tree: CommandTree):
    tree.command(name="my_task", description="コマンドしたユーザのタスクを表示")(my_task)
    
from .. import loader, utils
import asyncio

@loader.tds
class SixSevenMod(loader.Module):
    """Анимация .67"""

    strings = {"name": "SixSeven"}

    async def cmd67(self, message):
        """Запусти анимацию"""
        
        frames = [
"""
⠀⠀⠀⠀⢀⣀⣀
⠀⠀⠀⢠⣿⣿⣿⣧
⠀⠀⠀⣿⣿⣿⣿⣿
⠀⠀⠀⠈⠻⣿⠟
⠀⠀⠀⢠⡟⢻⡄
⠀⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠘⠃
   67 👋
""",
"""
⠀⠀⠀⠀⢀⣀⣀
⠀⠀⠀⢠⣿⣿⣿⣧
⠀⠀⠀⣿⣿⣿⣿⣿
⠀⠀⠀⠈⠻⣿⠟
⠀⠀⠀⢸⡇⢸⡇
⠀⠀⠀⠀⢳⡟
⠀⠀⠀⠀⠘
   67 👋
""",
"""
⠀⠀⠀⠀⢀⣀⣀
⠀⠀⠀⢠⣿⣿⣿⣧
⠀⠀⠀⣿⣿⣿⣿⣿
⠀⠀⠀⠈⠻⣿⠟
⠀⠀⠀⢸⡇⢸⡇
⠀⠀⠀⢸⡇⠘⣧
⠀⠀⠀⠀⠀⠀⠘
   67 👋
"""
        ]

        msg = await utils.answer(message, frames[0])

        for _ in range(6):
            for frame in frames:
                await asyncio.sleep(0.4)
                await msg.edit(frame)

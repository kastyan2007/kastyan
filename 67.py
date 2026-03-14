from .. import loader, utils
import asyncio

@loader.tds
class SixSeven(loader.Module):
    """Анимация 67"""

    strings = {"name": "SixSeven"}

    async def _animate(self, message, frames):
        msg = await utils.answer(message, frames[0])
        for _ in range(5):
            for frame in frames:
                await asyncio.sleep(0.4)
                await msg.edit(frame)

    async def 67cmd(self, message):
        """анимация .67"""

        frames = [
"""
   ⠀⢀⣀
  ⢠⣿⣿⣧
  ⣿⣿⣿⣿
   ⠻⣿⠟
   ⢸⡇
  👋 67
""",
"""
   ⠀⢀⣀
  ⢠⣿⣿⣧
  ⣿⣿⣿⣿
   ⠻⣿⠟
   ⢸⡇⣀
      👋
""",
"""
   ⠀⢀⣀
  ⢠⣿⣿⣧
  ⣿⣿⣿⣿
   ⠻⣿⠟
   ⣸⡇
   👋 67
"""
        ]

        await self._animate(message, frames)

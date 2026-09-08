import logging

import discord
from discord import app_commands
from discord.ext import commands

from services.stages import REGIONS


logger = logging.getLogger(__name__)


class Errors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._previous_tree_error = bot.tree.on_error

    async def cog_load(self) -> None:
        self.bot.tree.error(self.on_app_command_error)

    async def cog_unload(self) -> None:
        if self.bot.tree.on_error == self.on_app_command_error:
            self.bot.tree.on_error = self._previous_tree_error

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> None:
        if ctx.command is not None and ctx.command.has_error_handler():
            return
        if ctx.cog is not None and ctx.cog.has_error_handler():
            return
        if isinstance(error, commands.CommandNotFound):
            return

        message = self._prefix_error_message(ctx, error)
        if message is None:
            original = self._original_error(error)
            logger.error(
                'Unhandled error in prefix command %s',
                ctx.command,
                exc_info=original,
            )
            message = 'コマンドの実行中にエラーが発生しました。'
        await ctx.reply(message, mention_author=False)

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        message = self._app_error_message(error)
        if message is None:
            original = self._original_error(error)
            command_name = (
                interaction.command.qualified_name if interaction.command else None
            )
            logger.error(
                'Unhandled error in application command %s',
                command_name,
                exc_info=original,
            )
            message = 'コマンドの実行中にエラーが発生しました。'

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    @staticmethod
    def _prefix_error_message(
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> str | None:
        if isinstance(error, commands.MissingRequiredAttachment):
            return '添付ファイルを指定してください。'
        if isinstance(error, commands.CommandOnCooldown):
            return f'しばらく待ってからお試しください。（あと{error.retry_after:.1f}秒）'
        if isinstance(error, commands.MaxConcurrencyReached):
            return 'このコマンドは現在処理中です。完了してからお試しください。'
        if isinstance(error, commands.BotMissingPermissions):
            return 'Botにこの操作を行う権限がありません。'
        if isinstance(error, (commands.NotOwner, commands.MissingPermissions)):
            return 'このコマンドを実行する権限がありません。'
        if isinstance(error, commands.UserInputError):
            if ctx.command is not None and ctx.command.qualified_name == 'stage':
                regions = '\n'.join(
                    f'{name}: `{code}`' for code, name in REGIONS.items()
                )
                return (
                    '使い方: `stage <GUID> [サーバー]`\n'
                    f'省略すると自動判定します。\n{regions}'
                )
            return '入力値またはコマンドの使い方を確認してください。'
        if isinstance(error, commands.CheckFailure):
            return 'このコマンドは現在利用できません。'
        return None

    @staticmethod
    def _app_error_message(error: app_commands.AppCommandError) -> str | None:
        if isinstance(error, app_commands.CommandOnCooldown):
            return f'しばらく待ってからお試しください。（あと{error.retry_after:.1f}秒）'
        if isinstance(error, app_commands.BotMissingPermissions):
            return 'Botにこの操作を行う権限がありません。'
        if isinstance(error, app_commands.MissingPermissions):
            return 'このコマンドを実行する権限がありません。'
        if isinstance(error, app_commands.TransformerError):
            return '入力値またはコマンドの使い方を確認してください。'
        if isinstance(error, app_commands.CheckFailure):
            return 'このコマンドは現在利用できません。'
        return None

    @staticmethod
    def _original_error(error: Exception) -> Exception:
        if isinstance(
            error,
            (commands.CommandInvokeError, app_commands.CommandInvokeError),
        ):
            return error.original
        return error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Errors(bot))

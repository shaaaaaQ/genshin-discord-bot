import logging
import sqlite3

import discord
from discord.ext import commands, tasks

from services.codes import (
    CodesClient,
    CodesError,
    CodesStateStore,
    create_codes_embeds,
)


logger = logging.getLogger(__name__)


class Codes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = CodesClient()
        self.state = CodesStateStore()

    async def cog_load(self) -> None:
        await self.client.start()
        self.check_for_new_codes.start()

    async def cog_unload(self) -> None:
        self.check_for_new_codes.cancel()
        await self.client.close()

    async def _notification_channel(
        self, channel_id: int
    ) -> discord.abc.Messageable:
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)
        if not isinstance(channel, discord.abc.Messageable):
            raise TypeError(
                f'Notification channel ({channel_id}) is not messageable'
            )
        return channel

    @tasks.loop(minutes=15)
    async def check_for_new_codes(self) -> None:
        logger.info('Checking for new exchange codes')
        try:
            settings = await self.state.get_settings()
            if not settings:
                logger.info(
                    'Exchange code check completed: no notification settings'
                )
                return
            codes = await self.client.fetch()
            current_keys = {code.key for code in codes}
            for setting in settings:
                try:
                    # Ignore a stale snapshot if an administrator changed or
                    # removed this setting while the API request was running.
                    if (
                        await self.state.get_channel_id(setting.guild_id)
                        != setting.channel_id
                    ):
                        continue
                    # The first lookup for a server establishes its baseline.
                    if setting.active_keys is None:
                        await self.state.save_active_keys(
                            setting.guild_id, current_keys
                        )
                        continue

                    new_codes = [
                        code
                        for code in codes
                        if code.key not in setting.active_keys
                    ]
                    if new_codes:
                        channel = await self._notification_channel(
                            setting.channel_id
                        )
                        embeds = create_codes_embeds(new_codes)
                        embeds[0].description = (
                            '新しい交換コードが追加されました。'
                        )
                        for embed in embeds:
                            await channel.send(
                                embed=embed,
                                allowed_mentions=discord.AllowedMentions.none(),
                            )
                        logger.info(
                            'Notified %d new exchange code(s) to guild %d',
                            len(new_codes),
                            setting.guild_id,
                        )

                    await self.state.save_active_keys(
                        setting.guild_id, current_keys
                    )
                except (
                    OSError,
                    sqlite3.Error,
                    ValueError,
                    TypeError,
                    discord.HTTPException,
                ):
                    logger.exception(
                        'Exchange code notification failed for guild %d',
                        setting.guild_id,
                    )
            logger.info(
                'Exchange code check completed: %d active code(s), %d guild(s)',
                len(codes),
                len(settings),
            )
        except CodesError as error:
            logger.warning('Periodic exchange code lookup failed: %s', error)
        except (OSError, sqlite3.Error, ValueError):
            logger.exception('Periodic exchange code notification failed')

    @check_for_new_codes.before_loop
    async def before_check_for_new_codes(self) -> None:
        await self.bot.wait_until_ready()

    @commands.hybrid_group(
        fallback='status',
        invoke_without_command=True,
        description='交換コード通知の設定を管理します',
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def codesnotify(
        self,
        ctx: commands.Context,
    ) -> None:
        """交換コード通知の設定を管理します。"""
        if ctx.guild is None:
            return

        channel_id = await self.state.get_channel_id(ctx.guild.id)
        if channel_id is None:
            message = '交換コードの通知先は設定されていません。'
        else:
            message = f'現在の交換コード通知先は <#{channel_id}> です。'
        await ctx.reply(
            message,
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @codesnotify.command(name='set', description='交換コードの通知先を設定します')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def codesnotify_set(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
    ) -> None:
        """交換コードの通知先を設定します。"""
        if ctx.guild is None:
            return

        bot_member = ctx.guild.me
        permissions = channel.permissions_for(bot_member)
        if not permissions.send_messages or not permissions.embed_links:
            await ctx.reply(
                'そのチャンネルでメッセージ送信と埋め込みリンクを使える権限が必要です。',
                mention_author=False,
            )
            return

        previous_channel_id = await self.state.get_channel_id(ctx.guild.id)
        await self.state.set_channel(ctx.guild.id, channel.id)
        if previous_channel_id is None:
            try:
                current_codes = await self.client.fetch()
                await self.state.save_active_keys(
                    ctx.guild.id, {code.key for code in current_codes}
                )
            except (CodesError, OSError, sqlite3.Error, ValueError):
                logger.exception(
                    'Failed to initialize exchange code state for guild %d',
                    ctx.guild.id,
                )
        await ctx.reply(
            f'交換コードの通知先を {channel.mention} に設定しました。',
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @codesnotify.command(name='remove', description='交換コードの通知を解除します')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def codesnotify_remove(self, ctx: commands.Context) -> None:
        """交換コードの通知を解除します。"""
        if ctx.guild is None:
            return

        removed = await self.state.remove(ctx.guild.id)
        message = (
            '交換コードの通知設定を削除しました。'
            if removed
            else '交換コードの通知先は設定されていません。'
        )
        await ctx.reply(message, mention_author=False)

    @commands.hybrid_command(description='現在利用できる原神の交換コードを表示します')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def codes(self, ctx: commands.Context) -> None:
        """現在利用できる原神の交換コードを表示します。"""
        await ctx.defer()
        try:
            codes = await self.client.fetch()
            embeds = create_codes_embeds(codes)
        except CodesError as error:
            await ctx.reply(str(error), mention_author=False)
            return
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.exception('Invalid hoyoverse-api response')
            await ctx.reply(
                '交換コードの形式を読み取れませんでした。', mention_author=False
            )
            return
        await ctx.reply(
            embed=embeds[0],
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        for embed in embeds[1:]:
            await ctx.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Codes(bot))

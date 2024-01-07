# This cog creates all moderation commands.
# Copyright (C) 2023  Alec Jensen
# Full license at LICENSE.md

import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import humanize
import logging

from utils.kidney_bot import KidneyBot


time_convert = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800
}

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot: KidneyBot = bot

    async def permissionHierarchyCheck(self, user: discord.Member, target: discord.Member) -> bool:
        logging.debug(
            f'Checking permission hierarchy for {user} and {target}.')
        if target.top_role >= user.top_role:
            if user.guild.owner == user:
                return True
            else:
                return False
        elif target.top_role <= user.top_role:
            return True

    async def convert_time_to_seconds(self, time: str):
        times = []
        current = ""
        for char in time:
            current += char
            if char.isalpha():
                times.append(current)
                current = ""

        if current != "":
            return False

        seconds = 0
        for time in times:
            seconds += int(time[:-1]) * time_convert[time[-1]]

        return seconds

    # TODO: implement configuration for ephemeral messages
    async def ephemeral_moderation_messages(self, guild: discord.Guild) -> bool:
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('Moderation cog loaded.')

    @app_commands.command(name='nickname', description="Change nicknames")
    @app_commands.default_permissions(manage_nicknames=True)
    @app_commands.guild_only()
    async def nickname(self, interaction: discord.Interaction, user: discord.Member, *, newnick: str):
        await interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        if not await self.permissionHierarchyCheck(interaction.user, user):
            interaction.followup.send(
                "You cannot moderate users higher than you", ephemeral=True)
            return
        try:
            await user.edit(nick=newnick)
        except discord.errors.Forbidden:
            await interaction.followup.send('Missing required permissions. Is the user above me?', ephemeral=True)
        else:
            embed = discord.Embed(
                title=f"Nickname change result", description=None, color=discord.Color.green())
            embed.add_field(name="User", value=user.mention, inline=False)
            embed.add_field(name="Old nickname",
                            value=user.display_name, inline=False)
            embed.add_field(name="New nickname", value=newnick, inline=False)
            embed.set_footer(
                text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
            await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))

    @app_commands.command(name='purge', description="Purge messages")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def purge(self, interaction: discord.Interaction, limit: int, user: discord.Member = None):
        await interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        msg = []
        if not user:
            await interaction.channel.purge(limit=limit, before=interaction.created_at)
        else:
            async for m in interaction.channel.history():
                if len(msg) == limit:
                    break
                if m.author == user:
                    msg.append(m)
            await interaction.channel.delete_messages(msg)

        embed = discord.Embed(title=f"Purge result",
                              description=None, color=discord.Color.green())
        embed.add_field(name="Messages purged", value=limit, inline=False)
        embed.set_footer(
            text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))

    @app_commands.command(name='mute', description="Mute users")
    @app_commands.default_permissions(mute_members=True)
    @app_commands.guild_only()
    async def mute(self, interaction: discord.Interaction, user: discord.Member, *, reason: str = None):
        await interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        if not await self.permissionHierarchyCheck(interaction.user, user):
            interaction.followup.send(
                "You cannot moderate users higher than you", ephemeral=True)
            return

        role = discord.utils.get(interaction.guild.roles, name="Muted")
        await user.add_roles(role, reason=f'by {interaction.user} for {reason}')
        embed = discord.Embed(title=f"Mute result",
                              description=None, color=discord.Color.red())
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Muted", value=user.mention, inline=False)
        embed.set_footer(
            text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))

    @app_commands.command(name='unmute', description="Unmute users")
    @app_commands.default_permissions(mute_members=True)
    @app_commands.guild_only()
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        if not await self.permissionHierarchyCheck(interaction.user, user):
            interaction.followup.send(
                "You cannot moderate users higher than you", ephemeral=True)
            return
        # eventually, we will detect mutes from tempmutes
        await user.edit(timed_out_until=None)
        # await ctx.channel.send(f'{member.mention} was untempmuted.', delete_after=10)

        role = discord.utils.get(interaction.guild.roles, name="Muted")
        await user.remove_roles(role)
        embed = discord.Embed(title=f"Unmute result",
                              description=None, color=discord.Color.green())
        embed.add_field(name="Unmuted", value=user.mention, inline=False)
        embed.set_footer(
            text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))

    @app_commands.command(name='tempmute', description="Timeout users")
    @app_commands.default_permissions(mute_members=True)
    @app_commands.guild_only()
    async def tempmute(self, interaction: discord.Interaction, user: discord.Member, time: str, *, reason: str = None):
        await interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        if not await self.permissionHierarchyCheck(interaction.user, user):
            interaction.followup.send(
                "You cannot moderate users higher than you", ephemeral=True)
            return
        seconds = await self.convert_time_to_seconds(time)
        if seconds is False:
            await interaction.followup.send('Invalid time!', ephemeral=True)
            return
        if seconds > 1209600:
            await interaction.followup.send('Timeouts can only be 2 weeks max!', ephemeral=True)
            return
        until = timedelta(seconds=await self.convert_time_to_seconds(time))
        await user.timeout(until, reason=reason)
        time_formatted = humanize.precisedelta(until, format="%0.0f")
        embed = discord.Embed(title=f"Timeout result",
                              description=None, color=discord.Color.red())
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Timeout", value=user.mention, inline=False)
        embed.add_field(name="Duration", value=time_formatted, inline=False)
        embed.set_footer(
            text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        await user.send(f"You have been muted in **{interaction.guild}** for *{time_formatted}*")

    @app_commands.command(name='kick', description="Kick users")
    @app_commands.describe(users="The users to kick. Can be multiple users, comma separated.")
    @app_commands.describe(delete_message_time="The time to delete messages from the user. Can be up to 7 days.")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(self, interaction: discord.Interaction, users: str, reason: str = None, delete_message_time: str = None):
        interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        users = [user.strip() for user in users.split(',')]

        converter: commands.MemberConverter = commands.MemberConverter()
        ctx = await commands.Context.from_interaction(interaction)
        for i, user in enumerate(users):
            user = await converter.convert(ctx, user)
            users[i] = user

            if not await self.permissionHierarchyCheck(interaction.user, user):
                interaction.followup.send(
                    "You cannot moderate users higher than you", ephemeral=True)
                return

            await interaction.guild.kick(user, reason=reason)

        if max_delete_time is not None:
            try:
                max_delete_time = await self.convert_time_to_seconds(delete_message_time)
            except:
                interaction.followup.send(
                    "You cannot input invalid numbers.", ephemeral=True)
                return
        else:
            max_delete_time = 0

        for channel in interaction.guild.channels:
            async for message in channel.history():
                if message.author in users:
                    if message.created_at > interaction.created_at - timedelta(seconds=max_delete_time):
                        await message.delete()


        embed = discord.Embed(title=f"Kick result",
                              description=None, color=discord.Color.red())
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Kicked", value=', '.join(
            [user.mention for user in users]), inline=False)
        embed.set_footer(
            text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))

    @app_commands.command(name='ban', description="Ban users")
    @app_commands.describe(users="The users to ban. Can be multiple users, comma separated.")
    @app_commands.describe(delete_message_time="The time to delete messages from the user. Can be up to 7 days.")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(self, interaction: discord.Interaction, users: str, reason: str = None, delete_message_time: str = None):
        interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))

        if delete_message_time is not None:
            try:
                delete_message_time = await self.convert_time_to_seconds(delete_message_time)
            except:
                interaction.followup.send(
                    "You cannot input invalid numbers.", ephemeral=True)
                return
        else:
            delete_message_time = 0
        
        if delete_message_time > 604800:
            interaction.followup.send(
                "You can only delete messages up to 7 days old", ephemeral=True)
            return
        
        users = [user.strip() for user in users.split(',')]

        converter: commands.MemberConverter = commands.MemberConverter()
        ctx = await commands.Context.from_interaction(interaction)
        for i, user in enumerate(users):
            user = await converter.convert(ctx, user)
            users[i] = user

            if not await self.permissionHierarchyCheck(interaction.user, user):
                interaction.followup.send(
                    "You cannot moderate users higher than you", ephemeral=True)
                return

            await interaction.guild.ban(user, reason=reason, delete_message_seconds=delete_message_time)

        embed = discord.Embed(title=f"Ban result",
                              description=None, color=discord.Color.red())
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned", value=', '.join(
            [user.mention for user in users]), inline=False)
        embed.set_footer(
            text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))

    @app_commands.command(name='unban', description="Unban users")
    @app_commands.describe(users="The users to unban. Can be multiple users, comma separated.")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(self, interaction: discord.Interaction, users: str, reason: str = None):
        interaction.response.defer(ephemeral=await self.ephemeral_moderation_messages(interaction.guild))
        users = [user.strip() for user in users.split(',')]

        converter: commands.MemberConverter = commands.MemberConverter()
        ctx = await commands.Context.from_interaction(interaction)
        for i, user in enumerate(users):
            user = await converter.convert(ctx, user)
            users[i] = user

            if not await self.permissionHierarchyCheck(interaction.user, user):
                interaction.followup.send(
                    "You cannot moderate users higher than you", ephemeral=True)
                return

            await interaction.guild.unban(user, reason=reason)

        embed = discord.Embed(title=f"Unban result",
                              description=None, color=discord.Color.red())
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Unbanned", value=', '.join(
            [user.mention for user in users]), inline=False)
        embed.set_footer(
            text=f"Moderator: {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.followup.send(embed=embed, ephemeral=await self.ephemeral_moderation_messages(interaction.guild))


async def setup(bot):
    await bot.add_cog(Moderation(bot))

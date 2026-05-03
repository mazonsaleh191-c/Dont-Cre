import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# نظام الاقتصاد
economy_file = 'economy.json'

def load_economy():
    if os.path.exists(economy_file):
        with open(economy_file, 'r') as f:
            return json.load(f)
    return {}

def save_economy(data):
    with open(economy_file, 'w') as f:
        json.dump(data, f, indent=4)

economy_data = load_economy()

@bot.event
async def on_ready():
    print(f'{bot.user.name} اشتغل!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ضيفني لسيرفرك يسطا بقا 😉"))
    daily_reset.start()

# ========== الألعاب ==========
@bot.command(name='رول')
async def roll(ctx, dice: str = "d6"):
    try:
        if 'd' in dice:
            rolls, limit = map(int, dice.split('d'))
        else:
            rolls = 1
            limit = int(dice)
    except:
        await ctx.send("اكتب صح زي `!رول d20` او `!رول 2d6`")
        return
    
    results = [random.randint(1, limit) for _ in range(rolls)]
    total = sum(results)
    await ctx.send(f'🎲 الرول: {", ".join(map(str, results))}\n📊 المجموع: {total}')

@bot.command(name='حظ')
async def luck(ctx):
    fortunes = [
        "🎯 حظك جامد النهاردة!",
        "💀 خلي بالك شوية",
        "💰 هتخش فلوس",
        "😴 نصيبك نايم",
        "🚀 هتطلع برة",
        "🍀 حظك حلو",
        "⚡ جاهز لأي حاجة",
        "🎁 هتاخد هدية"
    ]
    await ctx.send(random.choice(fortunes))

@bot.command(name='تخين')
async def fat(ctx, member: discord.Member = None):
    member = member or ctx.author
    fatness = random.randint(1, 100)
    emoji = "🐷" if fatness > 70 else "🐔" if fatness > 30 else "🐒"
    await ctx.send(f'{emoji} {member.name} تخين {fatness}%')

@bot.command(name='قرعة')
async def raffle(ctx, *participants):
    if not participants:
        await ctx.send("ضيف الناس بعد الامر زي `!قرعة احمد محمد علي`")
        return
    winner = random.choice(participants)
    await ctx.send(f'🎉 الفائز: **{winner}**')

@bot.command(name='رميه')
async def coinflip(ctx):
    result = random.choice(["⭕ وجه", "❌ ضهر"])
    await ctx.send(f'🪙 {result}')

@bot.command(name='رقم')
async def guess(ctx, number: int = None):
    if number is None or number < 1 or number > 10:
        await ctx.send("اختار رقم من 1 ل 10: `!رقم 5`")
        return
    
    secret = random.randint(1, 10)
    if number == secret:
        await ctx.send(f'🎯 صح! الرقم كان {secret}')
    else:
        await ctx.send(f'❌ غلط! الرقم كان {secret}')

@bot.command(name='سؤال')
async def question(ctx, *, question):
    answers = [
        "✅ اه",
        "❌ لا",
        "🤔 مش متأكد",
        "🎯 اكيد",
        "🚫 مستحيل",
        "💭 اسأل تاني",
        "⏳ بعد شوية",
        "🌟 نص نص"
    ]
    await ctx.send(f'سؤال: {question}\nجواب: {random.choice(answers)}')

# ========== الإدارة ==========
@bot.command(name='مسح')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f'🗑️ مسحت {len(deleted)-1} رسالة', delete_after=3)

@bot.command(name='كيك')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="مش محدد"):
    await member.kick(reason=reason)
    await ctx.send(f'👢 كيك {member.mention} - السبب: {reason}')

@bot.command(name='بان')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="مش محدد"):
    await member.ban(reason=reason)
    await ctx.send(f'🔨 بان {member.mention} - السبب: {reason}')

@bot.command(name='انبان')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned = await ctx.guild.bans()
    for ban_entry in banned:
        user = ban_entry.user
        if user.name.lower() == member_name.lower():
            await ctx.guild.unban(user)
            await ctx.send(f'✅ انبان {user.name}')
            return
    await ctx.send('❌ مش موجود في البان ليست')

@bot.command(name='ميوت')
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member, *, reason="مش محدد"):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'🔇 ميوت {member.mention} - السبب: {reason}')

@bot.command(name='انميوت')
@commands.has_permissions(mute_members=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role and muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f'🔊 انميوت {member.mention}')

@bot.command(name='رتبه')
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f'🎖️ ضفت رتبة {role.name} لـ {member.mention}')

@bot.command(name='انشاءروم')
@commands.has_permissions(manage_channels=True)
async def createroom(ctx, name):
    guild = ctx.guild
    await guild.create_text_channel(name)
    await ctx.send(f'✅ اتعمل روم {name}')

# ========== الترفيه ==========
@bot.command(name='قول')
async def say(ctx, *, message):
    await ctx.send(message)

@bot.command(name='صوت')
async def voice(ctx):
    voices = [
        "🎤 يلا بينا يا ولاد",
        "🎤 احا يعني",
        "🎤 مش فاضي يا عم",
        "🎤 ده نور جامد",
        "🎤 يسطا بطل لعب",
        "🎤 خليك ف دمك",
        "🎤 انتا عبيط؟",
        "🎤 ماشي يا برنس"
    ]
    await ctx.send(random.choice(voices))

@bot.command(name='ميم')
async def meme(ctx):
    memes = [
        "https://i.imgur.com/removed_for_example.jpg",
        "https://i.imgur.com/removed_for_example2.jpg",
        "https://i.imgur.com/removed_for_example3.jpg"
    ]
    await ctx.send(f'😂 {random.choice(memes)}')

@bot.command(name='همسة')
async def whisper(ctx, member: discord.Member, *, message):
    try:
        await member.send(f'📩 همسة من {ctx.author.name}: {message}')
        await ctx.send('✅ الهمسة اتسلمت', delete_after=3)
    except:
        await ctx.send('❌ مينفعش ابعت له')

@bot.command(name='افكر')
async def think(ctx):
    thoughts = [
        "🤔 هو انتا ليه كدا؟",
        "🧠 انا بفكر في حاجة",
        "💭 مش عارف",
        "🎯 عايز اقولك حاجة",
        "🚀 احنا هنروح فين؟"
    ]
    await ctx.send(random.choice(thoughts))

@bot.command(name='رقص')
async def dance(ctx):
    dances = [
        "💃 يلا نرقص",
        "🕺 اهووه",
        "🎶 شيل رجلك",
        "✨ استعد للرقص"
    ]
    await ctx.send(random.choice(dances))

# ========== الاقتصاد ==========
@bot.command(name='فلوس')
async def money(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    
    if user_id not in economy_data:
        economy_data[user_id] = {"money": 100, "bank": 0}
        save_economy(economy_data)
    
    money = economy_data[user_id]["money"]
    bank = economy_data[user_id]["bank"]
    await ctx.send(f'💰 {member.name}\n💵 جيب: {money}\n🏦 بنك: {bank}')

@bot.command(name='عمل')
async def work(ctx):
    user_id = str(ctx.author.id)
    
    if user_id not in economy_data:
        economy_data[user_id] = {"money": 100, "bank": 0}
    
    earned = random.randint(50, 200)
    economy_data[user_id]["money"] += earned
    save_economy(economy_data)
    
    jobs = ["مبرمج", "دكتور", "مهندس", "تاجر", "سائق"]
    job = random.choice(jobs)
    await ctx.send(f'👷 اشتغلت {job} وكسبت {earned} 💵')

@bot.command(name='سرقه')
async def steal(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send("❌ مينفعش تسرق نفسك")
        return
    
    thief_id = str(ctx.author.id)
    target_id = str(member.id)
    
    if target_id not in economy_data:
        economy_data[target_id] = {"money": 100, "bank": 0}
    
    if thief_id not in economy_data:
        economy_data[thief_id] = {"money": 100, "bank": 0}
    
    target_money = economy_data[target_id]["money"]
    
    if target_money < 10:
        await ctx.send("❌ الفقير ماعندهش فلوس")
        return
    
    success = random.random() < 0.4
    if success:
        stolen = random.randint(10, min(100, target_money))
        economy_data[target_id]["money"] -= stolen
        economy_data[thief_id]["money"] += stolen
        save_economy(economy_data)
        await ctx.send(f'🦹 سرقت {stolen} 💵 من {member.name}')
    else:
        fine = random.randint(20, 50)
        economy_data[thief_id]["money"] = max(0, economy_data[thief_id]["money"] - fine)
        save_economy(economy_data)
        await ctx.send(f'🚓 اتحبست ودفعت غرامة {fine} 💵')

@bot.command(name='تحويل')
async def transfer(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ المبلغ لازم يكون اكبر من صفر")
        return
    
    sender_id = str(ctx.author.id)
    
    if sender_id not in economy_data:
        economy_data[sender_id] = {"money": 100, "bank": 0}
    
    if economy_data[sender_id]["money"] < amount:
        await ctx.send("❌ معندكش فلوس كفاية")
        return
    
    receiver_id = str(member.id)
    if receiver_id not in economy_data:
        economy_data[receiver_id] = {"money": 100, "bank": 0}
    
    economy_data[sender_id]["money"] -= amount
    economy_data[receiver_id]["money"] += amount
    save_economy(economy_data)
    
    await ctx.send(f'✅ حولت {amount} 💵 لـ {member.name}')

@bot.command(name='ايداع')
async def deposit(ctx, amount: int):
    if amount <= 0:
        await ctx.send("❌ المبلغ لازم يكون اكبر من صفر")
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in economy_data:
        economy_data[user_id] = {"money": 100, "bank": 0}
    
    if economy_data[user_id]["money"] < amount:
        await ctx.send("❌ معندكش فلوس كفاية في الجيب")
        return
    
    economy_data[user_id]["money"] -= amount
    economy_data[user_id]["bank"] += amount
    save_economy(economy_data)
    
    await ctx.send(f'🏦 اودعت {amount} 💵 في البنك')

@bot.command(name='سحب')
async def withdraw(ctx, amount: int):
    if amount <= 0:
        await ctx.send("❌ المبلغ لازم يكون اكبر من صفر")
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in economy_data:
        economy_data[user_id] = {"money": 100, "bank": 0}
    
    if economy_data[user_id]["bank"] < amount:
        await ctx.send("❌ معندكش فلوس كفاية في البنك")
        return
    
    economy_data[user_id]["bank"] -= amount
    economy_data[user_id]["money"] += amount
    save_economy(economy_data)
    
    await ctx.send(f'💵 سحبت {amount} 💵 من البنك')

@bot.command(name='توبفلوس')
async def topmoney(ctx):
    if not economy_data:
        await ctx.send("❌ مفيش بيانات")
        return
    
    sorted_users = sorted(economy_data.items(), key=lambda x: x[1]["money"] + x[1]["bank"], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 اغنى الناس", color=discord.Color.gold())
    for i, (user_id, data) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(int(user_id))
            name = user.name
        except:
            name = f"User {user_id}"
        
        total = data["money"] + data["bank"]
        embed.add_field(name=f"{i}. {name}", value=f"💰 {total}", inline=False)
    
    await ctx.send(embed=embed)

@tasks.loop(hours=24)
async def daily_reset():
    pass

@bot.command(name='يومي')
async def daily(ctx):
    user_id = str(ctx.author.id)
    
    if user_id not in economy_data:
        economy_data[user_id] = {"money": 100, "bank": 0, "last_daily": None}
    
    now = datetime.now().strftime("%Y-%m-%d")
    
    if "last_daily" in economy_data[user_id] and economy_data[user_id]["last_daily"] == now:
        await ctx.send("❌ اخدت المكافأة اليومية النهاردة")
        return
    
    reward = random.randint(100, 300)
    economy_data[user_id]["money"] += reward
    economy_data[user_id]["last_daily"] = now
    save_economy(economy_data)
    
    await ctx.send(f'🎁 اخدت المكافأة اليومية: {reward} 💵')

# ========== معلومات ==========
@bot.command(name='معرف')
async def info(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    embed = discord.Embed(title=f"👤 {member.name}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="🆔 ID", value=member.id, inline=False)
    embed.add_field(name="📅 انضم", value=member.joined_at.strftime("%Y-%m-%d %H:%M"), inline=False)
    embed.add_field(name="🎮 حالة", value=str(member.status).title(), inline=False)
    embed.add_field(name="🎖️ رتب", value=", ".join([role.name for role in member.roles[1:]]), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='سيرفر')
async def server(ctx):
    guild = ctx.guild
    
    embed = discord.Embed(title=f"🏰 {guild.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👥 الاعضاء", value=guild.member_count, inline=True)
    embed.add_field(name="📅 تاريخ التأسيس", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="👑 المالك", value=guild.owner.name, inline=True)
    embed.add_field(name="📊 الرومات", value=len(guild.channels), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='بنك')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 البنك: {latency}ms')

@bot.command(name='وقت')
async def time(ctx):
    now = datetime.now()
    await ctx.send(f'🕐 الوقت: {now.strftime("%Y-%m-%d %H:%M:%S")}')

@bot.command(name='افاتار')
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url if member.avatar else member.default_avatar.url)

# ========== مساعدة ==========
@bot.command(name='مساعدة')
async def helpme(ctx):
    embed = discord.Embed(title="📚 كل الأوامر", color=discord.Color.purple())
    
    embed.add_field(
        name="🎮 الألعاب",
        value="```رول, حظ, تخين, قرعة, رميه, رقم, سؤال```",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ الإدارة",
        value="```مسح, كيك, بان, انبان, ميوت, انميوت, رتبه, انشاءروم```",
        inline=False
    )
    
    embed.add_field(
        name="😂 الترفيه",
        value="```قول, صوت, ميم, همسة, افكر, رقص```",
        inline=False
    )
    
    embed.add_field(
        name="💰 الاقتصاد",
        value="```فلوس, عمل, سرقه, تحويل, ايداع, سحب, توبفلوس, يومي```",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ معلومات",
        value="```معرف, سيرفر, بنك, وقت, افاتار```",
        inline=False
    )
    
    embed.set_footer(text=f"طلب {ctx.author.name}")
    await ctx.send(embed=embed)

TOKEN = os.getenv('BOT_TOKEN')
bot.run(TOKEN)

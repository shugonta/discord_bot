import os


class Config():
    token = os.environ["DISCORD_TOKEN"]
    guild = os.environ["DISCORD_GUILD"]
    general = 345804296991801345
    off_sanka = 389011203206283264
    aeon_cinema = 345804296991801346
    pyongyang = 404983177669771264
    bot_id = os.environ["BOT_ID"]
    timeout_time = 600
    post_interval = 1200
    invite_interval = 1200
    status_check_period = 10
    delete_period = 3600

    line_access_token = os.environ["LINE_TOKEN"]

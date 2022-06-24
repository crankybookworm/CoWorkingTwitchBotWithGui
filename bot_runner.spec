#- * -mode: python - * -

block_cipher = None


a = Analysis(['bot_runner.py'],
    pathex = ['D:/Development/Python/PomoBot/pomoenv/Lib/site-packages'],
    binaries = [],
    datas = [
        ('BotResources', 'BotResources')
        # ('BotResources/resources/PomoBotUI.ui', 'BotResources/resources/PomoBotUI.ui'),
        # ('BotResources/static/images/CoWorkingBotIcon.png', 'BotResources/static/images/CoWorkingBotIcon.png'),
        # ('BotResources/resources/darkeum.qss', 'BotResources/resources/darkeum.qss'),
        # ('BotResources/resources/botConfig.json', 'BotResources/resources/botConfig.json'),
        # ('BotResources/resources/chatBotConfig.json', 'BotResources/resources/chatBotConfig.json'),
        # ('BotResources/resources/botDatabase.json', 'BotResources/resources/botDatabase.json'),
        # ('BotResources/resources/flipDict.json', 'BotResources/resources/flipDict.json'),
        # ('BotResources/static/styles/pomoBoard.css', 'BotResources/static/styles/pomoBoard.css'),
        # ('BotResources/templates/pomoBoard.html', 'BotResources/templates/pomoBoard.html'),
        # ('BotResources/templates/index.html', 'BotResources/templates/index.html')
    ],
    hiddenimports = [],
    hookspath = [],
    runtime_hooks = [],
    excludes = [],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,)
pyz = PYZ(a.pure, a.zipped_data,
    cipher = block_cipher)
exe = EXE(pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        # exclude_binaries = True,
        name = 'CoWorkingBot',
        debug = False,
        bootloader_ignore_signals = False,
        strip = False,
        upx = True,
        upx_exclude=[],
        runtime_tmpdir=None,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        console = False,
        # icon='BotResources/static/images/CoWorkingBotIcon.png'
    )

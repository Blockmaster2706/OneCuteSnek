def command_help(command):
    if   command == "help":
        return "Thisss Command. Returnsss help for the ssspecified Command.\nSssyntax: /help command:(COMMAND)"
    elif command == "setlogs":
        return 'Sssetsss the Channel to log commandsss in. Removesss the LogChannel if Action is "Remove". Ssspecify Channel asss ID. Admin only.'
    elif command == "database":
        return "The Database Command. Only for the Developer."
    elif command == "reminder":
        return "Ussse thisss to remind you of sssomething. Sssyntax: /reminder reminder: (message) hours: x(optional) minutes: x(optional) seconds: x(optional)"
    elif command == "commandtoggle":
        return "Togglesss Commandsss on or off. Only for the Developer."
    elif command == "sneki":
        return "Jussst a little tessst command"
prgname = "process.py"

def usage(base, commands, message):
	print("Usage: %s %s command ..." % (prgname, base))
	if message is not None:
		print("")
		print(message)
		print("")
	print("Commands:\n")
	for cmd in commands:
		if cmd != "*":
			if len(commands[cmd]) >= 3:
				print("%s - %s\n\t%s %s %s %s\n" % (cmd, commands[cmd][1], prgname, base, cmd, commands[cmd][2]))
			else:
				print("%s - %s\n\t%s %s %s ...\n" % (cmd, commands[cmd][1], prgname, base, cmd))
		else:
			if len(commands[cmd]) >= 3:
				print("default - %s\n\t%s %s %s %s\n" % (commands[cmd][1], prgname, base, cmd, commands[cmd][2]))
			else:
				print("default - %s\n\t%s %s %s ...\n" % (commands[cmd][1], prgname, base, cmd))

	print("help - print usage\n")

def run(argv, base, commands, message=None):
	if len(argv) == 0 or argv[0] == "help":
		usage(base, commands, message)
		return
	cmd = argv[0]
	if cmd not in commands:
		cmd = "*"
		commands[cmd][0](argv)
	else:
		commands[cmd][0](argv[1:])


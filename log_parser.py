from bot_proto import *
from log_proto import *
import datetime
import sys


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Need flag; -s status, -w for work"
        sys.exit()
    elif len(sys.argv) == 2:
        flag = sys.argv[1]
        hours_count = 24

    elif len(sys.argv) == 3:
        flag = sys.argv[1]
        hours_count = int(sys.argv[2])
    else:
        print "Too many args"
        sys.exit()


    log = logDB()

    if flag == "-s":
        status = log.get_status(hours_count)
        print status
        sys.exit()

    elif flag == "-w":
        telebot = Telegram()
        while True:
            try:
                if datetime.datetime.now().hour == 12:
                    telebot.send_text(telebot.admin_id, log.get_status(hours_count))
                    time.sleep(60 * 60)

            except KeyboardInterrupt:
                print 'Interrupt by user..'
                break

            except Exception, e:
                log_event(get_exception())
    else:
        print "Wrong flag"
        sys.exit()

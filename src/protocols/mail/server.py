import sys

sys.path.append('../../../src')
import sound.stream as stream
import sound.emitter as em
import sound.listener as ls
import time
import smtplib
import threading as t

stream.start_stream()

# First listen must be forever and not trigger a timeout
initial_listen = True

# Things to receive
valid_commands = ['FR', 'TO', 'DT']  # Known with data
parameters = ["", "", []]  # Parameters for each valid command
required_commands = valid_commands[:3]  # What it still needs, the non-sound version would use it sometimes

# Retry variables
actively_listening = False  # Whether it is actually listening to a signal not just waiting for a header tone
retry = False  # Whether an error was encountered and retrying is active
retry_attempts = 0  # How many times retried to send but got no response (will stop after 3 retries)
hard_retry_attempts = 0  # Includes getting back errors as retries (will stop after 10 retries)

# Timeout variables
counting = False  # Whether to count (not counting during for example actually listening to a signal or emitting)
time_count_in_ms = 0  # Current process time
time_limit_in_s = 10  # How long to wait before timeout
status = ""  # Last sent message (for retransmits)


# Exits the program
def suicide(*_):
    global counting
    stream.end_stream()
    counting = False
    quit()


# Status callback function, which stops couting while the program is listening and resumes it once it no longer is
def listener_status(sts):
    global counting
    global retry
    global actively_listening
    if sts == "Confirmation tone confirmed!":
        actively_listening = True
        counting = False
    elif sts in ["Playing data.", "Starting live emitting."]:  # This has to change once status callbacks in listening
        counting = True
    elif sts in ["Ending recording.", "Data recieved and message end!"]:
        actively_listening = False


# This will trigger with each retry, where it will wait 10 seconds and retransmit, then wait 10 seconds for reply
def timeout():
    global hard_retry_attempts
    global status

    time.sleep(10)
    if hard_retry_attempts > 10:
        em.emit(callback_func=suicide, type="test_stream", header="QT", data="",
                status_callback=listener_status)
        suicide()
        return
    if retry_attempts > 3:
        em.emit(callback_func=suicide, type="test_stream", header="QT", data="",
                status_callback=listener_status)
        suicide()
        return
    if retry and not actively_listening:
        hard_retry_attempts += 1
        print(f"Sending: 12 No reply")
        status = "12 No reply"
        em.emit(callback_func=callback, type="test_stream", header="12", data="No reply",
                status_callback=listener_status)
        return


# This will count exit the program if it hasn't received anything for a long time and is not in retrying mode
# because in retrying mode it will exit itself after a couple retries
def global_timeout():
    global time_count_in_ms
    global retry, retry_attempts, hard_retry_attempts
    global status

    time_count_in_ms = 0
    while not retry and counting and not stream.PLAYING and not stream.EMITTING:
        time.sleep(0.1)
        if not retry and counting and not stream.PLAYING and not stream.EMITTING:
            time_count_in_ms += 100
        else:
            return
        if time_count_in_ms > (time_limit_in_s * 1000):
            if not retry:
                print("Timeout while waiting for reply from the server...")
                retry = True
                print(f"Sending: 13 Timeout")
                status = "13 Timeout"
                em.emit(callback_func=callback, type="test_stream", header="13", data="Timeout",
                        status_callback=listener_status)
                return


# Main callback function
def callback(header=None, data=None):
    global retry, retry_attempts, hard_retry_attempts
    global status
    global time_count_in_ms, counting
    global initial_listen

    time_count_in_ms = 0  # Timer is reset since received something as it was called back
    if f"{header} {data}" == status:  # heard its own error message (don't know how else to do it yet XD
        return

    if header is None:  # Means it is listening
        if retry:  # It will start another retry attempt if it is listening for a reply after retrying
            retry_attempts += 1
            t.Thread(target=timeout).start()
        else:
            if not initial_listen:  # If not the first listen it starts global timeout
                t.Thread(target=global_timeout).start()
            else:
                initial_listen = False
        counting = True
        ls.listen(callback_func=callback, status_callback=listener_status)
    else:  # Heard something
        print(f"Received request from client: {header} {data}")

        if header not in valid_commands + ['EX', 'ML', 'DN', 'AC']:  # Unknown command received from server
            retry = True
            status = "11 Unknown command"
            print("Sending: 11 Unknown command")
            em.emit(callback_func=callback, type="test_stream", header="11", data="Unknown command",
                    status_callback=listener_status)
        else:  # Got valid command
            retry = False
            retry_attempts = 0
            status = ""
            if header == "ML":  # Request to start communication
                print("Sending: SD ")  # Ask client to send data
                em.emit(callback_func=callback, type="test_stream", header="SD", data="",
                        status_callback=listener_status)

            elif header == "EX":  # Asked to exit
                sender = parameters[0].split(" ")[0]
                recipient = parameters[1]
                sbject = "".join(parameters[2]).split("\n\n")[0]
                text = "\n\n".join(parameters[2]).split("\n\n")[1:]
                text = f"Subject: {sbject}\n" \
                       f"From: {sender}\n" \
                       f"To: {recipient}\n" \
                       f"\n{text}"
                with open("received_mail.txt", "w") as f:
                    f.write(text)
                print("Sending: QT ")  # Tell client to quit
                em.emit(callback_func=suicide, type="test_stream", header="QT", data="",
                        status_callback=listener_status)

            elif header == "DT":  # Got sent data (appends, so it can be sent by lines for example)
                required_commands.pop(required_commands.index('DT'))
                parameters[2].append(data)
                print("Sending: OK ")
                em.emit(callback_func=callback, type="test_stream", header="OK", data="",
                        status_callback=listener_status)

            elif header in ['FR', 'TO']:  # Gets sent author or recipient
                parameters[valid_commands.index(header)] = data
                required_commands.pop(required_commands.index(header))
                print("Sending: OK ")
                em.emit(callback_func=callback, type="test_stream", header="OK", data="",
                        status_callback=listener_status)

            elif header == "DN":  # Asked to transmit through the internet
                print("Sending: WT ")  # Tells client to wait (so it doesn't time out and retransmit needlessly)
                em.emit(callback_func=callback, type="test_stream", header="WT", data="",
                        status_callback=listener_status)

            elif header == "AC":  # Asked to send back reply after sending
                try:  # Tries sending email through SMTP
                    sender = parameters[0].split(" ")[0]
                    password = parameters[0].split(" ")[1]
                    recipient = parameters[1]
                    sbject = "".join(parameters[2]).split("\n\n")[0]
                    text = "".join(parameters[2]).split("\n\n")[1]
                    text = f"Subject: {sbject}\n" \
                           f"From: {sender}\n" \
                           f"To: {recipient}\n" \
                           f"\n{text}"
                    send_mail_through_smtp(sendr=sender, auth=password, recpnt=recipient, cntent=text)
                    print("Sending: SC ")
                    em.emit(callback_func=callback, type="test_stream", header="SC", data="",
                            status_callback=listener_status)
                except Exception as e:  # Returns exception
                    print(f"Could not send mail, exception: {e}")
                    print("Sending: 55 Could not send")
                    em.emit(callback_func=callback, type="test_stream", header="55", data="Could not send",
                            status_callback=listener_status)


# Checks valid email, not used yet in sound version
def valid_mail(mail_address: str):
    add = mail_address
    if "@" not in add:
        return 0
    name, host = add.split("@")[0], add.split("@")[1]
    if len(name) == 0:
        return 0
    if "." not in host:
        return 0
    for i in host.split("."):
        if len(i) == 0:
            return 0
    return 1


# Sends email through SMTP
def send_mail_through_smtp(sendr, recpnt, cntent, auth):
    mail_sender = sendr
    mail_auth = auth
    mail_recipient = recpnt
    mail_content = cntent

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(mail_sender, mail_auth)
        print("Logged in...")
        server.sendmail(mail_sender, mail_recipient, mail_content)
    except Exception as ee:
        print(f'Could not send email, encountered error: {ee}')
        return 1

    print('Email sent successfully')
    return 0


# main
ls.listen(callback)

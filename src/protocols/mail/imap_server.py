import sys

sys.path.append('../../../src')
import sound.stream as stream
import sound.emitter as em
import sound.listener as ls
import time
import threading as t
import imaplib
import email
import quopri


# Function to communicate with imap server
def get_latest_email(set_seen=False):
    global username
    global password

    # Parameters to get
    emailFrom = ""
    emailSubject = ""
    emailDate = ""
    emailPlainText = ""
    emailHtml = ""

    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    imap.login(username, password1)
    print('logged in...')

    res, number_of_messages = imap.select('"[Gmail]/All Mail"')
    if res != "OK":
        print("'OK' response not received form the server...")

    res, unseen = imap.search('utf-8', 'Unseen')
    if res != 'OK':
        print("'OK' response not received from the server...")

    unseen_mail_ids = unseen[0].split()

    # working from the latest email skipping emails by google (boss' command)

    if len(unseen_mail_ids) == 0:
        print("No unread emails...")
    else:
        mid = unseen_mail_ids[-1].decode('utf-8')

        # Get body
        res, content = imap.fetch(mid, '(BODY.PEEK[])')
        if res != 'OK':
            print("'OK' response not received from the server...")
        # Using email lib makes it easy, we can parse it manually if we want, but it's mega annoying
        content = email.message_from_bytes(content[0][1])
        emailDate = content.get('Date')
        emailFrom = content.get('From')
        emailSubject = content.get('Subject')

        for part in content.walk():
            if part.get_content_type() == 'text/plain':
                emailPlainText = bytes(part)
            elif part.get_content_type() == 'text/html':
                emailHtml = bytes(part)

        def get_text(p):
            email_part = p
            text1 = ""
            chrset = 'utf-8'
            header = True
            for line in email_part.split(b"\n"):
                if line == b'':
                    header = False
                if header:
                    if line.split(b' ')[0] == b'Content-Transfer-Encoding:':
                        if line.split(b' ')[1] == b'quoted-printable':
                            email_part = quopri.decodestring(email_part)
                    elif line.split(b' ')[0] == b'Content-Type:':
                        try:
                            chrset = line.split()[2][8:]
                        except IndexError:
                            chrset = 'UTF-8'
                else:
                    text1 += line.decode(chrset.decode('utf-8'), errors='ignore') + '\n'

            return text1

        emailPlainText = get_text(emailPlainText)
        get_text(emailHtml)

        # Asking whether to set as read
        if set_seen:
            imap.store(mid, '+FLAGS', '\\Seen')

    imap.close()
    output = f"From: {emailFrom}\n" \
             f"Subject: {emailSubject}\n" \
             f"Date: {emailDate}\n" \
             f"\n" \
             f"{emailPlainText}"

    print('success...')

    return output


# SOUND THING

stream.start_stream()

# User settings
username = ""
password = ""

# Initial listen need to take forever
initial_listen = True

# Timeout variables
time_limit_in_s = 5  # How long to wait for a response
time_count_in_ms = 0  # Current process time
counting = False  # Whether to count (not counting during for example actually listening to a signal or emitting)

# Variables
clientReady = False  # No use yet, when client said it is ready to receive data

# Retry variables
last_header = ""  # Last header sent (for retransmissio)
last_content = ""  # Last content sent (for retransmissio)
actively_listening = False  # Whether actually listening, so it doesn't count then
retry = False  # Whether an error was encountered and retrying is active
retry_attempts = 0  # How many times retried to send but got no response (will stop after 3 retries)
hard_retry_attempts = 0  # Includes getting back errors as retries (will stop after 10 retries)


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
    global last_header, last_content
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
        print(f"Retrying Sending: {last_header} {last_content}")
        em.emit(callback_func=callback, type="test_stream", header=last_header, data=last_content,
                status_callback=listener_status)
        return


# This will count exit the program if it hasn't received anything for a long time and is not in retrying mode
# because in retrying mode it will exit itself after a couple retries
def global_timeout():  # If you don't get any response for a long time
    global time_count_in_ms
    global retry, retry_attempts, hard_retry_attempts
    global last_header, last_content

    time_count_in_ms = 0
    while not retry and counting and not stream.PLAYING and not stream.EMITTING:
        time.sleep(0.1)
        if not retry and counting and not stream.PLAYING and not stream.EMITTING:
            time_count_in_ms += 100
        else:
            return
        if time_count_in_ms > (time_limit_in_s * 1000):
            if not retry:
                print("Timeout while waiting for reply from the client...")
                retry = True
                print(f"Retrying Sending: {last_header} {last_content}")
                em.emit(callback_func=callback, type="test_stream", header=last_header, data=last_content,
                        status_callback=listener_status)
                return


# Main callback function
def callback(header=None, data=None):
    global retry, retry_attempts, hard_retry_attempts
    global last_header, last_content
    global time_count_in_ms, counting
    global initial_listen
    global clientReady
    global username, password

    time_count_in_ms = 0  # Timer is reset since received something as it was called back
    if (header, data) == (last_header, last_content):  # heard its own error message
        return

    if header is None:  # Means it is listening
        if retry:  # It will start another retry attempt
            retry_attempts += 1
            t.Thread(target=timeout).start()
        else:  # It will start global timetou (which exits if retry emitting is done)
            if not initial_listen:  # Not on initial listen because then it's liek a server just listens forever
                t.Thread(target=global_timeout).start()
            else:
                initial_listen = False
        counting = True
        ls.listen(callback_func=callback, status_callback=listener_status)
    else:  # Heard something
        print(f"Received request from client: {header} {data}")

        if header not in ['FT', 'AR', 'RV', 'EX']:  # Not in valid commands
            retry = True
            last_header = '11'
            last_content = 'Unknown command'
            print("Sending: 11 Unknown command")
            em.emit(callback_func=callback, type="test_stream", header="11", data="Unknown command",
                    status_callback=listener_status)
        else:  # Received valid command
            retry = False
            retry_attempts = 0
            last_header, last_content = "", ""

            if header == "FT":  # Asked to fetch
                # Fetch is in form: "FT <username> <password>"
                username = data.split(" ")[0]
                password = data.split(" ")[1]

                print("Sending: WT ")  # Asks client to wait
                last_header = "WT"
                last_content = ""
                em.emit(callback_func=callback, type="test_stream", header="WT", data="",
                        status_callback=listener_status)

            elif header == "AR":  # Client is waiting, can fetch email through imap
                clientReady = True
                try:
                    # Gets latest email
                    latest_mail = get_latest_email()

                    # Separates header and content
                    mail_header, mail_content = latest_mail.split("\n\n")[0], latest_mail.split("\n\n")[1]
                    optimized_header = mail_header.split("\n")
                    # Shortens header so it's faster over sound
                    for i in range(len(optimized_header)):
                        if optimized_header[i].split(" ")[0] == "From:":
                            senders = []
                            authors = optimized_header[i].split(" ")[1:]
                            for author in authors:
                                if author[0] == "<":
                                    senders.append(author[1:-1])
                            optimized_header[i] = "FR: " + ", ".join(senders)
                        elif optimized_header[i].split(" ")[0] == "Subject:":
                            optimized_header[i] = "SJ: " + " ".join(optimized_header[i].split(" ")[1:])
                        elif optimized_header[i].split(" ")[0] == "Date:":
                            optimized_header[i] = "DA: " + " ".join(optimized_header[i].split(" ")[1:])
                    optimized_header = "\n".join(optimized_header)

                    to_be_sent = "\n\n".join([optimized_header, mail_content])

                    # Sends whole message at once
                    print("Sending: DT " + to_be_sent)
                    last_header = "DT"
                    last_content = to_be_sent
                    if clientReady:
                        em.emit(callback_func=callback, type="test_stream", header="DT", data=to_be_sent,
                                status_callback=listener_status)
                except Exception as e:
                    print(f"Could not fetch mail, exception: {e}")
                    print("Sending: 55 Error while fetching")
                    em.emit(callback_func=suicide, type="test_stream", header="55", data="Error while fetching",
                            status_callback=listener_status)

            # If asked to exit will ask client to quit and then exit
            elif header == "RV" or header == "EX":
                print("Sending: QT ")
                em.emit(callback_func=suicide, type="test_stream", header="QT", data="",
                        status_callback=listener_status)


# main
ls.listen(callback)

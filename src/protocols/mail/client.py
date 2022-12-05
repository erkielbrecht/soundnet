import sys
sys.path.append('../../../src')
import sound.stream as stream
import sound.emitter as em
import sound.listener as ls
import time
import threading as t

stream.start_stream()

# Timeout variables
time_limit_in_s = 5     # How long to wait for a response
time_count_in_ms = 0    # Current process time
counting = False        # Whether to count (not counting during for example actually listening to a signal or emitting)

# Variables
send_over_internet = True   # Whether to save the email or whether to send it over the actual internet
serverReady = False         # No use yet, when server said it is ready to receive data
last_header = "ML"          # Header of the last message sent (to retransmit it if server throws error)
last_content = ""           # Content of the last message sent (to retransmit it if server throws error)

# Retry variables
actively_listening = False  # Whether it is actually listening to a signal not just waiting for a header tone
retry = False               # Whether an error was encountered and retrying is active
retry_attempts = 0          # How many times retried to send but got no response (will stop after 3 retries)
hard_retry_attempts = 0     # Includes getting back errors as retries (will stop after 10 retries)

# User arguments
username = ""   # Username of user
password = ""   # Password of user
# Mail arguments
subject = ""        # Mail subject
recipients = ['']   # Mail recipient email addresses in a list
text = ""           # Data to transmit

# Turns them into commands understandable by the server
mailFrom = f'FR {username} {password}'
mailTo = f'TO {", ".join(recipients)}'
mailData = f'DT {subject}\n\n{text}'
current_cmd_index = 0   # Which command it is supposed to send next from V
cmnds = [mailFrom, mailTo, mailData]    # <------------------------- this list


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
    global current_cmd_index
    global hard_retry_attempts
    time.sleep(10)
    if hard_retry_attempts > 10:
        em.emit(callback_func=suicide, type="test_stream", header="EX", data="",
                status_callback=listener_status)
        suicide()
        return
    if retry_attempts > 3:
        em.emit(callback_func=suicide, type="test_stream", header="EX", data="",
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
def global_timeout():
    global time_count_in_ms
    global retry, retry_attempts, hard_retry_attempts

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
                print(f"Retrying Sending: {last_header} {last_content}")
                em.emit(callback_func=callback, type="test_stream", header=last_header, data=last_content,
                        status_callback=listener_status)
                return


# Main callback function
def callback(header=None, data=None):
    global counting, time_count_in_ms, time_limit_in_s
    global current_cmd_index
    global serverReady
    global last_header, last_content
    global retry, retry_attempts, hard_retry_attempts

    time_count_in_ms = 0    # Timer is reset since received something as it was called back
    if (header, data) == (last_header, last_content):  # heard itself (just temporary fix hopefuly)
        return

    if header is None:  # Means it is listening
        if retry:   # It will start another retry attempt
            retry_attempts += 1
            t.Thread(target=timeout).start()
        else:   # It will start global timetou (which exits if retry emitting is done)
            t.Thread(target=global_timeout).start()
        counting = True
        ls.listen(callback_func=callback, status_callback=listener_status)
    else:   # Heard something
        counting = True
        retry_attempts = 0  # Because got response
        time_limit_in_s = 5
        print(f"Received reply from server: {header} {data}")

        if header not in ["QT", "55", "OK", "SD", "WT", "SC"]:   # Got error
            retry = True
            print(f"Retrying Sending: {last_header} {last_content}")
            em.emit(callback_func=callback, type="test_stream", header=last_header, data=last_content,
                    status_callback=listener_status)
        else:
            retry = False
            hard_retry_attempts = 0     # Got non-error response
            if header == "QT" or header == "55":    # Either asked to quit or unrecoverable error
                if header == "55":  # Will tell the server to exit and then exit itself
                    last_header = "EX"
                    em.emit(callback_func=suicide, type="test_stream", header="EX", data="",
                            status_callback=listener_status)
                else:
                    time_count_in_ms = 0
                    suicide()

            elif header == "SD" or (serverReady and header == "OK"):    # Got the initial SD (send) req or OK response
                time_count_in_ms = 0
                serverReady = True
                if current_cmd_index == 3:  # It exhausted all things needed to send (from, to, data etc.)

                    if send_over_internet:  # Will ask to be actually sent
                        print(f"Sending: DN ")
                        last_header = "DN"
                        em.emit(callback_func=callback, type="test_stream", header="DN", data="",
                                status_callback=listener_status)
                    else:   # Other computer has email can exit
                        print("Sending: EX ")
                        last_header = "EX"
                        em.emit(callback_func=callback, type="test_stream", header="EX", data="",
                                status_callback=listener_status)
                else:   # Will continue sending data
                    cmmnd, content = cmnds[current_cmd_index][:2], cmnds[current_cmd_index][3:]
                    last_header = cmmnd
                    last_content = content
                    print(f"Sending: {cmmnd} {content}")
                    em.emit(callback_func=callback, type="test_stream", header=cmmnd, data=content,
                            status_callback=listener_status)
                current_cmd_index += 1
            elif header == "WT":        # If asked to wait (server is trying to process and send email)
                time_limit_in_s = 60    # it will wait 60 seconds until timeout unlike the normal 5s
                print("Sending: AC ")
                last_header = "AC"
                last_content = ""
                # Sends back "AC" to ask server to report when it has sent/not sent the email
                em.emit(callback_func=callback, type="test_stream", header="AC", data="",
                        status_callback=listener_status)
            elif header == "SC":    # SC (success) in sending email, will ask server to EX (exit)
                print("Sending: EX ")
                last_header = "EX"
                em.emit(callback_func=callback, type="test_stream", header="EX", data="",
                        status_callback=listener_status)


# main
print("Sending: ML ")
t.Thread(target=global_timeout).start()
em.emit(callback_func=callback, type="test_stream", header="ML", data="", status_callback=listener_status)

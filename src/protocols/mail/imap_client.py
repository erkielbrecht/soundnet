import sys
sys.path.append('../../../src')
import sound.stream as stream
import sound.emitter as em
import sound.listener as ls
import time
import threading as t

stream.start_stream()

# User settings
username = ""   # User mail
password = ""   # User password

# Timeout variables
time_limit_in_s = 5     # How long to wait for reply
time_count_in_ms = 0    # Current time
counting = False        # Whether to count (not counting during for example actually listening to a signal or emitting)
last_header = "FT"      # Header of the last message sent (to retransmit it if server throws error)
last_content = ""       # Content of the last message sent (to retransmit it if server throws error)

# Retry variables
actively_listening = False  # Whether it is actually listening to a signal not just waiting for a header tone
retry = False               # Whether an error was encountered and retrying is active
retry_attempts = 0          # How many times retried to send but got no response (will stop after 3 retries)
hard_retry_attempts = 0     # Includes getting back errors as retries (will stop after 10 retries)


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
def global_timeout():  # If you don't get any response for a long time
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
    global last_header, last_content
    global retry, retry_attempts, hard_retry_attempts

    time_count_in_ms = 0    # Timer is reset since received something as it was called back
    if (header, data) == (last_header, last_content):  # heard itself (just temporary fix hopefuly)
        return

    if header is None:  # Means it is listening
        if retry:  # It will start another retry attempt
            retry_attempts += 1
            t.Thread(target=timeout).start()
        else:  # It will start global timetou (which exits if retry emitting is done)
            t.Thread(target=global_timeout).start()
        counting = True
        ls.listen(callback_func=callback, status_callback=listener_status)
    else:   # Heard something
        counting = True
        retry_attempts = 0  # Because got response
        time_limit_in_s = 5
        print(f"Received reply from server: {header} {data}")
        if header not in ["55", "WT", "DT", "QT"]:  # Unexpected or error reply
            retry = True
            print(f"Retrying Sending: {last_header} {last_content}")
            em.emit(callback_func=callback, type="test_stream", header=last_header, data=last_content,
                    status_callback=listener_status)
        else:   # Correct response
            retry = False
            hard_retry_attempts = 0     # Because got non-error response
            if header == "QT" or header == "55":    # Asked to quit or unrecoverable error
                if header == "55":  # Unrecoverable error will tell server to exit
                    last_header = "EX"
                    em.emit(callback_func=suicide, type="test_stream", header="EX", data="",
                            status_callback=listener_status)
                else:
                    time_count_in_ms = 0
                    suicide()
            elif header == "WT":        # Asked to wait
                time_limit_in_s = 60    # will wait 60 secs instead of 5s
                print("Sending: AR ")   # And tells server it's awaiting reply
                last_header = "AR"
                last_content = ""
                em.emit(callback_func=callback, type="test_stream", header="AR", data="",
                        status_callback=listener_status)
            elif header == "DT":    # Got sent mail data
                mail_data = data
                mail_header, mail_content = mail_data.split("\n\n")[0], "\n\n".join(mail_data.split("\n\n")[1:])
                mail_header.split("\n")

                # Transforms the simplified short data for sound transfer to readable text
                for i in range(len(mail_header)):
                    if mail_header[i][:2] == "FR":
                        mail_header[i] = "From: " + mail_header[i][4:]
                    elif mail_header[i][:2] == "DA":
                        mail_header[i] = "Date: " + mail_header[i][4:]
                    elif mail_header[i][:2] == "SJ":
                        mail_header[i] = "Subject: " + mail_header[i][4:]
                "\n".join(mail_header)
                mail_data = "\n\n".join([mail_header, mail_content])

                # Writes it down to a file
                with open("new_mail.txt", "w") as f:
                    f.write(mail_data)
                print("Sending: RV ")
                last_header = "RV"
                em.emit(callback_func=callback, type="test_stream", header="RV", data="",
                        status_callback=listener_status)


# Main
print("Sending: FT ")
t.Thread(target=global_timeout).start()
em.emit(callback_func=callback, type="test_stream", header="FT", data=f"{username} {password}",
        status_callback=listener_status)

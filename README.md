This is the EoCS repository for the year 1 project 

# **SoundNet**

## 1. Protocols

### 1.1 Hypertext Transfer Protocol

​	The ***HTTP protocol*** allows for two methods: ***GET*** and  ***HEAD***. The *GET* method fetches a website from a server based on it's name, which is then found on the server using an internal sort of *DNS*.

​	The  *HEAD* method only gets the header of a website, which contains information about the website, such as files it includes or it's expiry date.

​	Additionally, the *HTTP protocol* has infrastructure around it to cache websites and will not redownload them from the server if they're not past their expiry date.

### 1.2 Email Transfer Protocol

​	The ***Mail protocol*** is actually an umbrella term for two different but similar protocols. One to fetch emails from a server, and the other to send emails through the server. The email sending protocol is either saved into the other computer which acts as a server or can use the server computer to send an email through the real internet through the actual *SMTP* protocol.

​	Similarly, the fetching protocol actually fetches the last unseen email using *IMAP*, and after parsing it, sends it over to the client in a specific format.

### 1.3 Streaming Protocol

​	The ***Streaming protocol*** is used for "real-time" data transfer, where the listening computer is translating and processing frequencies symbol after symbol. This protocol is much more error prone compared to the underlying sound protocol the other protocols use, which first records and only then analyses a message.

## 2. Modulation/Demodulation

### 2.1 Symbol to Frequency Translation

​	The symbol to frequency dictionary uses ASCII and in its configuration has a default frequency set. This frequency can not be too low, as lower frequencies take longer to pick up with the same confidence (they take longer to send the same amount of waves). On the other hand if they're too high, the microphone will have a harder time picking them up from high frequency background noise and also because computer speakers often can't emit them so loud.

​	Next then there is a step size, which is the difference in Hz between two frequencies. This also has to be set high enough so that the computer can properly differentiate between frequencies, but also low enough, so that the frequencies don't get too high causing the same problem with high frequencies described above.

​	Every ASCII character consists of two frequencies player right after each other. This works on a decimal system where [base frequency, base frequency] would be the first ASCII character [base frequency, base frequency + 1 step] would be the second and [base frequenct + 1 step, base frequency] would be the 10th ASCII character. This is because if each character would have it's own unique frequency, there wouldn't be enough frequencies with a large enough step size to differentiate them. It would however be faster.

### 2.2 Turning Frequencies into Sound

​	Once a string has been converted using the method described above, a sound  sine wave is calculated by an algorithm and then an actual sound file is generated. This sound file consists of a meeting tone, which the server is always listening for for a time that's based on the configuration and then a message type tone, which specifies what kind of message is about to be sent. Afterwards the frequency of each symbol is appended of a certain time length set in the configuration. Finally, a frequency signifying the end of a message is added. This is then manually pushed into the computer's speakers output data queue, which causes the speakers to emit a sound.

### 2.3 Picking Up a Signal

​	A server script is always listening for the handshake frequency. Once it hears it for a certain time and can be sure it is not a random noise it starts recording all the frequencies it hears until it hears the message ending frequency. It then translates this back to a string.

# 3. Demo video

(Press the image)

[![Watch the video](https://img.youtube.com/vi/ebeE0NMbJdk/maxresdefault.jpg)](https://youtu.be/ebeE0NMbJdk)

# 4. Project members
### Adam Bujna
### Hector Coronado Riscos
### Filipe Dos Santos Cordeiro
### Erki Elbrecht
### Pol Garccia Tombas
### Keith Iqbal
### Mauro Kasirin
### Gideon Mazzola
### Tarik Začiragić
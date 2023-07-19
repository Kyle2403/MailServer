The program's purpose is to mimic Simple Mail Transfer Protocol (SMTP), so it focuses on handling different requests like an SMTP server and saving mail on disk instead of actually sending mails. 

You can initialize the server by openning server.bat and connect to the server using "telnet 127.0.0.1 port_num" with port_num being the number in server_config.txt and send data to the server to have an email saved. In that case, the right order of commands is EHLO 127.0.0.1 -> MAIL FROM:<example@gmail.com> -> RCPT TO:<reciepient@gmail.com> -> DATA -> type in mail content and enter (SUBJECT and DATE can be added by typing Subject: your_subject and Date: your_date as an input of DATA) -> type "." and enter to finish. After that the cycle can be done again to save more mails. If the commands are mispelled/not capital, order is wrong or the format of email and time are not correct, the server would display error code and corresponding messages. The format can be seen below.

Or you can comply mail in the send folder, open another terminal to run "python client.py client_config.txt" and that mail would be saved in the inbox folder. In that case, mail file has to have the following fields and in the exact order shown: (see the sample in send folder)
 Sender information.
	One line and non-empty.
	Email address in <> bracket.
	example: From: <someone@domain.com>
 Recipent(s) information.
	One line and non-empty.
	Email address in <> bracket.
	Separated by , if there are multiple address supplied.
	To: <other@domain.com>
	example: To: <other@domain.com>,<other.other@domain.com>
 Sending time.
	One line and non-empty.
	Date and time in RFC 5322 format.
	example: Mon, 14 Aug 2006 02:34:56 -0600
 Subject.
	One line and non-empty.
 Body.
	Multiple lines in ASCII.
Raw data from the LimeSurvey questionaires.

The intro interview gives feedback on how to setup 2FA with Blue TOTP on a website.
In `intro_question_codes.csv` all codes are listed with their meanings.

## SUS = System Usabilty Scale
The answers AO01, AO02, AO03, AO04 and AO05 represent how much the participant agrees with the question/statement.
| answer option | meaning |
| --- | --- |
| AO01 | "totally disagree" |
| AO02 | "mostly disagree" |
| AO03 | "neutral" |
| AO04 | "mostly agree" |
| AO05 | "totally agree" |

## SUS11 = additional question to SUS (11. question)
It's meant to check, if the resulting score calcutated by the SUS covers what a participant thinks about the
usability of the system.
| answer option | meaning |
| --- | --- |
| AO01 | "the worst imagineable" |
| AO02 | "awful" |
| AO03 | "poor" |
| AO04 | "OK" |
| AO05 | "good" |
| AO06 | "excellent" |
| AO07 | "the best imagineable" |

## UEQ = User Experience Questionaire
AO01 is the answer option that totally agrees with the left sided term.
AO04 is neutral.
AO07 is the answer option that totally agrees with the right sided term.
E.g. "fast | slow" -> answer was AO02, then the participant evaluates the system as fast, but it 
could be faster (AO01).

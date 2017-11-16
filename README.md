# 타타루(Tataru)
한국어 명령어를 받는 디스코드용의 다목적 봇입니다.

접두사는 "타타루"로 고정되어있지만, main.py 파일에서 수정 가능합니다.

A Korean Discord bot for multiple purpose.

Prefix is fixed to "타타루" but you can change it by changing it in main.py

# Prerequisites
- Discord Bot User Token
    - (https://discordapp.com/developers/applications/me)
- Naver Client ID & Secret to use "Naver" cog
    - (https://developers.naver.com/apps/#/register)

# Installing
**Linux**
- libopus-dev

# 명령어(Commands)
## General
#### 골라줘(Choose)
`타타루` `골라줘` `고를` `대상` `들`
```
타타루 골라줘 하나 둘 셋
>>하나
```
여러 가지 인자들 중 하나를 골라줍니다.

Choose one of the arguments

*****

#### 따귀(Slap)
`타타루` `따귀` `대상`
```
타타루 따귀 @찬피
>>@찬피의 뺨을 후려갈겼어용
```
주어진 대상의 따귀를 후려갈깁니다.

Slap the target given.

*****

#### 주사위(Dice)
`타타루` `주사위` `최대숫자`
```
타타루 주사위
>>@WoodNeck이(가) 주사위를 굴려 🎲30이(가) 나왔어용
타타루 주사위 1000
>>@WoodNeck이(가) 주사위를 굴려 🎲174이(가) 나왔어용
```
1~100 사이의 주사위를 굴립니다. 1보다 큰 인자가 주어질 경우 1과 해당 인자 사이의 주사위를 굴립니다.

Roll dice between 1 to 100. If number is given, roll dice between 1 to that number.

*****

#### 핑(Ping)
`타타루` `핑`
```
타타루 핑
>>퐁이에용
```
테스트용, 퐁을 반환합니다.

Returns message "Pong".

*****

#### 초대(Invite)
`타타루` `초대`
```
타타루 초대
>>https://discordapp.com/oauth2/authorize?client_id=357073005819723777&scope=bot&permissions=-1
```
타타루 봇 초대용 링크를 반환합니다.

Returns invite link for Tataru bot.

*****

## Naver
#### 지식인(Naver Q&A community search)
`타타루` `지식인` `물어볼 내용`
물어볼 내용에 해당하는 지식인 검색 결과를 반환합니다.

Returns 지식iN(Naver Q&A Community) search result.

*****

#### 번역(Translation)
`타타루` `번역할 언어`로 `번역해줘/기계번역해줘` `번역할 내용`
```
타타루 영어로 번역해줘 안녕하세요
>>Hello.
타타루 영어로 기계번역해줘 안녕하세요
>>你好。
```

네이버의 Papago SMT와 NMT API를 사용한 한국어->외국어 번역 기능입니다.

`번역해줘` 사용시 Papago SMT API를, `기계번역해줘` 사용시 Papago NMT API를 사용합니다.

`번역해줘` 사용시 `영어`, `중국어`, `일본어`로 번역 가능합니다.

`기계번역해줘` 사용시 `영어`, `중국어`로 번역 가능합니다.

Korean to foriegn language translation command using Naver's Papago SMT, NMT API.

Bot will use Papago SMT API when using `번역해줘` command, and will use NMT API when using `기계번역해줘` command.

Can translate to `English`, `Chinese`, `Japanese` when using `번역해줘` command.

Can translate to `English`, `Chinese` when using `기계번역해줘` command.

*****

#### 로마자변환(Romanization)
`타타루` `로마자변환` `변환할 인명`
```
타타루 로마자변환 홍길동
>> Hong Gildong
```
네이버 API를 이용, 인명을 로마자변환한 결과를 받아옵니다.

By using Naver API, bot sends romanization result of Korean name.

*****

#### 얼굴인식(Face recognition)
`타타루` `얼굴인식` `인식할 이미지 URL`

네이버 API를 이용, 이미지에서 얼굴인식된 결과를 받아옵니다. 얼굴인식 결과에는 감정, 성별, 나이, 닮은 연예인과 같은 정보가 포함되어 있습니다.

By using Naver API, bot sends face recognition result including info of emotion, gender, age, similar celebrity.

*****

#### 네이버이미지(Naver image search)
`타타루` `네이버이미지` `검색할 내용`

네이버의 이미지 검색 결과를 받아옵니다.

Returns image search result from Naver.

*****

## Google
#### 이미지(Image)
`타타루` `이미지` `검색할 내용`

구글의 이미지 검색 결과를 받아옵니다.

Returns image search result from Google.

*****

## Dangerous Invite
#### 위험한초대(Dangerous Invite Game)
`타타루` `위험한초대`

위험한초대 게임을 만듭니다.

Creates a new game of "Dangerous Invite"

명령어 (`타타루 위험한초대`) 입력시 DM을 받고, DM을 통해 3글자의 단어 입력시 위험한초대 게임이 시작됩니다.

게임 시작시 24시간의 시간이 주어지며, 시간 내에 시작한 봇을 제외한 어떤 유저든 해당 단어가 포함된 단어를 말할 시 서버에서 추방되고 게임이 종료됩니다. 혹은 24시간의 시간이 지날시 게임을 시작한 사람이 서버에서 추방됩니다.

By putting a command `타타루 위험한초대`, user will get a DM. After saying 3-length word in DM to bot, game will start.

24 hours are given after starting game. Anyone except bots saying a sentence including target word will be kicked from server. If no one says target word within 24 hours, the one who started game will be kicked from server.

*****

# 추가기능(Additional Features)
## GG2 Bubble 변환
채팅 메시지가 GG2 bubble에 해당하는 메시지일시 해당 버블 이미지를 전송.

If message content is same with GG2 bubble, it will send that image.

- 사용가능한 GG2 Bubbles (Available GG2 Bubbles)
    - `z1` ~ `z9`
    - `x1` ~ `x29`
    - `c1` ~ `c9`
    - `e`
    - `센트리`
    - `우버`

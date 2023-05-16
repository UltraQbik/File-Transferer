# FT

## communication

### Allways available

 c: PubKey please
 
 s: **pubkey**

### Sending files (untrusted)

#c: I want to send a file

 s: I dont know you, key please

#c: **pubkey**

 s: I dont trust you, wait for confirmation


### Sending files (Trusted)


#c: I want to send a file

#s: Sure, details?

#c: Size: 26, Name: readmelol.txt, encryption_key: 140EAF7B0698A4C44683513CBE01378161C5CAD38100AA13AFE2C3383913318A

#s: When your ready

*c: **file** **checksum**

#s: Chill, file saved
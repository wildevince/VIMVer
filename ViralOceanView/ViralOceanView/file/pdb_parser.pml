#get structure
fetch 6xqb, async=0

#representations
hide
show cartoon
show sticks, resn GTP
show spheres, name MG

# colors
### color by chain
color yellow, chain A
color green, chain B
color black, resn GTP or name MG
bg_color white

# export en GLmol
###
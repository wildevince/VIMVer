import drawSvg as draw
from django.conf import settings 

from Bio import SeqIO, SeqRecord


def GetMutations(RefSeq:str, inputSeq:str):
    ### fasta
    import Bio.SeqIO
    res = []
    aa1:str=""
    aa2:str=""
    j:int=0
    gap:bool=False
    #print(f"RefSeq:{len(RefSeq)} ; inputSeq:{len(inputSeq)}")
    for i in range(len(RefSeq)):
        if(RefSeq[i] != inputSeq[i]):
            if(RefSeq[i] == '-'): # if a gap in refseq : insertion
                gap = True
                aa1 = "-"
                aa2 += inputSeq[i] 
            else: # not a gap in refseq
                if(gap): # end of long gap
                    res.append((aa1,j,aa2))
                    aa1 = ""
                    aa2 = ""
                    gap = False
                # event = substitution 
                aa1 = RefSeq[i]
                aa2 = inputSeq[i]
                res.append((aa1,j,aa2))
                j+=1
        else:
            # event match
            if(RefSeq[i] != '-'):
                j+=1
            if(gap): # end long gap
                res.append((aa1,j,aa2))
                aa1 = ""
                aa2 = ""
                gap = False
            
            #res.append((RefSeq[i],i,inputSeq[i]))
            #if(inputSeq[i]=='-'):
                #print(RefSeq[i]+str(i)+inputSeq[i])
    #print(*res)
    return res  # *(0:char, 1:int, 2:char)


def draw_figure(jobkey:str, Title:str, Type:str, mode:str ,refseq_length:int, Mutations:list, **kwargs:dict):
    """
    ### Parameters \n
    jobkey (str) => PK of user's query \n
    Title (str) => on top midle of figure \n
    Type (str) => "protein" or "rna" \n
    mode (str) => "mutation"(default) or "general \n
    refseq_length (int) => length of refseq \n
    
    ### Output \n
    generation of image .png and .svg \n
    return drawSvg object on Jupyter \n
    
    ### Function details\n
    """
    ###  methods
    def getTextLength(text:str, police:int) -> float:
        """text:str and police_size:int -> length:float""" 
        #return 7.0* police /12.0 * len(text)
        lowers:int = 0
        uppers:int = 0
        for i in range(len(text)):
            if(text[i].isdigit() or text[i].isupper() or text[i] in "mw_%v "):
                uppers += 1
            else:
                lowers += 1
        return 1*(lowers)*police/5 + 3*(uppers)*police/5

    def draw_legend(text:str, police:int, x:float, y:float, center:float=0, color:str='black'):
        """text:str, police_size:int, x_position:number, y_position:number, center[0-1]:0=start,0.5=midle,1=end -> drawSvg.Text()"""
        text_length:float = getTextLength(text, police)
        return draw.Text(text, police, x = x-text_length*(center), y = y-police, fill=color)

    ## dimensions
    max_width:int = kwargs.get("max_width", 400)
    max_height:int = kwargs.get("max_height", 120)
    Origin = (0, -max_height/2)  # center left
    Vscale:float=max_width/refseq_length #num pixel // residue
    if("max_width" not in kwargs.keys()):
        while(Vscale < 0.4): 
            if(max_width >= 600): #max width 600 pixel
                break
            max_width *= 1.10
            Vscale = max_width/refseq_length
    Vscale = int(Vscale*1000)/1000.0

    Hscale:float=len(Mutations)/refseq_length #num mut // len seq 
    if("max_height" not in kwargs.keys()):
        if(Hscale >= 0.3): #max height 250 pix or 400
            max_height = 250 
            if(Hscale >= 0.7):
                max_height  = 400
    Hscale = int(Hscale*1000)/1000.0

    ## drawSvg object : root
    root = draw.Drawing(max_width, max_height, origin=Origin, displayInline=False)

    ## mode
    if(mode != "mutation"):
        pass
    elif(mode == "mutation" and Mutations is not None): # mode == mutation
        mutation_switch:bool = False
        levels:list = [] #  *[x position:int]
        
        ## draw background 
        root.append(draw.Rectangle(*Origin, max_width, max_height, fill='white'))

        ## Draw Genome/protein
        X:int = 0
        Y:int = int(-1*max_height/20)
        W:int = max_width
        H:int = int(1*max_height/20)
        if(H < 10): #min height of genome : 10 pix
            H = 10
            Y = -10
        if(Type == "protein"): #color of genome color
            backgroundColor = "blue"
        elif(Type == "rna"):
            backgroundColor = "cyan"
        else:
            backgroundColor = "grey"
        root.append(draw.Rectangle(X, Y, W, H, fill=backgroundColor))

        ## Draw Mutations
        for mutation in Mutations:
            # mutation = (0:aa1:char ,1:position:int, 2:aa2:char)
            ### variables
            is_gap = (mutation[2] == '-')
            pos_i:float = mutation[1]       ###  current position in seq
            pos_x = X+pos_i*Vscale           ###  current relative x_position in figure

            ### draw line
            color:str = "grey" if(is_gap) else "red" if(mutation[0]=='-') else "black"
            sx:float = pos_x
            sy:int = H/2 if(mutation_switch) else H/4
            ex:float = pos_x
            ey:int = -H - (H/4 if(mutation_switch) else H/2)

            ### draw label
            ## mutation label text
            label_text:str = mutation[0]+str(mutation[1])+mutation[2]
            label_text_length:int = getTextLength(label_text, 6)
            ## position x in figure of mutation label
            x_label:float = pos_x 
            # shift on pos_x depending on global position => avoid overlapp with end of figure
            x_label_gap:float = float(label_text_length *(pos_i/refseq_length)) 
            x_label -= x_label_gap 

            ## position y in figure of mutation label
            y_label:int = 0  
            next_level = None
            I:int = len(levels)

            if(mutation_switch): 
                # extract upper levels
                for i in range(0, len(levels), 2):
                    if(pos_x > levels[i]): # is safe to write
                        y_label = H * (i/2+1) + 6 # set y position of mutation label
                        levels[i] = pos_x + label_text_length # update next safe x position on this level
                        break
                    next_level = i + 2
                if(y_label == 0 or len(range(0, len(levels), 2)) == 0):
                    if(len(range(0, len(levels), 2)) == 0):
                        next_level = 0
                    levels += [0]*2
                    levels[next_level] = pos_x + label_text_length
                    y_label  = H * (next_level/2 +1) + 6
            
            else: 
                # extract downer levels
                if(len(levels) > 1):
                    for i in range(1, len(levels), 2):
                        if(pos_x > levels[i]): # is safe to write
                            y_label = -H * ((i+1)/2 +1) - 6# set y position of mutation label
                            levels[i] = pos_x + label_text_length # update next safe x position on this level
                            break
                        next_level = i + 2
                    # if not safe level then new level
                if(y_label == 0 or not len(levels) > 1):
                    if(not len(levels) > 1):
                        next_level = 1
                    levels += [0]*2
                    levels[next_level] = pos_x + label_text_length
                    y_label  = -H * ((next_level+1)/2 +1) - 6

            ## float correction on pos_x
            pos_x = int(pos_x * 100)/100.0

            #print("pos_i, pos_x, mutation_switch, label_text, Levels, next_level : ")
            #print("\t", pos_i, pos_x, mutation_switch, label_text, len(levels), next_level)

            color:str = "green" if(is_gap) else "red" if(mutation[0]=='-') else "black"
            root.append(draw.Line(sx,sy,ex,ey, stroke=color, stroke_width=1, fill='none', marker_end='none'))
            #root.append(draw.Rectangle(x=x_label, y=y_label, width=label_text_length, height=6,  fill='green'))
            root.append(draw.Text(label_text, 6, x=x_label, y=y_label, fill=color))
            mutation_switch = not mutation_switch
        
        ## caption
        if(Title != "" and Type != ""):
            ### draw title 
            root.append(draw.Text(Title, 12, x=1*max_width/3 -2*getTextLength(Title,12)/3, y=max_height/2-12))
            root.append(draw_legend(Type,8,0,max_height/2-12,0))
            ### draw caption
            if(Type == "protein"):
                root.append(draw_legend('Nter', 8, 1, H *(-1/10), 0, 'white'))
                root.append(draw_legend('Cter', 8, max_width-getTextLength("Cter",8), H *(-1/10), 1, 'white'))
            elif(Type == "rna"):
                root.append(draw_legend("5'", 8, 1, H *(-1/10), 0, 'black'))
                root.append(draw_legend("3'", 8, max_width-getTextLength("3'",8), H *(-1/10), 1, 'black'))
            ### draw length
            text = "length: "+str(refseq_length)
            root.append(draw_legend(text, 8, max_width-getTextLength(text,8), max_height/2, 1))
            ### draw legend
            root.append(draw.Text("- insertion", 6, x=0, y=2-max_height/2, fill='red'))
            root.append(draw.Text("- mismatch", 6, x=0, y=8-max_height/2, fill='black'))
            root.append(draw.Text("- deletion", 6, x=0, y=14-max_height/2, fill='green'))
            ### draw Vscale value
            if(False):
                text:str = "Vscale: 1/"+str(Vscale)
                text_length:float = getTextLength(text, 8)
                root.append(draw.Text(text, 8, x = max_width-text_length , y = max_height/2 -8))
        
    ## display print
    if(jobkey != ""):
        outfilepath:str = f"outSVG/{jobkey}_{Type}_{refseq_length}"
        root.setPixelScale(2)
        if(kwargs.get("save")):
            root.saveSvg(settings.MEDIA_ROOT+"/"+outfilepath+".svg")
        root.savePng(settings.MEDIA_ROOT+"/"+outfilepath+".png")
        #root.rasterize()
        #return root
        if(Type=='rna'):
            return {
                'path':settings.MEDIA_URL+outfilepath+".png",
                'max_width':max_width,
                'max_height':max_height,
                }
        return settings.MEDIA_URL+outfilepath+".png"

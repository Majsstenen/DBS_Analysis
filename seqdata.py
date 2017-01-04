class ReadPair(object):
    """ object that represent an illumina read pair
    """
    
    import misc
    
    def __init__(self, currentRead, header, sequenceR1, sequenceR2, qualR1, qualR2, direction, h1, h2, h3, constructType, dbsMatch, dbsSeq, dbsQual, mappingFlagR1, refNameR1, refPosR1, mapQR1, cigarR1, mappingFlagR2, refNameR2, refPosR2, mapQR2, cigarR2,insertSize, clusterId, annotations, fromFastqId, r1PositionInFile,r2PositionInFile,bamFilePos,individual_id,analysisfolder):

        # original read info
        # comming from the raw fastq files, except id that is a increasing int for each entry in fastq
        # the sequences (r1Seq & r2Seq) and qualities (r1Qual & r2Qual) are never saved to the database (except as None values) and are thus not usable after the handle identification step, they could theoretically be added to database though will take a lot of exttra space
        self.id = currentRead
        self.header   = header
        self.r1Seq      = sequenceR1 	#self.r1Seq      = strip3primN(sequence1)
        self.r2Seq      = sequenceR2 	#self.r2Seq      = strip3primN(sequence2)
        self.r1Qual     = qualR1
        self.r2Qual     = qualR2
        self.fileOrigin = fromFastqId # this is the id in the database of the fastq file that the read pair comes from
        self.r1PositionInFile = r1PositionInFile # this is the positions in the original files where the read is found
        self.r2PositionInFile = r2PositionInFile

        # handle flags and coordinates
        # theese varibles stores handle coordinates for the three main handles
        self.direction = direction
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3
        self.construct = constructType # the contsructtype dict stores information about which handles were found dunring handle identification

        # these variables are used to find the handles connected to the individual id and the id sequence/barcode
        # the handles are only used during the dbs_handle_identifier step and are never saved to the database and are therefore defined as None here
        self.fwd_primer = None
        self.individual_id_primer = None
        self.individual_id = individual_id

        # dbs flags and coordinates
        self.dbs = None
        self.dbsSeq = dbsSeq # this is the actual dbs sequence part of the read pair
        self.dbsQual = dbsQual
        self.dbsmatch = dbsMatch # flag true or false depensing on if the dbs sequence math the expected pattern
        self.dbsPrimaryCoordinates = None

        # other flags and information
        self.analysisfolder = None # this is a holder for defining an analysis folder link
        self.annotations = annotations # a dict with other info that does not really fit anywhere else
        self.overlap = None
        self.brokenSequence = ''
        #self.construct = None
        self.insert= None # this is a list with the part of the sequence that are between the handles only used in dbs_handle_identifier then saved to various fastq files and used for mapping
        self.clusterId = clusterId # the cluster id that the read pair belong to after clustering inititally None

        # graphical representation, not really used anymore, still kept here if needed in the future
        self.outstring = str(self.id)+''.join([' ' for i in range(10-len(str(self.id)))]),
        self.__str__ = self.outstring

        # mapping info from the bamfile look at pysam and sam/bam file defenition to get info about each field/variable
        self.bamFilePos = bamFilePos
        self.mappingFlagR1 = SamFlag(mappingFlagR1)
        self.refNameR1 = refNameR1
        self.refPosR1 = refPosR1
        self.mapQR1 = mapQR1
        self.cigarR1 = cigarR1
        self.mappingFlagR2 = SamFlag(mappingFlagR2)
        self.refNameR2 = refNameR2
        self.refPosR2 = refPosR2
        self.mapQR2 = mapQR2
        self.cigarR2 = cigarR2
        self.insertSize = insertSize
        
        # connection to analysisfolder object
        self.analysisfolder = analysisfolder

    @property
    def databaseTuple(self, ):
        """ returning a tuple that is formated to be added to sql database"""
        # data base has following info:
        #       (id,          header,  sequence1, sequence2, quality1,quality2,handleCoordinates,clusterId,annotation,fromFastq)

        # Dumping the quality and sequence values
        #return  (self.id,     self.r1Header,self.r1Seq,self.r2Seq,self.r1Qual,self.r2Qual,   str(self.handleCoordinates),self.dbs,     str(self.annotations),self.fileOrigin)
        #return  (self.id,     self.r1Header,None,None,None,None,   str(self.handleCoordinates),self.dbs,     str(self.annotations),self.fileOrigin)
        return (self.id, self.header, None,None,None,None,self.direction,str(self.h1),str(self.h2),str(self.h3),self.construct,self.dbsmatch,self.dbsSeq,self.dbsQual,self.mappingFlagR1.flag,self.refNameR1,self.refPosR1,self.mapQR1,self.cigarR1,self.mappingFlagR2.flag,self.refNameR2,self.refPosR2,self.mapQR2,self.cigarR2,self.insertSize,self.clusterId,str(self.annotations),self.fileOrigin, self.r1PositionInFile,self.r2PositionInFile,self.bamFilePos, self.individual_id)

    def fixInsert(self,):
        """ This functions gets the insert sequence depending on what handles where found earlier"""

        # the insert variable has the following layout
                      #r1s  r1q  r2s  r2q
        self.insert = [None,None,None,None]
        # Where
        #r1s is read one sequence
        #r1q is read one quality
        #r2s is read two sequence
        #r2q is read two quality
        
        if self.direction == '1 -> 2':
            if self.h2:
                self.insert[0] = self.r1Seq[self.h2[1]:]
                self.insert[2] = self.r1Qual[self.h2[1]:]
                if self.readIntoh3Coordinates != None:
                    self.insert[0] = self.r1Seq[self.h2[1]:self.readIntoh3Coordinates[0]]
                    self.insert[2] = self.r1Qual[self.h2[1]:self.readIntoh3Coordinates[0]]
            if self.h3 and self.h3 != True:
                self.insert[1] = self.r2Seq[self.h3[1]:]
                self.insert[3] = self.r2Qual[self.h3[1]:]
            if self.individual_id and self.fwd_primer:
                self.insert[0] = self.r1Seq[self.fwd_primer[0]:]
                self.insert[2] = self.r1Qual[self.fwd_primer[0]:]
        
        elif self.direction == '2 -> 1':
            if self.h2:
                self.insert[0] = self.r2Seq[self.h2[1]:]
                self.insert[2] = self.r2Qual[self.h2[1]:]
                if self.readIntoh3Coordinates != None:
                    self.insert[0] = self.r2Seq[self.h2[1]:self.readIntoh3Coordinates[0]]
                    self.insert[2] = self.r2Qual[self.h2[1]:self.readIntoh3Coordinates[0]]
            if self.h3 and self.h3 != True:
                self.insert[1] = self.r1Seq[self.h3[1]:]
                self.insert[3] = self.r1Qual[self.h3[1]:]
        
        if self.insert == [None,None,None,None]: self.insert = None
        return 0

    def matchdbs(self,):
        """ this function matches the DBS sequence against the expected pattern """
        
        if self.analysisfolder.settings.type == 'HLA':   from sequences import HLA_DBS as DBS
        elif self.analysisfolder.settings.type == 'WFA': from sequences import WFA_DBS as DBS

        if self.dbsPrimaryCoordinates:
            self.dbs = self.dbsPrimaryCoordinates[0][self.dbsPrimaryCoordinates[1]:self.dbsPrimaryCoordinates[2]]
            self.dbsQual = self.dbsPrimaryCoordinates[3][self.dbsPrimaryCoordinates[1]:self.dbsPrimaryCoordinates[2]]

        if self.dbs:

            dbsSeq=self.dbs.replace('.','')
            dbsSeq = dbsSeq.split('  ')
            if len(dbsSeq)!=1:dbsSeq = ''
            else: dbsSeq = dbsSeq[0]

            dbsRegex = UIPAC2REGEXP(DBS)
            import re
            
            if dbsSeq:
                match = re.match('^'+dbsRegex+'$',self.dbs)
                if match:
                    self.dbsmatch = True
                    self.dbsSeq = self.dbs
                    #print 'woohooo!',dbsSeq
                else:
                    self.dbsmatch = False
                    self.dbsSeq = False
                    #print 'ohhhnooooo!',dbsSeq
            else:pass#print 'BADSEQUENCE!',dbsSeq
            
    def matchSequence(self, readsequence, matchsequence, maxDistance, matchfunk=misc.hamming_distance, startOfRead=False,breakAtFirstMatch=False):
        """" function for finding sequenc motifs in the read sequence returns a list with [startcoordinate, endcoordinate, number of missmatches]"""
        
        #
        # Imports
        #
        import re
        import misc
        # matchfunk = hamming_distance        
        try:
            from hamming_cython_solution import hamming_loop
            matchfunk = hamming_loop
            import hamming_cython_solution
        except ImportError: pass
        
        startPosition = None
        endPosition   = None
        missmatches   = None
        
        #matchfunk=levenshtein
        
        #
        # use regular expression to try and find a perfect match
        #
        perfect_match = re.search(matchsequence, readsequence)
        if perfect_match:
            startPosition = perfect_match.start()
            endPosition = perfect_match.end()
            missmatches = 0
        
        #
        # if perfect match is not found use hamming distance to try and find a "near perfect" match
        #
        elif int(maxDistance):
            mindist = [10000,-1]
            goto = len(readsequence)
            if startOfRead: goto = 10
            for i in range(goto):
                
                if i+len(matchsequence) <= len(readsequence): dist = matchfunk(matchsequence,readsequence[i:i+len(matchsequence)])
                else: dist = 10001
                # if breakAtFirstMatch and (matchfunk == misc.hamming_distance or matchfunk == hamming_cython_solution.hamming_loop):
                #     if dist >= maxDistance:
                #         return [i,i+len(matchsequence),dist]
                
                if dist < mindist[0]: mindist =[dist,i]
            
            if mindist[0] < int(maxDistance)+1:
                startPosition = mindist[1]
                endPosition = mindist[1]+len(matchsequence)
                missmatches = mindist[0]
            else:
                startPosition = None
                endPosition = None
                missmatches = None
        
        return [startPosition,endPosition,missmatches]

    def makeColoredOut(self, terminalcolor=True, htmlcolor=False):
        """ creates the string with colors for each of the reads """
        
        #
        # THIS function needs commenting and revision!!! //EB
        #
        import misc
        if terminalcolor:
            color = misc.TerminalColors()
            newline = '\n'
        elif htmlcolor:
            color = misc.HtmlColors()
            newline = '<br>'
        
        outputSeq = ''
        if True:
            if self.direction == '1 -> 2' or self.direction == '? -> ?' or self.direction == None: quals = [self.r1Qual,self.r2Qual[::-1]]
            if self.direction == '2 -> 1': quals = [self.r2Qual,self.r1Qual[::-1]]
            outputSeq += 'QualBar'
            for i in quals[0]:
                qNum = ord(i)-33
                if qNum >= 28:
                    outputSeq += color.GreenIntense
                elif qNum >= 20:
                    outputSeq += color.YellowIntense
                elif qNum >= 0:
                    outputSeq += color.RedIntense
                outputSeq += '_' + color.Color_Off
            outputSeq += ' '
            for i in quals[1]:
                qNum = ord(i)-33
                if qNum >= 28:
                    outputSeq += color.GreenIntense
                elif qNum >= 20:
                    outputSeq += color.YellowIntense
                elif qNum >= 0:
                    outputSeq += color.RedIntense
                outputSeq += '_' + color.Color_Off
        outputSeq += newline
        
        if   self.direction == '1 -> 2':outputSeq += self.direction+' '
        elif self.direction == '2 -> 1':outputSeq += self.direction+' '
        else:
            #outputSeq = '     ? -> ?'+''.join([' ' for i in range(10-len('? -> ?'))]) +' '+ self.r1Seq+' '+'.'.join(['' for i in range(160-len(self.r2Seq)-len(self.r1Seq))])+' '+revcomp(self.r2Seq)
            outputSeq += '? -> ? '+ self.r1Seq+' '+revcomp(self.r2Seq)
            #print outputSeq
        
        if self.direction:
            
            lastWritten = 0

            if self.direction == '1 -> 2':
                
                if self.h1:
                    outputSeq += self.r1Seq[lastWritten:self.h1[0]]+color.BlueIntense+self.r1Seq[self.h1[0]:self.h1[1]]+color.Color_Off
                    lastWritten = self.h1[1]
                
                if self.h2:
                    outputSeq += self.r1Seq[lastWritten:self.h2[0]]+color.PurpleIntense+self.r1Seq[self.h2[0]:self.h2[1]]+color.Color_Off
                    lastWritten = self.h2[1]
                    
                outputSeq += self.r1Seq[lastWritten:]
                
                outputSeq += ' '
                lastWritten = 0
                if self.h3:
                    if  self.h3 == True and self.readIntoh3 == True: outputSeq += '###### SOMETHING HERE #####'
                    else:
                        outputSeq += revcomp(self.r2Seq)[lastWritten:len(self.r2Seq)-self.h3[1]]+color.YellowIntense+revcomp(self.r2Seq)[len(self.r2Seq)-self.h3[1]:len(self.r2Seq)-self.h3[0]]+color.Color_Off
                        lastWritten = len(self.r2Seq)-self.h3[0]
                    if self.h1_in_both_ends and self.readIntoh3 == None:
                        import sys
                        outputSeq += revcomp(self.r2Seq)[lastWritten:]
                        print ' ########  wowowow! funky buissyness!',outputSeq,str(self.h1in2ndReadCoordinates),'  ##################'
                        sys.exit()
                    
                if self.h1_in_both_ends:
                    
                    if self.annotations['h2_r2_coordinates'][0]:
                        outputSeq += revcomp(self.r2Seq)[lastWritten:len(self.r2Seq)-self.annotations['h2_r2_coordinates'][1]]+color.PurpleIntense+revcomp(self.r2Seq)[len(self.r2Seq)-self.annotations['h2_r2_coordinates'][1]:len(self.r2Seq)-self.annotations['h2_r2_coordinates'][0]]+color.Color_Off
                        lastWritten = len(self.r2Seq)-self.annotations['h2_r2_coordinates'][0]
                    
                    if self.h1in2ndReadCoordinates[0] == 0 or (self.h1in2ndReadCoordinates[0] != None and self.h1in2ndReadCoordinates[0] != False):
                        outputSeq += revcomp(self.r2Seq)[lastWritten:len(self.r2Seq)-self.h1in2ndReadCoordinates[1]]+color.BlueIntense+revcomp(self.r2Seq)[len(self.r2Seq)-self.h1in2ndReadCoordinates[1]:len(self.r2Seq)-self.h1in2ndReadCoordinates[0]]+color.Color_Off
                        lastWritten = len(self.r2Seq)-self.h1in2ndReadCoordinates[0]
                outputSeq += revcomp(self.r2Seq)[lastWritten:]
                    
            elif self.direction == '2 -> 1':
                
                if self.h1:
                    #outputSeq += 'HERE --'+self.r2Seq+' --\n'
                    outputSeq += self.r2Seq[lastWritten:self.h1[0]]+color.BlueIntense+self.r2Seq[self.h1[0]:self.h1[1]]+color.Color_Off
                    lastWritten = self.h1[1]
                
                if self.h2:
                    outputSeq += self.r2Seq[lastWritten:self.h2[0]]+color.PurpleIntense+self.r2Seq[self.h2[0]:self.h2[1]]+color.Color_Off
                    lastWritten = self.h2[1]
                    
                if self.annotations and self.readIntoh3Coordinates != None:
                    outputSeq += self.r2Seq[lastWritten:self.readIntoh3Coordinates[0]]+color.YellowIntense+self.r2Seq[self.readIntoh3Coordinates[0]:self.readIntoh3Coordinates[1]]+color.Color_Off
                    lastWritten = self.readIntoh3Coordinates[1]
                    #self.readIntoh3Coordinates = [startPosition,endPosition,missmatches]
                
                if self.readIntoh3Coordinates == None:
                    outputSeq += self.r2Seq[lastWritten:]
                
                outputSeq += ' '
                lastWritten = 0
                if self.h3 and self.h3 != True:
                    outputSeq += revcomp(self.r1Seq)[lastWritten:len(self.r1Seq)-self.h3[1]]+color.YellowIntense+revcomp(self.r1Seq)[len(self.r1Seq)-self.h3[1]:len(self.r1Seq)-self.h3[0]]+color.Color_Off
                    lastWritten = len(self.r1Seq)-self.h3[0]
                    #if self.h1_in_both_ends:
                    #    import sys
                    #    print 'wowowow!'
                    #    sys.exit()
                    
                #if self.h1_in_both_ends:
                #    
                #    if self.annotations['h2_r2_coordinates'][0]:
                #        outputSeq += revcomp(self.r2Seq)[lastWritten:len(self.r2Seq)-self.annotations['h2_r2_coordinates'][1]]+color.PurpleIntense+revcomp(self.r2Seq)[len(self.r2Seq)-self.annotations['h2_r2_coordinates'][1]:len(self.r2Seq)-self.annotations['h2_r2_coordinates'][0]]+color.Color_Off
                #        lastWritten = len(self.r2Seq)-self.annotations['h2_r2_coordinates'][0]
                #    
                #    if self.h1in2ndReadCoordinates[0] == 0 or (self.h1in2ndReadCoordinates[0] != None and self.h1in2ndReadCoordinates[0] != False):
                #        outputSeq += revcomp(self.r2Seq)[lastWritten:len(self.r2Seq)-self.h1in2ndReadCoordinates[1]]+color.BlueIntense+revcomp(self.r2Seq)[len(self.r2Seq)-self.h1in2ndReadCoordinates[1]:len(self.r2Seq)-self.h1in2ndReadCoordinates[0]]+color.Color_Off
                #        lastWritten = len(self.r2Seq)-self.h1in2ndReadCoordinates[0]
                outputSeq += revcomp(self.r1Seq)[lastWritten:]
                
                # 2->1 END
            
            #######################################################################################
            # STRANGE TO RUN THESE FUNCTIONS HERE SHOULD MAYBE BE DONE AT SOME OTHER POINT! //EB  #
            #                                                                                     #
            self.fixInsert()                                                                      #
            #if self.insert: outputSeq+= '--'+self.insert+'--'                                    #
                                                                                                  #
            if self.h3 and self.h1 and self.h2:                                                   #
                outputSeq += ' LOOK HERE!'                                                        #
                self.matchdbs()                                                                   #
                if self.dbsmatch: outputSeq += ' Match!'                                          #
                else: outputSeq += ' No match...'                                                 #
            #outputSeq += '\n'                                                                    #
            #######################################################################################
            #print self.construct
            
            #if self.dbsPrimaryCoordinates:
            #    print 'PRIMARYDBS',
            #    print self.dbsPrimaryCoordinates[0][self.dbsPrimaryCoordinates[1]:self.dbsPrimaryCoordinates[2]]
            #if 'secondary_dbs_coordinates' in self.annotations:
            #    print 'SCNDARYDBS',
            #    print self.annotations['secondary_dbs_coordinates'][0][self.annotations['secondary_dbs_coordinates'][1]:self.annotations['secondary_dbs_coordinates'][2]]

        #if self.overlap: print 'OLP'+outputSeq
        #else:print ''+outputSeq
        self.outputSeq = outputSeq

    def identifyDirection(self,):
        """ function that uses the matchSequence function to find the handles defined in sequences
        """
        
        if self.analysisfolder.settings.type == 'HLA':
            from sequences import HLA_H1 as H1
            from sequences import HLA_H2 as H2
            from sequences import HLA_H3 as H3
            from sequences import HLA_DBS as DBS
        elif self.analysisfolder.settings.type == 'WFA':
            from sequences import WFA_H1 as H1
            from sequences import WFA_H2 as H2
            from sequences import WFA_H3 as H3
            from sequences import WFA_DBS as DBS
        from sequences import IND_HANDLE_1
        from sequences import IND_HANDLE_2

        # set direction to None (ie. not identified)
        self.direction = None
        
        missmatchesAllowed = self.analysisfolder.settings.maxHandleMissMatches

        import re
        perfect_read_regex = re.compile('^'+H1+UIPAC2REGEXP(DBS)+revcomp(H2)+'[AGTCN]+'+revcomp(H3)+'$')
        if perfect_read_regex.match(self.r1Seq+revcomp(self.r2Seq)):
            self.direction  = '1 -> 2'
            self.h1 = [0,len(H1),0]
            self.h2 = [len(H1)+len(DBS),len(H1)+len(DBS)+len(H2),0]
            self.h3 = [0,len(H3),0]
            self.dbsPrimaryCoordinates = [self.r1Seq,self.h1[1],self.h2[0],self.r1Qual]
            self.construct = 'constructOK'
            
            self.h1_in_both_ends = None
            self.h3_in_both_ends = None
            self.h1in2ndReadCoordinates = None
            self.h3in2ndReadCoordinates = None
            self.readIntoh3 = None
            self.readIntoh3Coordinates = None
            
            if self.analysisfolder.settings.IndexReferenceTsv:
                self.individual_id_primer = self.matchSequence(self.r1Seq,IND_HANDLE_1,missmatchesAllowed,breakAtFirstMatch=True)
                self.fwd_primer           = self.matchSequence(self.r1Seq,IND_HANDLE_2,missmatchesAllowed,breakAtFirstMatch=True)
                if self.individual_id_primer[0] and self.fwd_primer[0]: self.individual_id = self.r1Seq[self.individual_id_primer[1]:self.fwd_primer[0]]
                else: self.individual_id = None
            else:
                self.individual_id_primer = None
                self.fwd_primer           = None
                self.individual_id = None
            return ''


        # look for h1 in read 1
        self.h1 = self.matchSequence(self.r1Seq,H1,missmatchesAllowed,startOfRead=True,breakAtFirstMatch=True)
        startPosition,endPosition,missmatches = self.h1
        if startPosition!=None and startPosition <= 2: self.direction = '1 -> 2'
        if startPosition==None: self.h1 = None
        
        # look for H3 in read one
        if not self.direction:
            self.h3 = self.matchSequence(self.r1Seq,H3,missmatchesAllowed,startOfRead=True,breakAtFirstMatch=True)
            startPosition,endPosition,missmatches = self.h3
            if startPosition!=None and startPosition <= 2: self.direction = '2 -> 1'
            if startPosition==None: self.h3 = None

        # look for H3 in read two
        self.h3_in_both_ends = None
        startPosition,endPosition,missmatches = self.matchSequence(self.r2Seq,H3,missmatchesAllowed,startOfRead=True,breakAtFirstMatch=True)
        if startPosition!=None and startPosition <= 2:
            if self.h3:
                self.h3_in_both_ends = True
                self.h3in2ndReadCoordinates = [startPosition,endPosition,missmatches]
            else:
                self.h3_in_both_ends = False
                self.direction = '1 -> 2'
                self.h3 = [startPosition,endPosition,missmatches]

        # look for H1 in read 2
        self.h1_in_both_ends = None
        if not (self.h3 and self.direction == '1 -> 2'):
            startPosition,endPosition,missmatches = self.matchSequence(self.r2Seq,H1,missmatchesAllowed,startOfRead=True,breakAtFirstMatch=True)
            if startPosition!=None and startPosition <= 2:
                if self.h1:
                    self.h1_in_both_ends = True
                    self.h1in2ndReadCoordinates = [startPosition,endPosition,missmatches]
                else:
                    self.direction = '2 -> 1'
                    self.h1 = [startPosition,endPosition,missmatches]
                    self.h1in2ndReadCoordinates = self.h1
                
        # look for readinto h3
        checkSeq = None
        self.readIntoh3 = None
        self.readIntoh3Coordinates = None
        if self.direction == '1 -> 2': checkSeq = self.r1Seq
        elif self.direction == '2 -> 1': checkSeq = self.r2Seq
        if checkSeq:
            startPosition,endPosition,missmatches = self.matchSequence(checkSeq,revcomp(H3),missmatchesAllowed,breakAtFirstMatch=True)
            if startPosition!=None:
                self.readIntoh3 = True
                self.readIntoh3Coordinates = [startPosition,endPosition,missmatches]
                if not self.h3: self.h3 = True

        # look for individual index in read 1 //HA
        self.individual_id = None
        if self.direction and not self.h3_in_both_ends:
            
            # find the h2 handle and DBS sequence
            if self.direction == '1 -> 2':
                self.h2 = self.matchSequence(self.r1Seq,revcomp(H2),missmatchesAllowed,breakAtFirstMatch=True)
                if not self.h2[0]: self.h2 = None
                
                if self.h1 and self.h2:
                    self.dbsPrimaryCoordinates = [self.r1Seq,self.h1[1],self.h2[0],self.r1Qual]
                    
                    # look for individual id
                    self.individual_id_primer = self.matchSequence(self.r1Seq,IND_HANDLE_1,missmatchesAllowed,breakAtFirstMatch=True)
                    self.fwd_primer           = self.matchSequence(self.r1Seq,IND_HANDLE_2,missmatchesAllowed,breakAtFirstMatch=True)
                    if self.individual_id_primer[0] and self.fwd_primer[0]: self.individual_id = self.r1Seq[self.individual_id_primer[1]:self.fwd_primer[0]]
                    else: self.individual_id = None
                
                if self.h1_in_both_ends: # find secondary h2
                    self.annotations['h2_r2_coordinates'] = self.matchSequence(self.r2Seq,revcomp(H2),missmatchesAllowed,breakAtFirstMatch=True)
                    if self.h1in2ndReadCoordinates[0]==0 and self.annotations['h2_r2_coordinates'][0] or (self.h1in2ndReadCoordinates[0] and self.annotations['h2_r2_coordinates'][0]):
                        self.annotations['secondary_dbs_coordinates'] = [self.r2Seq,self.h1in2ndReadCoordinates[1],self.annotations['h2_r2_coordinates'][0]]

            elif self.direction == '2 -> 1':
                self.h2 = self.matchSequence(self.r2Seq,revcomp(H2),missmatchesAllowed,breakAtFirstMatch=True)
                if not self.h2[0]: self.h2 = None

                if self.h1 and self.h2:
                    self.dbsPrimaryCoordinates = [self.r2Seq,self.h1[1],self.h2[0],self.r2Qual]

            else:pass
    
        #classify construct type
        if self.h1 and self.h2 and self.h3:
            self.construct = 'constructOK'
        else: 
            self.construct ='missing:'
            if not self.h1: self.construct += ' h1 '
            if not self.h3: self.construct += ' h3 '
            if not self.h2: self.construct += ' h2'
            if self.h1 and self.h3 and not self.h2 and self.direction == '1 -> 2' and len(self.r1Seq)<60: self.construct = ' h2-SemiOK'

    def isIlluminaAdapter(self, ):
        """ function that identifies illumina adapter content within the reads and annotates the reads accordingly"""

        import math

        for i in [15]:#range(15):
            handleStartPosition,handleEndPosition,handleMissMatches = self.matchSequence(self.r1Seq, 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC'[:35-i], int(math.ceil(float(35-i)*0.1)))
            if handleStartPosition:
                self.annotations['Read1IsIlluminaAdapter'] = str(handleMissMatches)+':'+ str(handleStartPosition)
                break

        for i in [15]:#range(15):
            handleStartPosition,handleEndPosition,handleMissMatches = self.matchSequence(self.r2Seq, 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'[:34-i], int(math.ceil(float(34-i)*0.1)))
            if handleStartPosition:
                self.annotations['Read2IsIlluminaAdapter'] = str(handleMissMatches)+':'+ str(handleStartPosition)
                break

    def getFromFiles(self,):
        
        """ function for retreaving data from files on disc not the database
        currently only the fastqs maybe bam aswell later on"""
        
        import metadata
        
        tmp = self.analysisfolder.database.c.execute('SELECT filePairId,fastq1,fastq2,readCount,addedToReadsTable,minReadLength FROM fastqs WHERE filePairId == '+str(self.fileOrigin)).fetchone()
        filePairId,fastq1,fastq2,readCount,addedToReadsTable,minReadLength = tmp
        
        #
        # get r1 from fastq
        #
        if fastq1.split('.')[-1] in ['gz','gzip']: #
            import gzip                            # open thr fastq file
            fastq1 = gzip.open(fastq1)             # 
        else: fastq1 = open(fastq1)                #
        fastq1.seek(self.r1PositionInFile) # go to the read position
        tmp = fastq1.readline().rstrip().split(' ')[0] # get the header
        assert self.header == tmp, 'ERROR: '+str(self.header)+' != '+str(tmp) # assert that it is the correct read
        self.r1Seq = fastq1.readline().rstrip() # get the sequence
        fastq1.readline().rstrip() # trash the "+"
        self.r1Qual = fastq1.readline().rstrip() # get the quality

        #
        # get r2 from fastq
        #
        if fastq2.split('.')[-1] in ['gz','gzip']: #
            import gzip                            # open thr fastq file
            fastq2 = gzip.open(fastq2)             # 
        else: fastq2 = open(fastq2)                #
        fastq2.seek(self.r2PositionInFile) # go to the read position
        tmp = fastq2.readline().rstrip().split(' ')[0] # get the header
        assert self.header == tmp, 'ERROR: '+str(self.header)+' != '+str(tmp) # assert that it is the correct read
        self.r2Seq = fastq2.readline().rstrip() # get the sequence
        fastq2.readline().rstrip() # trash the "+"
        self.r2Qual = fastq2.readline().rstrip() # get the quality

class BarcodeClusterer(object):
    
    def __init__(self, analysisfolder):
        
        self.analysisfolder = analysisfolder
        self.logfile = self.analysisfolder.logfile

    def generateBarcodeFastq(self, ):
        """ function that loads the barcode sequnces found from the database and creates a fasta file with these sequence formated and rady for running the clustering
        """

        #
        # imports
        #
        import operator
        import misc
        if self.analysisfolder.settings.type == 'HLA':  from sequences import HLA_DBS as DBS
        elif self.analysisfolder.settings.type == 'WFA':from sequences import WFA_DBS as DBS

        if self.logfile: self.logfile.write('Generating barcode fastq ...\n')

        #
        # setting initial values
        #
        uniqBarcodeSequences = {}
        temporaryDict = {}
        barcodeCounter = 0
        totalReadPairCounter = 0
        qualities = {}
        readPairHasBarcodeCounter = 0
        base_frequencies = [{'A':0,'T':0,'G':0,'C':0} for i in xrange(len(DBS))]

        if self.logfile: self.logfile.write('Loading read pairs ...\n')
        progress = misc.Progress(self.analysisfolder.results.totalReadCount, logfile=self.logfile, unit='reads-loaded-from-db', mem=True)
        with progress:
            self.analysisfolder.database.getConnection()
            for pairid,barcodeSequence,qual in self.analysisfolder.database.c.execute('SELECT id, dbsSeq, dbsQual FROM reads'):
                pairid = int(pairid)
                if barcodeSequence:
                    readPairHasBarcodeCounter += 1
                    qualities[pairid] = qual
                    try:            uniqBarcodeSequences[barcodeSequence].append(pairid)
                    except KeyError:uniqBarcodeSequences[barcodeSequence] = [pairid]
                    for i in xrange(len(barcodeSequence)): base_frequencies[i][barcodeSequence[i]] += 1
                progress.update()
        if self.logfile: self.logfile.write('Done.\n')
        self.analysisfolder.results.setResult('uniqueBarcodeSequences',len(uniqBarcodeSequences))
        if self.logfile: self.logfile.write(str(self.analysisfolder.results.uniqueBarcodeSequences)+' uniq barcode sequences found within the read pair population.\n')
        
        #
        # print base frequenzies for raw barcodes to file
        #
        with open(self.analysisfolder.dataPath+'/rawBarcodeBaseFreq.dict.txt','w') as outfile: outfile.write(str(base_frequencies))

        self.id2seq = {}
        if self.logfile: self.logfile.write('Sorting the barcodes by number of reads/sequence.\n')
        if self.logfile: self.logfile.write('Building the sorting dictionary ...\n')
        for barcode, idList in uniqBarcodeSequences.iteritems():
            try:		temporaryDict[len(idList)].append(barcode)
            except KeyError:temporaryDict[len(idList)] = [barcode]
            for idnumber in idList: self.id2seq[idnumber] = barcode

        if self.logfile: self.logfile.write('Creating output ... \n')
        barcodeFastqFile = open(self.analysisfolder.dbsfastq,'w')
        progress = misc.Progress(readPairHasBarcodeCounter, logfile=self.logfile, unit='reads-to-fastq', mem=True)
        with progress:
            for count, barcodes in sorted(temporaryDict.iteritems(), key=operator.itemgetter(0))[::-1]:
                for barcode in barcodes:
                    barcodeCounter += 1
                    readPairCounter = 0
                    for readPairId in uniqBarcodeSequences[barcode]:
                        readPairCounter += 1
                        totalReadPairCounter += 1
                        barcodeFastqFile.write('@'+str(readPairId)+' bc='+str(barcodeCounter)+' rp='+str(readPairCounter)+' bctrp='+str(count)+'\n'+barcode+'\n+\n'+qualities[readPairId]+'\n')
                        progress.update()
        barcodeFastqFile.close()	
        
        return readPairHasBarcodeCounter

    def runBarcodeClusteringPrograms(self, ):
        """ runs the actual clustering programs as subprocesses
        """

        #
        # imports
        #
        import subprocess
        import time

        clusteringProgramsLogfile = open(self.analysisfolder.logpath+'/'+time.strftime("%y%m%d-%H:%M:%S",time.localtime())+'_cdHitBarcodeClustering.log.txt','w')

        # cluster raw barcodes
        command = ['cd-hit-454',
                  '-i',self.analysisfolder.dataPath+'/rawBarcodeSequencesSortedByAbundance.fq',
                  '-o',self.analysisfolder.dataPath+'/clusteredBarcodeSequences',
                  '-g','1',      # mode
                  '-n','3',      # wrodsize
                  '-M','0',      # memory limit
                  '-T',str(self.analysisfolder.settings.parallelProcesses),      # threads
                  '-gap','-100', # disallow gaps
                  '-c',str(1.000-float(self.analysisfolder.settings.barcodeMissmatch)/float(self.analysisfolder.settings.barcodeLength)) # identity cutoff
                  ]
        if self.logfile: self.logfile.write('Starting command: '+' '.join(command)+'\n')
        cdhit = subprocess.Popen(command,stdout=clusteringProgramsLogfile,stderr=subprocess.PIPE )
        errdata = cdhit.communicate()
        if cdhit.returncode != 0:
            print 'cmd: '+' '.join( command )
            print 'cd-hit view Error code', cdhit.returncode, errdata
            sys.exit()

        # Build consensus sequences for read pair clusters
        # command = ['cdhit-cluster-consensus',
        #     self.analysisfolder.dataPath+'/clusteredBarcodeSequences.clstr',
        #     self.analysisfolder.dataPath+'/rawBarcodeSequencesSortedByAbundance.fq',
        #     self.analysisfolder.dataPath+'/clusteredBarcodeSequences.consensus',
        #     self.analysisfolder.dataPath+'/clusteredBarcodeSequences.aligned'
        #     ]
        # if self.logfile: self.logfile.write('Starting command: '+' '.join(command)+'\n')
        # ccc = subprocess.Popen(command,stdout=clusteringProgramsLogfile,stderr=subprocess.PIPE )
        # errdata = ccc.communicate()
        # if ccc.returncode != 0:
        #     print 'cmd: '+' '.join( command )
        #     print 'cdhit-cluster-consensus view Error code', ccc.returncode, errdata
        #     sys.exit()
        clusteringProgramsLogfile.close()

        return 0

    def parseBarcodeClusteringOutput(self, readPairsHasBarcode):
        """ parse the output from the clustering programs to find what reads ids have beeen clustered together
        """

        import misc
        
        #
        # inititate variables
        #
        totalClusterCount = 0
        barcodeClusters = {}
        singletonClusters = {}
        nonSingletonClusters = {}

        #
        # open file connections
        #
        # consensusFile = open(self.analysisfolder.dataPath+'/clusteredBarcodeSequences.consensus.fastq')
        clstrFile = open(self.analysisfolder.dataPath+'/clusteredBarcodeSequences.clstr')

        #
        # load cluster ids and consensus sequences
        #
        if self.logfile: self.logfile.write('\nLoading barcode clusters and a barcode consesnsus sequences for each cluster ...\n')
        # while True:
        #     header = consensusFile.readline().rstrip()
        #     barcodeSequence = consensusFile.readline().rstrip()
        #     junk = consensusFile.readline().rstrip()
        #     barcodeQuality = consensusFile.readline().rstrip()
        #     if header == '': break
        #     totalClusterCount += 1
        #     header = header.split('_cluster_')
        #     clusterId = int(header[1].split(' ')[0])
        #     if header[0][:2] == '@s':
        #         singletonClusters[clusterId] = {'clusterReadCount':1,'readPairs':[],'identities':[],'clusterBarcodeSequence':barcodeSequence,'clusterBarcodeQuality':barcodeQuality}
        #         barcodeClusters[clusterId] = singletonClusters[clusterId]
        #     elif header[0][:2] == '@c':
        #         nonSingletonClusters[clusterId] = {'clusterReadCount':int(header[1].split(' ')[2]),'readPairs':[],'identities':[],'clusterBarcodeSequence':barcodeSequence,'clusterBarcodeQuality':barcodeQuality}
        #         barcodeClusters[clusterId] = nonSingletonClusters[clusterId]
        #     else: raise ValueError
        # self.analysisfolder.results.setResult('barcodeClusterCount',totalClusterCount)
        # self.analysisfolder.results.setResult('singeltonBarcodeClusters',len(singletonClusters))
        if self.logfile: self.logfile.write('A total of '+str(totalClusterCount)+' clusters of barcode sequences were loaded into memory.\n')

        #
        # Load what readpairs are in each cluster
        #
        if self.logfile: self.logfile.write('\nLoading read pair to barcode cluster connections ...\n')
        progress = misc.Progress(readPairsHasBarcode, logfile=self.logfile, unit='reads-loaded', mem=True)
        # tmp_totalClusterCount = 0
        barcodeCluster = None
        with progress:
            for line in clstrFile:
                line = line.rstrip()
                if line[0] == '>':
                    if barcodeCluster:
                        # print '#',clusterId,barcodeCluster['clusterReadCount'],barcodeCluster['clusterBarcodeSequence'],(clusterId in nonSingletonClusters),(clusterId in singletonClusters),len(barcodeCluster['readPairs']),len(barcodeCluster['identities'])
                        # assert barcodeCluster['clusterReadCount'] == barcodeClusters[clusterId]['clusterReadCount'],'readcounts dont match'
                        # if barcodeCluster['clusterBarcodeSequence'] != barcodeClusters[clusterId]['clusterBarcodeSequence']:print'NNNNNNNNNNNNNNNNNNNN';print barcodeCluster['clusterBarcodeSequence'];print barcodeClusters[clusterId]['clusterBarcodeSequence']
                        barcodeClusters[clusterId] = barcodeCluster
                        if barcodeCluster['clusterReadCount'] >1: nonSingletonClusters[clusterId] = barcodeCluster
                        else: singletonClusters[clusterId] = barcodeCluster
                    # tmp_totalClusterCount += 1
                    clusterId = int(line.split(' ')[1])
                    clusterReadCount = 0
                    barcodeCluster = {'clusterReadCount':0,'readPairs':[],'identities':[],'clusterBarcodeSequence':None,'clusterBarcodeQuality':None}
                    continue
                elif line[0] == '0':
                    readId = line.split('>')[1].split('.')[0]
                    identity = 'seed'
                    assert line.split(' ')[-1] == '*', 'Error in file format of clstr file'
                    barcodeCluster['clusterBarcodeSequence'] = self.id2seq[int(readId)]
                else:
                    readId = line.split('>')[1].split('.')[0]
                    identity = float(line.split(' ')[-1].split('/')[-1].split('%')[0])
                # barcodeClusters[clusterId]['readPairs'].append(readId)
                # barcodeClusters[clusterId]['identities'].append(identity)
                # clusterReadCount += 1
                barcodeCluster['readPairs'].append(int(readId))
                barcodeCluster['identities'].append(identity)
                barcodeCluster['clusterReadCount'] += 1
                progress.update()
        totalClusterCount = len(barcodeClusters)
        self.analysisfolder.results.setResult('barcodeClusterCount',len(barcodeClusters))
        self.analysisfolder.results.setResult('singeltonBarcodeClusters',len(singletonClusters))
        if self.logfile: self.logfile.write('All read pair to barcode cluster connections loaded.\n')

        return barcodeClusters

    def addBarcodeClusterInfoToDatabase(self, barcodeClusters):
        """ adds the cluster info to the database both one entry for each cluster but also updates each readpair entry
        """

        import misc
        import metadata

        #
        # set initial values
        #
        tmpUpdateValues = {}
        updateValues = []
        updateChunks = []
        updateChunkSize = 10000
        addValues = [(None,0,'[]','[]','NoneCluster',None,None,None)]

        #
        # drop old data and create table for new data
        #
        if self.logfile: self.logfile.write('Create barcodeClusters table (and drop old one if needed) ...\n')
        self.analysisfolder.database.getConnection()
        self.analysisfolder.database.c.execute("DROP TABLE IF EXISTS barcodeClusters")
        self.analysisfolder.database.c.execute('''CREATE TABLE barcodeClusters (clusterId,clusterTotalReadCount,readPairsList,readBarcodeIdentitiesList,clusterBarcodeSequence,clusterBarcodeQuality,contigSequencesList,annotations,PRIMARY KEY (clusterId))''')
        if self.logfile: self.logfile.write('commiting changes to database.\n')
        self.analysisfolder.database.commitAndClose()

        #
        # Convert the dictionary to be able to add info to database
        #
        progress = misc.Progress(len(barcodeClusters), logfile=self.logfile, unit='clusters', mem=True)
        if self.logfile: self.logfile.write('Converting the data ... \n')
        for clusterId,data in barcodeClusters.iteritems():
            for readPairId in data['readPairs']: tmpUpdateValues[readPairId]=clusterId
            addValues.append( (clusterId,data['clusterReadCount'],str(data['readPairs']),str(data['identities']),data['clusterBarcodeSequence'],data['clusterBarcodeQuality'],None,None) )
            progress.update()
        for readPairId in sorted(tmpUpdateValues.keys()):
            updateValues.append( (int(tmpUpdateValues[readPairId]),int(readPairId)) )
            if len(updateValues) == updateChunkSize:
                updateChunks.append(updateValues)
                updateValues = []
        updateChunks.append(updateValues)

        #
        # Add the barcodeClusters
        #	
        if self.logfile: self.logfile.write('Adding cluster info to database ... \n')
        self.analysisfolder.database.getConnection()	
        self.analysisfolder.database.c.executemany('INSERT INTO barcodeClusters VALUES (?,?,?,?,?,?,?,?)', addValues)
        if self.logfile: self.logfile.write('commiting changes to database.\n')
        self.analysisfolder.database.commitAndClose()

        #
        # Update the reads table
        #
        if self.logfile: self.logfile.write('Updating read pair info in the database ... \n')
        progress = misc.Progress(len(tmpUpdateValues), logfile=self.logfile, unit='reads-updated', mem=True)
        with progress:
            for updateValues in updateChunks:
                self.analysisfolder.database.getConnection()	
                self.analysisfolder.database.c.executemany('UPDATE reads SET clusterId=? WHERE id=?', updateValues)
                self.analysisfolder.database.commitAndClose()
                for i in xrange(len(updateValues)): progress.update()
            
        return 0

    def clusterBarcodeSequences(self):
        """ runns all the other functions in the right order
        """

        #
        # imports
        #
        import subprocess

        #
        # generate a fastq file with barcode sequences
        #
        readPairsHasBarcode = self.generateBarcodeFastq()
        self.analysisfolder.results.setResult('readPairsHasBarcode',readPairsHasBarcode)

        #
        # Run clustering programs
        #
        self.runBarcodeClusteringPrograms()

        #
        # Parse the output
        #
        barcodeClusters = self.parseBarcodeClusteringOutput(readPairsHasBarcode)

        #
        # compress files
        #
        a = [
              self.analysisfolder.dataPath+'/clusteredBarcodeSequences',
              self.analysisfolder.dataPath+'/clusteredBarcodeSequences.clstr',
              self.analysisfolder.dataPath+'/rawBarcodeSequencesSortedByAbundance.fq',
              #self.analysisfolder.dataPath+'/clusteredBarcodeSequences.consensus.fastq',
              #self.analysisfolder.dataPath+'/clusteredBarcodeSequences.aligned',
              ]
        processes = [] 
        if self.logfile: temp = self.logfile
        else: temp = sys.stdout
        for fileName in a:
            if self.logfile: self.logfile.write('Starting process:'+' gzip -v9 '+fileName+'\n')
            p=subprocess.Popen(['gzip','-f','-v9',fileName],stdout=temp)
            processes.append(p)

        #
        # save clustering info to database
        #
        self.addBarcodeClusterInfoToDatabase(barcodeClusters)

        #
        # Save results
        #
        self.analysisfolder.results.saveToDb()

        #
        # wait for file compression to finish
        #
        if self.logfile: self.logfile.write('Waiting for the compression of clustering files to finish.\n')
        for p in processes: p.wait()

        return 0

    def getBarcodeClusterIds(self, shuffle=True,byMixedClusterReadCount=True):
        """ function for fetching barcode cluster info from the database
        NOTE: this function should maybe not be under this object but rather be moved to the database object in the future(?)
        """

        import random

        self.analysisfolder.database.getConnection()
        tmp = list(self.analysisfolder.database.c.execute('SELECT clusterId,clusterTotalReadCount FROM barcodeClusters').fetchall())
        clusterIds = []
        readCountbyID = {}
        for clusterId,clusterTotalReadCount in tmp:
            clusterIds.append(clusterId)
            readCountbyID[clusterId] = clusterTotalReadCount
        if shuffle: random.shuffle(clusterIds)
        self.analysisfolder.database.commitAndClose()

        if byMixedClusterReadCount:
            
            id2ReadCountDist = {}
            yielded = {}
            normal = []
            large = []
            huge = []
            humongous = []
            outofthescale = []
            
            self.analysisfolder.logfile.write('Sorting cluster ids to groups of varying read pair counts ...\n')
            for clusterId in clusterIds:
                if clusterId == None: continue
                clusterId = int(clusterId)
                cluster = BarcodeCluster(clusterId,self.analysisfolder)
                #cluster.loadClusterInfo()
                cluster.readPairCount = readCountbyID[cluster.id]
                id2ReadCountDist[cluster.id] = cluster.readPairCount
                yielded[cluster.id] = False
                if   cluster.readPairCount <  1000 and cluster.readPairCount >= 0: normal.append(cluster.id)
                elif cluster.readPairCount <  5000 and cluster.readPairCount >= 1000: large.append(cluster.id)
                elif cluster.readPairCount < 35000 and cluster.readPairCount >= 5000: huge.append(cluster.id)
                elif cluster.readPairCount <500000 and cluster.readPairCount >= 35000: humongous.append(cluster.id)
                else: outofthescale.append(cluster.id)
            self.analysisfolder.logfile.write('Done.\n')
            
            tmpCounter0 = 0
            yieldNow = None
            while False in yielded.values():
                if outofthescale and tmpCounter0 <= 0:
                    yieldNow = outofthescale[0]
                    outofthescale = outofthescale[1:]
                    yielded[yieldNow] = True
                    tmpCounter0 += 1
                    yield yieldNow
                elif humongous and tmpCounter0 <= 0:
                    yieldNow = humongous[0]
                    humongous = humongous[1:]
                    yielded[yieldNow] = True
                    tmpCounter0 += 1
                    yield yieldNow
                elif huge and tmpCounter0 <= 0:
                    yieldNow = huge[0]
                    huge = huge[1:]
                    yielded[yieldNow] = True
                    tmpCounter0 += 1
                    yield yieldNow
                elif large and tmpCounter0 <= 1:
                    yieldNow = large[0]
                    large = large[1:]
                    yielded[yieldNow] = True
                    tmpCounter0 += 1
                    yield yieldNow
                elif normal:
                    yieldNow = normal[0]
                    normal = normal[1:]
                    yielded[yieldNow] = True
                    tmpCounter0 += 1
                    yield yieldNow
                #SEAseqPipeLine.logfile.write( str(tmpCounter0)+'\t')
                #SEAseqPipeLine.logfile.write( str(yieldNow)+'\t')
                #SEAseqPipeLine.logfile.write( str(id2ReadCountDist[yieldNow])+'.\n')
                if tmpCounter0 == 6: tmpCounter0 = 0
                #if yielded.values().count(True) >= 100: break
        else:
            for clusterId in clusterIds:
                if clusterId[0] == None: continue
                try: yield int(clusterId[0])
                except TypeError: yield clusterId[0]

class BarcodeCluster(object,):
    """ object that represent a cluster of ReadPairs that all have the same barcode sequence
    """
    
    def __init__(self, clusterId,analysisfolder):

        #
        # information about the cluster
        #
        self.id = clusterId
        self.analysisfolder = analysisfolder # link to the analysis folder for easy access
        self.readPairCount = None # total readpairs in cluster
        self.barcodeSequence = None # the DBS consensus sequence
        self.barcodeQuality = None
        self.annotations = {} # other information
        self.analyzed = False # flad for knowing if the cluster is already analyzed or if analysis need to be done
        self.minMAPQ = 0 # minimum mapping quality allowed for cluster NOTE THAT THIS ONE SHOULD BE AND WE SHOULD USE ONLY "analysisfolder.settings.minmapq"-or-whatever-thing
        self.constructTypes = None # a dictionary keeping track of all construct types observed in the read pairs of the cluster, see readppair definition for more info
        self.readPairsInBamFile = None # the number of read pairs from this cluster that are present in the bam file
        self.mappedSEReads = None # number of mapped Single End (SE) reads (ie not pairs)
        self.SEreadsPassMappingQualityFilter = None # number of SE reads that map with mapq above cutoff
        self.goodReadPairs = None # number of or list??? need to check code and fix this comment ----- CHANGE NEEDED HERE!
        self.duplicateReadPairs = None # count of readpairs marked as duplicates
        self.goodReadPairPositions = None # number of or list??? need to check code and fix this comment ----- CHANGE NEEDED HERE!
        self.targetInfo = None # list of dictionaries with bedstyle layout keeping info about targeted regions for this specific cluster of read pairs
        self.individual_ID_dictionary = None # dictrionary with the sequences (keys) and counts (values) of the indiivdual id sequences/barcodes found within the read pais in this cluster
        self.tableStr = None # htm string that are used in the web interface
        self.hetrozygous_positions = None # count of heterozygous positions identified in the target region definded in self.targetInfo

        #
        # connections to the reads
        #
        self.readPairIdsList = [] # list of read pair ids that are in the cluster
        self.readPairs = [] # list of actual read pair objects
        self.readPairsById = {} # sorted by idnumber
        self.readPairIdentities = [] # identities of readpair DBS to the cluster DBS seed
        self.readPairsPassFilter = [] # list of pair objects passing filter
        self.readPairsNotPassingFilter = [] # oposite of above

        #
        # for future usage if we do assebly of reads, only relavant for certain types of experimental data
        #
        self.contigIdsList = []
        self.contigCount = None
        self.contigSequences = []
        self.contigSequencesPassFilter = []
        self.contigSequencesNotPassingFilter = []
        self.nonSingletonContigs = None

        #
        # list to keep track of temporary files
        #
        self.filesCreated = []
        
        # flags for keeping track of whats been done
        self.reads_loaded = False
        self.info_loaded = False
        
    def setValues(self, clusterId,clusterTotalReadCount,readPairsList,readBarcodeIdentitiesList,clusterBarcodeSequence,clusterBarcodeQuality,contigSequencesList,annotations,constructTypes, readPairsInBamFile, mappedSEReads, SEreadsPassMappingQualityFilter, goodReadPairs, duplicateReadPairs, goodReadPairPositions, targetInfo, individual_ID_dictionary, htmlTable,analyzed,hetrozygous_positions, high_quality_cluster,):
        """ set the variable values for all info in the cluster, ususally used in conjunction with a database load in one way or another """
        assert clusterId == self.id
        self.readPairCount      = int(clusterTotalReadCount)
        self.readPairIdsList    = eval(readPairsList)
        self.readPairIdentities = eval(readBarcodeIdentitiesList)
        self.barcodeSequence    = clusterBarcodeSequence
        self.barcodeQuality     = clusterBarcodeQuality
        if contigSequencesList:
            self.contigIdsList  = eval(contigSequencesList)
        if annotations:
            self.annotations    = eval(annotations)
        else:
            self.annotations    = {}

        if constructTypes: self.constructTypes = eval(constructTypes)
        else: self.constructTypes = None
        self.readPairsInBamFile = readPairsInBamFile
        self.mappedSEReads = mappedSEReads
        self.SEreadsPassMappingQualityFilter = SEreadsPassMappingQualityFilter
        self.goodReadPairs = goodReadPairs
        self.duplicateReadPairs = duplicateReadPairs
        if goodReadPairPositions:self.goodReadPairPositions = eval(goodReadPairPositions)
        else:self.goodReadPairPositions=None
        self.targetInfo = eval(str(targetInfo))
        self.individual_ID_dictionary = eval(str(individual_ID_dictionary))
        self.tableStr = htmlTable
        self.analyzed = analyzed
        self.hetrozygous_positions = hetrozygous_positions
        self.high_quality_cluster = high_quality_cluster
        
        self.info_loaded = True

    def loadClusterInfo(self, ):
        """ (re)load the info from the database of this cluster
        """

        import sqlite3, time
        success = False
        while not success:
#            while self.analysisfolder.database.writeInProgress.value: time.sleep(0.1) # seems to cause a IOError: [Errno 9] Bad file descriptor at some point
            try:
                self.analysisfolder.database.getConnection()
                columnNames = [col[1] for col in self.analysisfolder.database.c.execute('PRAGMA table_info(barcodeClusters)').fetchall()]
                if 'constructTypes' not in columnNames:
                    info = self.analysisfolder.database.c.execute('SELECT clusterId,clusterTotalReadCount,readPairsList,readBarcodeIdentitiesList,clusterBarcodeSequence,clusterBarcodeQuality,contigSequencesList,annotations FROM barcodeClusters WHERE clusterId=?',(self.id,)).fetchall()
                    assert len(info) == 1, 'More than one ('+str(len(info))+') clusters found with id '+str(self.id)
                    (clusterId,clusterTotalReadCount,readPairsList,readBarcodeIdentitiesList,clusterBarcodeSequence,clusterBarcodeQuality,contigSequencesList,annotations) = info[0]
                    constructTypes, readPairsInBamFile, mappedSEReads, SEreadsPassMappingQualityFilter, goodReadPairs, duplicateReadPairs, goodReadPairPositions, targetInfo,individual_ID_dictionary, htmlTable,analyzed = 'None',None,None,None,None,None,'None','None',None,None,False
                    hetrozygous_positions, high_quality_cluster = None,None
                else:
                    info = self.analysisfolder.database.c.execute('SELECT clusterId,clusterTotalReadCount,readPairsList,readBarcodeIdentitiesList,clusterBarcodeSequence,clusterBarcodeQuality,contigSequencesList,annotations,constructTypes, readPairsInBamFile, mappedSEReads, SEreadsPassMappingQualityFilter, goodReadPairs, duplicateReadPairs, goodReadPairPositions, targetInfo,individual_ID_dictionary, htmlTable, analyzed, hetrozygous_positions, high_quality_cluster FROM barcodeClusters WHERE clusterId=?',(self.id,)).fetchall()
                    assert len(info) == 1, 'More than one ('+str(len(info))+') clusters found with id '+str(self.id)
                    (clusterId,clusterTotalReadCount,readPairsList,readBarcodeIdentitiesList,clusterBarcodeSequence,clusterBarcodeQuality,contigSequencesList,annotations,constructTypes, readPairsInBamFile, mappedSEReads, SEreadsPassMappingQualityFilter, goodReadPairs, duplicateReadPairs, goodReadPairPositions,targetInfo,individual_ID_dictionary,htmlTable,analyzed,hetrozygous_positions, high_quality_cluster) = info[0]

                self.analysisfolder.database.commitAndClose()

                assert clusterId == self.id
                self.setValues(clusterId,clusterTotalReadCount,readPairsList,readBarcodeIdentitiesList,clusterBarcodeSequence,clusterBarcodeQuality,contigSequencesList,annotations,constructTypes, readPairsInBamFile, mappedSEReads, SEreadsPassMappingQualityFilter, goodReadPairs, duplicateReadPairs, goodReadPairPositions,targetInfo,individual_ID_dictionary,htmlTable,analyzed,hetrozygous_positions, high_quality_cluster)
                success = True
            except sqlite3.OperationalError: time.sleep(1)

        return 0

    def loadReadPairs(self, log=True):
        """ function for loading the readpairs from the database for the specific barcode cluster
        """

        #
        # imports
        #
        import sqlite3
        import time
        starttime = time.time()
#	  try:
        from misc import Progress
        import sys
        #sys.stderr.write('now ion readpairs loader for cluster '+str(self.id)+'\n')
        
        # wait for acces to the database
        while self.analysisfolder.database.writeInProgress.value: time.sleep(0.1)
        
        #
        # reset if already loaded
        #
        self.readPairs = []
        self.readPairsByHeader = {}
        self.readPairsById = {}
        
        #
        # get the reads from the database and add the readobjects to the appropriate containers
        #
        #p = Progress(self.readPairCount, logfile=sys.stderr,unit='cluster_'+str(self.id)+'_reads', mem=True)
        if log: p = Progress(self.readPairCount, logfile=self.analysisfolder.logfile,unit='cluster_'+str(self.id)+'_reads', mem=True)
        #sys.stderr.write('progress init? for cluster '+str(self.id)+'\n')
        #sys.stderr.write('dropped='+str(self.analysisfolder.database.datadropped)+' '+str(self.id)+'\n')
        if not self.analysisfolder.database.datadropped:
            #sys.stderr.write('one step more cluster '+str(self.id)+'\n')
            for readPair in self.analysisfolder.database.getReadPairs(self.readPairIdsList):
                self.readPairs.append(readPair)
                self.readPairsById[readPair.id] = readPair
                self.readPairsByHeader[readPair.header] = readPair
                #p.update()
                if log:
                    try : p.update()
                    except ValueError: pass
            self.reads_loaded = True
        else:
            sys.stderr.write('data is dropped can not load read pair information cluster '+str(self.id)+'.\n')
            #sys.stderr.write('one step less cluster '+str(self.id)+'\n')
#	  except sqlite3.OperationalError: print 'ERROR: BarcodeCluster.loadReadPairs() is giving a sqlite3.OperationalError!!'
        # else: # THIS PART SHOULD BE OK TO REMOVE NOT USED ANYMORE!
        #     for readPair in self.analysisfolder.readsdb.getClusterReadPairs(self.id):
        #         self.readPairs.append(readPair)
        #         self.readPairsById[readPair.id] = readPair
        #         try: p.update()
        #         except ValueError: pass
        #print str(self.id)+'\t'+str(time.time()-starttime)+'\t'+str(len(self.readPairIdsList))

        #self.readPairsByHeader = {pair.header:pair for pair in self.readPairs}
        
        return 0

    @property
    def allreadssamechrom(self,):
        """ checks if all the reads are mapping on the same reference chromosome sequence and returns a bool
        """
        
        tmp = {}
        for readPair in self.readPairs:
            if readPair.mapQR1 >= self.minMAPQ and readPair.mapQR2 >= self.minMAPQ:
                tmp[readPair.refNameR1] = True
                tmp[readPair.refNameR2] = True
        
        count = 0
        for chrom in tmp:
            if chrom != None: count+=1
        
        if count == 1:
            self.chromosome = chrom
            return True
        elif count > 1: return False
        else: return None

    @property
    def allreadssamepos(self,):
        """ checks if all the reads has the same mapping posistion on the reference and returns a bool
        """

        tmp1 = {}
        tmp2 = {}
        for readPair in self.readPairs:
            if readPair.mapQR1 >= self.minMAPQ and readPair.mapQR2 >= self.minMAPQ:
                tmp1[readPair.refPosR1] = True
                tmp2[readPair.refPosR2] = True

        count1 = 0
        for pos in tmp1:
            if pos != None: count1+=1
        count2 = 0
        for pos in tmp2:
            if pos != None: count2+=1

        if count1 == 1 and count2 == 1: return True
        elif count1 > 1 or count2 > 1: return False
        else: return None

    def createBamFile(self,createIndex=False,cigarDummyForDupCheck = True, return_reads_dict=False, log=True):
        """ creates a bamfile with the reads specific for the clusster
        """

        #
        # imports
        #
        from misc import thousandString
        import pysam
        import time
        import subprocess
        import sys
        import os
        import operator

        if not self.readPairs:
            #
            # Load the read pairs from database
            #
            if log:
                try: self.analysisfolder.logfile.write('Loading reads for cluster '+str(self.id)+' ... '+'\n')
                except ValueError: pass
            self.loadReadPairs(log=log)
            self.build_individual_ID_dictionary()

        #
        # get the reads from the original bam file with all reads and write to new cluster specific bamfile
        #
        bamfile =  pysam.Samfile(self.analysisfolder.dataPath+'/mappedInserts.bam')
        
        # modify bamfile header to have the correct sort order tag in the cluster specific output bam file
        newHeader = bamfile.header 
        newHeader['HD']['SO']='coordinate'
        
        # create an dictionary to store the reads in memory
        readsDict = {reference['SN']:{} for reference in bamfile.header['SQ']}
        readsDict['unmapped'] = []
        pairs = [] # too keep track of the pairs connection
        
        # sort reads by position in bamfile to optimize reading file
        seekPos = {}
        for pair in self.readPairs:
            if pair.bamFilePos: seekPos[pair.bamFilePos] = pair
        
        # get the reads in memory from original bamfile
        for fileposition, pair in sorted(seekPos.iteritems(), key=operator.itemgetter(0)):
            bamfile.seek(pair.bamFilePos) # jump to position in file
            r1 = bamfile.next() # get read 1 in pair
            r2 = bamfile.next() # get read 2 in pair
            assert pair.header[1:] == r1.query_name, 'Error: read pair headers dont match '+pair.header[1:]+' == '+r1.query_name+'\n'
            r1.set_tag('bc',self.id)
            r2.set_tag('bc',self.id)
            r1.set_tag('in',self.individual_id)
            r2.set_tag('in',self.individual_id)
            if 'in_allele' in self.__dict__:
                r1.set_tag('al',self.in_allele)
                r2.set_tag('al',self.in_allele)
            pairs.append([r1,r2])
            
            # add the reads to in memory dict sorted by referencename and coordinate
            for read in [r1,r2]:
                if read.reference_id >= 0:
                    try: readsDict[read.reference_name][read.reference_start].append(read)
                    except KeyError:
                         readsDict[read.reference_name][read.reference_start] = [read]
                else: readsDict['unmapped'].append( read )
        
        #
        # find potential duplicates in the bamfile
        #
        dupMarkingDict = {reference['SN']:{} for reference in bamfile.header['SQ']}
        for pair in pairs:
            read1 = pair[0]
            read2 = pair[1]
            
            # check that read pair is mapped to a reference
            if read1.reference_id >= 0:
                # define the most 3 prime read on the reference strand as being "first in pair" (only for this check comparison)
                # REMOVED this as the pairs will be different if you change r1 and r2 ie != PCR duplicate
                #if read1.reference_start > read2.reference_start:
                #    read1 = pair[1]
                #    read2 = pair[0]
                #    pair = pair[::-1]
                
                # add to dictionary sorted by r1 and r2 positions to find groups of potential duplicates
                try:             dupMarkingDict[read1.reference_name][int(read1.reference_start)][int(read2.reference_start)].append(pair)
                except KeyError:
                    try:             dupMarkingDict[read1.reference_name][int(read1.reference_start)][int(read2.reference_start)] = [pair]
                    except KeyError: dupMarkingDict[read1.reference_name][int(read1.reference_start)] = {int(read2.reference_start):[pair]}
                
        #
        # go through potential duplicates and check cigar + directions if duplicated score by basequalities and mark (set flag in bamfile)
        # (note that r1 are here defined as the read most towards the 3prim end not the first read in the pair)
        #
        
        #
        # Dupmarking as similar to picard as possible according to http://broadinstitute.github.io/picard/faq.html
        # Q: How does MarkDuplicates work?
        # A: The MarkDuplicates tool finds the 5' coordinates and mapping orientations of each read pair (single-end data is also handled).
        # It takes all clipping into account as well as any gaps or jumps in the alignment. Matches all read pairs using the 5' coordinates and their orientations.
        # It marks all but the "best" pair as duplicates, where "best" is defined as the read pair having the highest sum of base qualities of bases with Q >= 15.
        # NOTE THAT: SE MAPPING MIGHT NOT BE HANDLED IN THE CORRECT WAY CHECK THIS OUT LATER!!
        #
        for reference_name, r1_positions in dupMarkingDict.iteritems():
            for r1_position,r2_positions in r1_positions.iteritems():
                for r2_position, reads_with_same_pos in r2_positions.iteritems():
                    
                    # make dict for direction and cigar check
                    direction_and_cigar  = {'fwd':{'fwd':{},'rev':{}},'rev':{'fwd':{},'rev':{}}}
                    
                    # fill the direction and cigar check dict
                    for pair in reads_with_same_pos:
                        read1 = pair[0]
                        read2 = pair[1]
                        
                        if not cigarDummyForDupCheck:
                            try:                 direction_and_cigar[{True:'rev',False:'fwd'}[read1.is_reverse]][{True:'rev',False:'fwd'}[read2.is_reverse]][str(read1.cigar)][str(read2.cigar)].append(pair)
                            except KeyError:
                                try:             direction_and_cigar[{True:'rev',False:'fwd'}[read1.is_reverse]][{True:'rev',False:'fwd'}[read2.is_reverse]][str(read1.cigar)][str(read2.cigar)] = [pair]
                                except KeyError: direction_and_cigar[{True:'rev',False:'fwd'}[read1.is_reverse]][{True:'rev',False:'fwd'}[read2.is_reverse]][str(read1.cigar)] = {str(read2.cigar):[pair]}
                        else:
                            # use a dummy string for a stricter duplication check, resullting in that reads that mapp with same coordinates but different cigar strings will be marked as duplicates
                            try:                 direction_and_cigar[{True:'rev',False:'fwd'}[read1.is_reverse]][{True:'rev',False:'fwd'}[read2.is_reverse]][str('dummy')][str('dummy')].append(pair)
                            except KeyError:
                                try:             direction_and_cigar[{True:'rev',False:'fwd'}[read1.is_reverse]][{True:'rev',False:'fwd'}[read2.is_reverse]][str('dummy')][str('dummy')] = [pair]
                                except KeyError: direction_and_cigar[{True:'rev',False:'fwd'}[read1.is_reverse]][{True:'rev',False:'fwd'}[read2.is_reverse]][str('dummy')] = {str('dummy'):[pair]}                    

                    # for all groups of identically mapped reads
                    for r1_direction, r2_directions in direction_and_cigar.iteritems():
                        for r2_direction, r1_cigars in r2_directions.iteritems():
                            for r1_cigar, r2_cigars in r1_cigars.iteritems():
                                for r2_cigar, identically_mapped_pairs in r2_cigars.iteritems():

                                    # calculate the sum of all base qualities in read pair, add them to dict and sort by them
                                    baseQualitySums = {}
                                    for pair in identically_mapped_pairs:
                                        read1 = pair[0]
                                        read2 = pair[1]
                                        # calculate the pairBaseQualitySum as sum of base qualities of bases with Q >= 15
                                        pairBaseQualitySum = sum([q for q in read1.query_qualities if q >= 15])+sum([q for q in read2.query_qualities if q >= 15])
                                        try:             baseQualitySums[pairBaseQualitySum].append(pair)
                                        except KeyError: baseQualitySums[pairBaseQualitySum]=[pair]
                                    pairsSortedbyqSum =[ (pairBaseQualitySum,pairList) for qSupairBaseQualitySumm,pairList in sorted(baseQualitySums.iteritems(), key=operator.itemgetter(0))]
                                    
                                    # for all but the highest scoring mark the reads as duplicates
                                    for (pairBaseQualitySum,pairList) in pairsSortedbyqSum[:-1]:
                                        for r1,r2 in pairList:
                                            if self.analysisfolder.settings.type != 'HLA':
                                                r1.is_duplicate = True
                                                r2.is_duplicate  = True
                                            r1.set_tag('cd',1)
                                            r2.set_tag('cd',1)
                                    
                                    # get all the pairs with the highest score and mark all but one as duplicate no sorting just what happens to be last in list
                                    pairBaseQualitySum,pairList = pairsSortedbyqSum[-1]
                                    for r1,r2 in pairList[:-1]:
                                        if self.analysisfolder.settings.type != 'HLA':
                                            r1.is_duplicate = True
                                            r2.is_duplicate = True
                                        r1.set_tag('cd',1)
                                        r2.set_tag('cd',1)
            
        #
        # print the reads to the bamfile in the order specified in bamfile header and coordinate sorted
        #
        if not return_reads_dict:
            outputBam = pysam.Samfile(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam',mode='wb',header=newHeader)
            for referenceName in [ reference['SN'] for reference in bamfile.header['SQ'] ]:
                positions = readsDict[referenceName]
                for position,readsList in sorted(positions.iteritems(), key=operator.itemgetter(0)):
                    for read in readsList: outputBam.write(read)
            # lastly print the unmapped (missing refID) reads to the bamfile and close the file
            for read in readsDict['unmapped']: outputBam.write(read)
            outputBam.close()
        
            # index the bamfile
            if createIndex: pysam.index(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam', self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bai')
            
            # keep track of temporary files
            self.filesCreated.append(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam')
            if createIndex: self.filesCreated.append(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bai')
        
        # these files will not be created anymore if needed run the picard marking or write a function that creates them
        # self.filesCreated.append(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.metrics.txt')
        
        # update the flags in the database
        if self.analysisfolder.settings.debug:
            updateValues = [ (int(pair[0].flag), int(pair[1].flag),self.readPairsByHeader[str('@'+pair[0].query_name)].id) for pair in pairs]
            self.analysisfolder.database.getConnection()
            self.analysisfolder.database.c.executemany('UPDATE reads SET mappingFlagR1=?, mappingFlagR2=? WHERE id=?', updateValues)
            self.analysisfolder.database.commitAndClose()
        
        if return_reads_dict: return readsDict
        
        return 0

    def build_individual_ID_dictionary(self,):
        self.individual_ID_dictionary = {}
        
        from misc import hamming_distance
        try: from hamming_cython_solution import hamming_loop as hamming_distance
        except ImportError: pass
        
        for read_pair in self.readPairs:
                #
                # add info about the id id found in the read pair to the "cluster-wide" dictionary
                #
                try:             self.individual_ID_dictionary[read_pair.individual_id] += 1
                except KeyError: self.individual_ID_dictionary[read_pair.individual_id]  = 1
        #
        # match the index references sequnces with the individual index 
        #
        temporary_indIDdict = {}
        for individual_id_sequence, count in self.individual_ID_dictionary.iteritems():
            
            this_is_a_known_id_sequence = None # set flag to None
            
            individual_index_missmatches_allowed = int(self.analysisfolder.settings.maxIndividualIndexMissMatches)
            
            if individual_id_sequence == None:
                try: temporary_indIDdict['other_exon'] += count
                except KeyError: temporary_indIDdict['other_exon'] = count
                continue
            
            # check against known sequences!!!
            for index_name,index_sequence in self.analysisfolder.individual_id_fasta_sequences_by_id.iteritems():
                if len(index_sequence) != len(individual_id_sequence): continue
                mismatch_count = hamming_distance(individual_id_sequence, index_sequence)
                
                if mismatch_count <= individual_index_missmatches_allowed:
                    # we have a match this is a known sequence
                    this_is_a_known_id_sequence = True
                    break
            
            if this_is_a_known_id_sequence:
                try: temporary_indIDdict[index_name] += count
                except KeyError: temporary_indIDdict[index_name] = count
            else:
               try: temporary_indIDdict['unknown'] += count
               except KeyError: temporary_indIDdict['unknown'] = count
        
        self.individual_ID_dictionary = temporary_indIDdict

    def analyze(self,createBamIndex=False):
        """ analyze and get statisstics about the cluster and how the reads in the cluster map to the reference etc
        """

        #
        # imports
        #
        import time
        from misc import hamming_distance
        try: from hamming_cython_solution import hamming_loop as hamming_distance
        except ImportError: pass
        from misc import thousandString
        from misc import percentage
        import pysam
        import sys

        starttime = time.time()

        #
        # Load cluster data and initiate values for counters etc
        #
        if self.analysisfolder.settings.debug: print 'Analyzing data in cluster '+str(self.id)
        try: self.analysisfolder.logfile.write('Analyzing data in cluster '+str(self.id)+' ... '+'\n')
        except ValueError:
            #sys.stderr.write('Analyzing data in cluster '+str(self.id)+' ... '+'\n')
            #self.analysisfolder.logfile = open(self.analysisfolder.logfile.name,'a')
            #self.analysisfolder.logfile.write('Analyzing data in cluster '+str(self.id)+' ... '+'\n')
            pass

        constructTypes = {}
        readPairsInBamFile = 0
        readPairsInBamFileCheck = 0
        mappedSEReads = 0
        SEreadsPassMappingQualityFilter = 0
        goodReadPairs = 0
        duplicateReadPairs = 0
        goodReadPairsRows = ''
        unmappedReadPairsRows = ''
        duplicateReadPairsRows = ''
        goodReadPairPositions = {}

        #
        # Load the read pairs from database
        #
        try: self.analysisfolder.logfile.write('Loading reads for cluster '+str(self.id)+' ... '+'\n')
        except ValueError:
            #sys.stderr.write('Loading reads for cluster '+str(self.id)+' ... '+'\n')
            pass
        loadPairsTime = time.time()
        self.loadReadPairs()
        loadPairsTime = time.time() - loadPairsTime
        self.build_individual_ID_dictionary()
        #sys.stderr.write('reads loaded for cluster '+str(self.id)+' ...  in '+str(loadPairsTime)+'s\n')

        #
        # build the bamfile with read mappings
        #
        try:self.analysisfolder.logfile.write('Creating bamfiles for cluster_'+str(self.id)+' ... '+'\n')
        except ValueError:
            #sys.stderr.write('Creating bamfiles for cluster_'+str(self.id)+' ... '+'\n')
            pass
        createBamTime = time.time()
        self.createBamFile(createIndex=createBamIndex)
        createBamTime = time.time() - createBamTime
        try:self.analysisfolder.logfile.write('Bamfiles ready for cluster_'+str(self.id)+'.'+'\n')
        except ValueError:
            #sys.stderr.write('Bamfiles ready for cluster_'+str(self.id)+'.'+'\n')
            pass
        bamfile = pysam.Samfile(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam')

        #
        # checking constructypes in read population...
        #
        for pair in self.readPairs:
            if pair.bamFilePos: readPairsInBamFile+=1
            try: constructTypes[ pair.construct ] += 1
            except KeyError: constructTypes[ pair.construct ] = 1

        #
        # Parse the bamfile
        #
        # # # self.individual_ID_dictionary = {}
        parseBamTime = time.time()
        try:self.analysisfolder.logfile.write('Making reads table forcluster '+str(self.id)+'.\n')
        except ValueError:
            #sys.stderr.write('Making reads table forcluster '+str(self.id)+'.\n')
            pass
        last_pair_chrom = None
        position_of_last_pair = None
        self.annotations['percentage_of_pairs_close_to_other'] = 0
        close_total = 0
        for alignedReadRead in bamfile:

            #
            # get the refernce names for both reads in the read pair
            #
            if not alignedReadRead.is_unmapped: r1ReferenceName = bamfile.getrname(alignedReadRead.tid)
            else: r1ReferenceName = 'NA'
            if not alignedReadRead.mate_is_unmapped: r2ReferenceName = bamfile.getrname(alignedReadRead.rnext)
            else: r2ReferenceName = 'NA'
  
            #
            # Filters
            #
            nicePair = bool( r1ReferenceName == r2ReferenceName and not alignedReadRead.is_unmapped and not alignedReadRead.mate_is_unmapped )
            passMappingQuality = bool(alignedReadRead.mapq >= int(self.analysisfolder.settings.mapqCutOff))
            if not alignedReadRead.is_unmapped: mappedSEReads += 1
            if passMappingQuality: SEreadsPassMappingQualityFilter += 1
  
            #
            # To do paired end checks choose read one
            #
            if alignedReadRead.is_read1: 

                readPairsInBamFileCheck += 1
                
                #
                # checking how many of the nice pairs that map within 1e5 bases ie 100kb of any other nice pair
                #
                this_read_is_close_to_other = False
                if nicePair and passMappingQuality and not alignedReadRead.is_duplicate:
                    if position_of_last_pair:
                        close_total += 1
                        if r1ReferenceName != 'NA' and last_pair_chrom == r1ReferenceName and alignedReadRead.pos-position_of_last_pair < 1e4:
                            self.annotations['percentage_of_pairs_close_to_other'] += 1
                            this_read_is_close_to_other = True
                            #print 'CLOSE #### ',last_pair_chrom,' ==', r1ReferenceName,' and ',alignedReadRead.pos-position_of_last_pair,' < 1e4'
                        else:
                            pass#print last_pair_chrom,' ==', r1ReferenceName,' and ',alignedReadRead.pos-position_of_last_pair,' > 1e4'
                    position_of_last_pair = alignedReadRead.pos
                    last_pair_chrom = r1ReferenceName

                #
                # Create a HTM table row for quick vizualisation later - THIS COULD BE CHANGED TO CSV TO ANEABLE SOME NICER D3JS STUFF
                #
                row = '<tr><td>'
                row += '<a href="read'+str(self.readPairsByHeader['@'+alignedReadRead.qname].id)+'">'
                # set header color and print header
                if nicePair and passMappingQuality and not alignedReadRead.is_duplicate: row += '<font color="green">'
                elif nicePair and passMappingQuality: row += '<font color="blue">'
                else: row += '<font color="red">'
                
                #row += alignedReadRead.qname+ '</td>'
                row += str(self.readPairsByHeader['@'+alignedReadRead.qname].id)+ '</td>' # save read pair id instead of header to save space in database
                row += '</a>'
                row +='<td>'+str(alignedReadRead.flag)+'</td>' # the samflag
                
                #chromosome
                if r1ReferenceName == r2ReferenceName: row += '<td>'+str(r1ReferenceName)+'</td>'
                else:  row += '<td>r1='+str(r1ReferenceName)+' r2='+str(r2ReferenceName)+'</td>'
                
                #positions
                if alignedReadRead.pos: row += '<td>'+thousandString(alignedReadRead.pos)+'</td>'
                else:row += '<td>'+str(alignedReadRead.pos)+'</td>'
                if alignedReadRead.pnext: row += '<td>'+thousandString(alignedReadRead.pnext)+'</td>'
                else:row += '<td>'+str(alignedReadRead.pnext)+'</td>'
                
                row += '<td>'+str(abs(alignedReadRead.isize))+'</td>' # insert size
                row += '<td>'+str(alignedReadRead.mapq)+'</td>' # mapping quality
                #row += '<td>'+str(alignedReadRead.cigar)+'</td>' # cigar string
                row += '<td>'+str(alignedReadRead.is_proper_pair) #properpair flag
                if this_read_is_close_to_other: row+=' +' # add plus to the flag above if close to another read
                row+='</td>'
                row += '<td>'+str(self.readPairsByHeader['@'+alignedReadRead.qname].individual_id)+'</td>' # the individual id of the read
                row += '</tr>'
                
                # add row to the correct group
                if nicePair and passMappingQuality and not alignedReadRead.is_duplicate:
                    goodReadPairsRows += row
                elif nicePair and passMappingQuality:
                    duplicateReadPairsRows += row
                else:
                    unmappedReadPairsRows += row
                
                #
                # add info about the id id found in the read pair to the "cluster-wide" dictionary
                #
                # # # try: self.individual_ID_dictionary[self.readPairsByHeader['@'+alignedReadRead.qname].individual_id] += 1
                # # # except KeyError: self.individual_ID_dictionary[self.readPairsByHeader['@'+alignedReadRead.qname].individual_id] = 1

                #
                # Save coordinate of reads that mapp in nice pairs
                #
                if nicePair and passMappingQuality:
                    goodReadPairs += 1
                    if alignedReadRead.is_duplicate: duplicateReadPairs += 1
                    else:
                        try:
                            goodReadPairPositions[r1ReferenceName].append(min(alignedReadRead.pos,alignedReadRead.pnext))
                        except KeyError:
                            goodReadPairPositions[r1ReferenceName]   =   [min(alignedReadRead.pos,alignedReadRead.pnext)]
        parseBamTime = time.time() - parseBamTime
        
        #
        # convert counts to percentage
        #
        self.annotations['percentage_of_pairs_close_to_other'] = percentage(self.annotations['percentage_of_pairs_close_to_other'],close_total)
        #print self.annotations

        #
        # assert that the database and bamfile counts match
        #
        assert readPairsInBamFile == readPairsInBamFileCheck, '## ERROR ## : The number of reads in the bamfile is not correct!\n'
        
        #
        # match the index references sequnces with the individual index 
        #
        # # # temporary_indIDdict = {}
        # # # for individual_id_sequence, count in self.individual_ID_dictionary.iteritems():
        # # #     
        # # #     this_is_a_known_id_sequence = None # set flag to None
        # # #     
        # # #     individual_index_missmatches_allowed = int(self.analysisfolder.settings.maxIndividualIndexMissMatches)
        # # #     
        # # #     if individual_id_sequence == None:
        # # #         try: temporary_indIDdict['other_exon'] += count
        # # #         except KeyError: temporary_indIDdict['other_exon'] = count
        # # #         continue
        # # #     
        # # #     # check against known sequences!!!
        # # #     for index_name,index_sequence in self.analysisfolder.individual_id_fasta_sequences_by_id.iteritems():
        # # #         if len(index_sequence) != len(individual_id_sequence): continue
        # # #         mismatch_count = hamming_distance(individual_id_sequence, index_sequence)
        # # #         
        # # #         if mismatch_count <= individual_index_missmatches_allowed:
        # # #             # we have a match this is a known sequence
        # # #             this_is_a_known_id_sequence = True
        # # #             break
        # # #     
        # # #     if this_is_a_known_id_sequence:
        # # #         try: temporary_indIDdict[index_name] += count
        # # #         except KeyError: temporary_indIDdict[index_name] = count
        # # #     else:
        # # #        try: temporary_indIDdict['unknown'] += count
        # # #        except KeyError: temporary_indIDdict['unknown'] = count
        # # # 
        # # # self.individual_ID_dictionary = temporary_indIDdict
        # # # #print self.individual_ID_dictionary

        #
        # Make the full html table in one string together with the info about potential u=individual ids/barcodes found
        #
        headerRow = 'Individual Id sequenes found:<br>'
        for seq, count in self.individual_ID_dictionary.iteritems():
                headerRow += '    '+str(seq)+' '+str(count)+'<br>'
        headerRow += '<br><br><tr>'
        headerRow += '<th>header</th>'
        headerRow += '<th>flags</th>'
        headerRow += '<th>chromosome</th>'
        headerRow += '<th>pos R1</th>'
        headerRow += '<th>pos R2</th>'
        headerRow += '<th>insertsize</th>'
        headerRow += '<th>mapQ</th>'
#        headerRow += '<th>CIGAR</th>'
        headerRow += '<th>ProperPair</th>'
        headerRow += '<th>ind id</th>'
        headerRow += '</tr>'
        self.tableStr = '<table>' +headerRow+ goodReadPairsRows + duplicateReadPairsRows + unmappedReadPairsRows + '</table>'

        #
        # save some of the stats for later
        #
        self.constructTypes = constructTypes
        self.readPairsInBamFile = readPairsInBamFile
        self.mappedSEReads = mappedSEReads
        self.SEreadsPassMappingQualityFilter = SEreadsPassMappingQualityFilter
        self.goodReadPairs = goodReadPairs
        self.duplicateReadPairs = duplicateReadPairs
        self.goodReadPairPositions = goodReadPairPositions

        try:self.analysisfolder.logfile.write('Cluster '+str(self.id)+' analyzed in '+str(round(time.time()-starttime,2))+' seconds '+'\n')
        except ValueError:
            #sys.stderr.write('Cluster '+str(self.id)+' analyzed in '+str(round(time.time()-starttime,2))+' seconds '+'\n')
            pass
        self.analyzed = True
        if self.analysisfolder.settings.debug: sys.stdout.write(str(self.id)+'\t'+str(self.readPairCount)+'\t'+str(time.time()-starttime)+'\t'+str(loadPairsTime)+'\t'+str(createBamTime)+'\t'+str(parseBamTime)+'\n')

    def updatedb(self,doUpdate=True,returnTuple=False):
        """ function for updating the daatabase with information about the cluster
        """
        
        if doUpdate:
            with self.analysisfolder.database.lock:
                self.analysisfolder.database.writeInProgress.value = True
                import sqlite3
                import time
                updated = False
                while not updated:
                    try: 
                        self.analysisfolder.database.getConnection()
                        
                        #
                        # check the column headers and add missing information
                        #
                        self.analysisfolder.database.c.execute('PRAGMA table_info(barcodeClusters)')
                        columnNames = [col[1] for col in self.analysisfolder.database.c.fetchall()]
                        if 'constructTypes' not in columnNames:
                            try: self.analysisfolder.logfile.write('Creating columns in table barcodeClusters in database \n')
                            except ValueError: pass
                            self.analysisfolder.database.getConnection()
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column constructTypes string")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column readPairsInBamFile integer")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column mappedSEReads integer")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column SEreadsPassMappingQualityFilter integer")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column goodReadPairs integer")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column duplicateReadPairs integer")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column goodReadPairPositions string")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column htmlTable string")
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column analyzed BOOLEAN")
                        if 'targetInfo' not in columnNames:
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column targetInfo string")
                        if 'individual_ID_dictionary' not in columnNames:
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column individual_ID_dictionary string")
                        if 'hetrozygous_positions' not in columnNames:
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column hetrozygous_positions int")
                        if 'high_quality_cluster' not in columnNames:
                            self.analysisfolder.database.c.execute("alter table barcodeClusters add column high_quality_cluster BOOLEAN")
                        #self.hetrozygous_positions
                        #self.high_quality_cluster
                        
                        #
                        # do the actual update
                        #
                        self.analysisfolder.database.c.execute(
                                'UPDATE barcodeClusters SET annotations=?, constructTypes=?,readPairsInBamFile=?, mappedSEReads=?, SEreadsPassMappingQualityFilter=?, goodReadPairs=?, duplicateReadPairs=?, goodReadPairPositions=?, targetInfo=?,individual_ID_dictionary=?, htmlTable=?, analyzed=?,hetrozygous_positions=?, high_quality_cluster=? WHERE clusterId=?',
                                (str(self.annotations),str(self.constructTypes),self.readPairsInBamFile,self.mappedSEReads,self.SEreadsPassMappingQualityFilter,self.goodReadPairs,self.duplicateReadPairs,str(self.goodReadPairPositions),str(self.targetInfo),str(self.individual_ID_dictionary),self.tableStr,self.analyzed,self.hetrozygous_positions,self.high_quality_cluster,self.id)
                            )
                        self.analysisfolder.database.commitAndClose()
                        self.analysisfolder.database.writeInProgress.value = False
                        updated = True
                        print self.id, updated
                    except sqlite3.OperationalError: time.sleep(1)
        
        #
        # return a tuple formated for update of db
        #
        if returnTuple:
            return (str(self.annotations),str(self.constructTypes),self.readPairsInBamFile,self.mappedSEReads,self.SEreadsPassMappingQualityFilter,self.goodReadPairs,self.duplicateReadPairs,str(self.goodReadPairPositions),str(self.targetInfo),str(self.individual_ID_dictionary),self.tableStr,self.analyzed,self.hetrozygous_positions,self.high_quality_cluster,self.id)

    def generateHtmlSummary(self):
        """ generates a small html style summary to use in later visualization of the cluster
        """
        #
        # output for viewer
        #
        from misc import percentage
        from misc import thousandString
        outStr = 'Cluster id='+str(self.id)+', with barcode '+str(self.barcodeSequence)+' has a total of '+str(self.readPairCount)+' read pairs.'+'<br><br>\n'
        outStr += '    ' + str(percentage(self.readPairsInBamFile,self.readPairCount))+'% of the read pairs are in the bamfile ('+str(thousandString(self.readPairsInBamFile))+' of '+str(thousandString(self.readPairCount))+'read pairs ) .<br>\n'
        #outStr += str(self.constructTypes)+'.<br>\n'
        outStr += str(percentage(self.mappedSEReads, self.readPairsInBamFile*2))+'% of the reads (SE) are mapped ('+str(thousandString(self.mappedSEReads))+' of '+str(thousandString(self.readPairsInBamFile*2))+' reads in the bamfile).<br>\n'
        outStr += str(percentage(self.SEreadsPassMappingQualityFilter,self.readPairsInBamFile*2))+'% of the reads (SE) are mapped with mapQ GT q'+   str(self.analysisfolder.settings.mapqCutOff)+'  ('+str(thousandString(self.SEreadsPassMappingQualityFilter))+' of '+str(thousandString(self.readPairsInBamFile*2))+' reads in the bamfile).<br>\n'
        outStr += str(percentage(self.goodReadPairs,self.readPairsInBamFile))+'% of the read Pairs are mapped nice and proper ('+str(thousandString(self.goodReadPairs))+' of '+str(thousandString(self.readPairsInBamFile))+' reads in the bamfile).<br>\n'
        outStr += str(percentage(self.duplicateReadPairs,self.goodReadPairs))+'% of the mapped read pairs are duplicates ('+str(thousandString(self.duplicateReadPairs))+' of '+str(thousandString(self.goodReadPairs))+' mapped reads pairs).<br>\n'
        return outStr

    def makeGoodReadPairPositionsPlots(self,outputfilename = None):
        """ nice and old function currently not used maybe in the future :) """

        import pysam
        chromSizes = {}
        for chrom in pysam.Samfile(self.analysisfolder.dataPath+'/mappedInserts.bam').header['SQ']: chromSizes[chrom['SN']] = chrom['LN']
        
        #
        # Make plos for the chromosomes present
        #
        try: self.analysisfolder.logfile.write('Making plots for cluster '+str(self.id)+'.\n')
        except ValueError: pass
        import matplotlib.pyplot as plt
        import operator
        for chrom, data in self.goodReadPairPositions.iteritems():
  
            binSize = int(int(chromSizes[chrom])/100)
            chrom=str(chrom)
  
            plots = []
            fig, axes = plt.subplots(1, sharex=True)
            plots.append(axes.hist(data,range(0,int(chromSizes[chrom]),binSize),label='chrom '+str(chrom)))#,histtype='step'))
  
            handles, labels = axes.get_legend_handles_labels()
            hl = sorted(zip(handles, labels), key=operator.itemgetter(1))
            handles2, labels2 = zip(*hl)
            axes.legend(handles2, labels2,loc=0,fontsize='small')
  
            axes.set_xlabel('coordinate')
            axes.set_ylabel('# Number of reads')
  
            axes.set_xlim([0,int(chromSizes[chrom])])
  
            #
            # save to file
            #
            if outputfilename:
                plt.savefig(outputfilename,dpi=300,bbox_inches='tight')
                self.filesCreated.append(outputfilename)
            else:
                #plt.savefig(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.histogram.'+chrom+'.pdf',dpi=300,bbox_inches='tight')
                #self.filesCreated.append(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.histogram.'+chrom+'.pdf')
                plt.savefig(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.histogram.'+chrom+'.png',dpi=300,bbox_inches='tight')
                self.filesCreated.append(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.histogram.'+chrom+'.png')

    def removeAllFiles(self):
        """ just removes all temporary files created during the lifetime of the cluster
        """
        
        import os
        for filename in self.filesCreated:
            if os.path.exists(filename):os.remove(filename)

    def findTargetCoverage(self, output='average_readdepth', reload_targetInfo=True):
        """ Function for calculating coverage over each target region in a bedfile specified
        keyword output can be either "read_count" or "average_readdepth"
        "read_count" sets the BarcodeCluster.targetInfo[ list_index ]['mappedReadCount'] to the count of reads that has it's leftmost mapping position within the targeted region
        "average_readdepth" sets the BarcodeCluster.targetInfo[ list_index ]['averageReadDepth'] to the average read depth of non-zero bases in the targeted region
        "average_readdepth_with_zeros" sets the BarcodeCluster.targetInfo[ list_index ]['averageReadDepth'] to the average read depth of all bases in the targeted region
        """
        
        #
        # imports
        #
        from seqdata import loadBEDfile
        import sys
        
        #
        # load the target region definition
        #
        if reload_targetInfo or not self.targetInfo: self.targetInfo = loadBEDfile(self.analysisfolder.settings.targetRegionBed)
        
        #
        # if readpairs are not loaded load them
        #
        if not self.readPairs: self.loadReadPairs()
        
        if output == 'read_count':

            #
            # set counter to zero at start
            #
            for entry in self.targetInfo: entry['mappedReadCount'] = 0

            #
            # count number of reads with mapping start coordinate in each region
            #
            for readpair in self.readPairs:
                #print readpair.header, readpair.refPosR1, readpair.refPosR2
                if readpair.refPosR1 and readpair.refPosR2:
                    #print readpair.header
                    for entry in self.targetInfo:
                        if readpair.refPosR1 >= entry['start_position'] and readpair.refPosR1 <= entry['end_position']: entry['mappedReadCount'] += 1
                        if readpair.refPosR2 >= entry['start_position'] and readpair.refPosR2 <= entry['end_position']: entry['mappedReadCount'] += 1
        
        elif output == 'average_readdepth' or output == 'average_readdepth_with_zeros':

            #
            # set counter to zero at start
            #
            for entry in self.targetInfo: entry['averageReadDepth'] = 0
            
            #
            # imports
            #
            import pysam
            import os
            
            #
            # get connection to bamile
            #
            if not os.path.exists(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam'): self.createBamFile(createIndex=True)
            bamfile = pysam.Samfile(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam')
            
            for entry in self.targetInfo:

                read_depths = [column.nsegments for column in bamfile.pileup(stepper='nofilter', reference=entry['reference_name'], start=entry['start_position'], end=entry['end_position']) if (column.pos >= entry['start_position'] and column.pos <= entry['end_position']) ]

                try:
                    if output == 'average_readdepth_with_zeros': entry['averageReadDepth'] = round(float(sum(read_depths))/float(entry['end_position']-entry['start_position']+1),2)
                    elif output == 'average_readdepth':          entry['averageReadDepth'] = round(float(sum(read_depths))/float(len(read_depths)),2)
                except ZeroDivisionError: entry['averageReadDepth'] = 0

        #
        # print a debug message
        #
        if self.analysisfolder.settings.debug:
            for entry in self.targetInfo:
                if 'mappedReadCount' in  entry: sys.stdout.write(entry['entry_name']+'(rc)='+str(entry['mappedReadCount'])+'\t')
                if 'averageReadDepth' in entry: sys.stdout.write(entry['entry_name']+'(rd)='+str(entry['averageReadDepth'])+'\t')
            sys.stdout.write('\n')

    def findHetroZygousBasesInTarget(self, include_hetro=True,include_homo_reference=False,include_homo_non_reference=False):
        
        #
        # imports
        #
        import pysam
        import os
        import misc
        
        if not self.targetInfo: self.findTargetCoverage()

        #
        # get connection to bamile
        #
        if not os.path.exists(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam'): self.createBamFile(createIndex=True)
        bamfile = pysam.Samfile(self.analysisfolder.temp+'/cluster_'+str(self.id)+'.markedDuplicates.bam')
        try:
            reference = pysam.FastaFile(self.analysisfolder.settings.bowtie2Reference)
        except IOError:
            reference = pysam.FastaFile(self.analysisfolder.settings.bowtie2Reference+'.fa')
        
        self.high_quality_cluster = True
        
        # go through each targeted region
        for entry in self.targetInfo:
            
            # define new information containers for entry dictrionary
            entry['hetrozygous_positions'] = {}
            entry['non_reference_positions'] = {}
            entry['homo_reference_positions'] = {}
            entry['missing_data'] = {}
            
            tmp_coverage_check = {}
            
            # make a pilup of aligned bases for each base in targeted region
            for pileup_column in bamfile.pileup(stepper='nofilter', reference=entry['reference_name'], start=int(entry['start_position'])-1, end=int(entry['end_position'])+1):
                
                # "assert" that the base are within target
                if pileup_column.pos >= entry['start_position'] and pileup_column.pos <= entry['end_position']:
                    
                    # check readcount above defined cutoff
                    if pileup_column.nsegments >= int(self.analysisfolder.settings.minReadDepthForVariantCalling): #change this to not only hetro variant but variant callin general
                        
                        # init counters
                        bases_in_this_position = {}
                        inserted_bases_in_next_position = {}
                    
                        #check all reads that align to this position and sequences phred quality
                        for pileup_read in pileup_column.pileups:
                                                        
                            # if next position is an insertion save the inserted bases to be able too look for hetrozygosity 
                            if pileup_read.indel >= 0:
                                
                                if pileup_read.indel == 0: insertion = '-' # no insertion present in read ie read is same as reference
                                else:
                                    insertion = pileup_read.alignment.seq[ pileup_read.query_position+1: pileup_read.query_position+pileup_read.indel+1] # insetion present
                                    insertion_qualities = pileup_read.alignment.query_qualities[ pileup_read.query_position+1: pileup_read.query_position+pileup_read.indel+1]
                                    averager_insertion_BQ = float(sum(insertion_qualities))/float(len(insertion_qualities))
                                
                                    if averager_insertion_BQ < int(self.analysisfolder.settings.minBasePhredQuality):
                                        try: inserted_bases_in_next_position[ 'InsertLowBQ' ] += 1
                                        except KeyError: inserted_bases_in_next_position[ 'InsertLowBQ' ] = 1
                                    else:
                                        try: inserted_bases_in_next_position[ insertion ] += 1
                                        except KeyError: inserted_bases_in_next_position[ insertion ]  = 1
                            
                            # if the current reference position is deleted in read set the base to "-"
                            if pileup_read.query_position == None: 
                                assert pileup_read.is_del
                                try: bases_in_this_position[ '-' ] += 1
                                except KeyError:bases_in_this_position[ '-' ] = 1
                            
                            # if a base has in the read has aligned to the reference, get the base to be able too look for hetrozygosity 
                            else:
                                #Check the sequences phred quality
                                if pileup_read.alignment.query_qualities[ pileup_read.query_position ] < int(self.analysisfolder.settings.minBasePhredQuality):
                                    #if self.analysisfolder.settings.debug: print 'base: '+pileup_read.alignment.seq[ pileup_read.query_position ]+' at genomic position '+str(pileup_column.pos)+' is lower than cutoff ' + str(pileup_read.alignment.query_qualities[ pileup_read.query_position ])+' < ' +str(self.analysisfolder.settings.minBasePhredQuality)
                                    try: bases_in_this_position[ 'lowBQ' ] += 1
                                    except KeyError: bases_in_this_position[ 'lowBQ' ] = 1
                                    continue
                                else:
                                    try: bases_in_this_position[pileup_read.alignment.seq[ pileup_read.query_position ]] += 1
                                    except KeyError: bases_in_this_position[pileup_read.alignment.seq[ pileup_read.query_position ]] = 1
                            
                        # set flags for positions
                        this_pos_hetro = None
                        insertion_hetro = None
                        most_frequent_base = (None,0)
                        most_frequent_insertion = (None,0)
                        
                        # if low base quality was detected add position to entry, as a list for low quality sequence positions in the temporary 
                        try: tmp_low_quality_bases = bases_in_this_position['lowBQ']
                        except KeyError: tmp_low_quality_bases = 0

                        try: tmp_low_quality_insertions = inserted_bases_in_next_position['InsertLowBQ']
                        except KeyError: tmp_low_quality_insertions = 0

                        
                        # check the distribution of bases at this position
                        for base, count in bases_in_this_position.iteritems():
                            
                            # caluclate the allele frequency of the base
                            allele_frequenzy = misc.percentage(count, pileup_column.nsegments - tmp_low_quality_bases)
                            
                            if allele_frequenzy > most_frequent_base[1] and base != 'lowBQ': most_frequent_base = (base, allele_frequenzy)
                            
                            #filters
                            larger_than_cutoff = allele_frequenzy >= 100*self.analysisfolder.settings.minAlleleFreqForHetrozygousVariant
                            smaller_than_1_minus_cutoff = allele_frequenzy <= 100*(1 - self.analysisfolder.settings.minAlleleFreqForHetrozygousVariant)
                            remove_bq_entry_filter = base != 'lowBQ'
                            
                            #check filters
                            if larger_than_cutoff and smaller_than_1_minus_cutoff and remove_bq_entry_filter: this_pos_hetro = True
                        
                        # check the distribution of insertions at the next position
                        for insertion, count in inserted_bases_in_next_position.iteritems():
    
                            # caluclate the allele frequency of the base
                            allele_frequenzy = misc.percentage(count, sum(inserted_bases_in_next_position.values())-tmp_low_quality_insertions) # tmp_low_quality_insertions
                            
                            if allele_frequenzy > most_frequent_insertion[1] and insertion != 'InsertLowBQ': most_frequent_insertion = (insertion, allele_frequenzy)
                            
                            #filters
                            larger_than_cutoff = allele_frequenzy >= 100*self.analysisfolder.settings.minAlleleFreqForHetrozygousVariant
                            smaller_than_1_minus_cutoff = allele_frequenzy <= 100*(1 - self.analysisfolder.settings.minAlleleFreqForHetrozygousVariant)
                            remove_bq_entry_filter = insertion != 'InsertLowBQ'
                            
                            if larger_than_cutoff and smaller_than_1_minus_cutoff and remove_bq_entry_filter: insertion_hetro = True
                        
                        # Get the reference base at this position
                        reference_base_in_this_position = reference.fetch(reference=pileup_column.reference_name,start=pileup_column.reference_pos,end=pileup_column.reference_pos+1)
                        
                        # do read depth checks to see that the number of high quality bases are larger than defined cutoff
                        high_quality_bases_in_this_position = pileup_column.nsegments - tmp_low_quality_bases
                        high_quality_insertions = sum(inserted_bases_in_next_position.values()) - tmp_low_quality_insertions
                        this_position_read_depth_check = high_quality_bases_in_this_position >= int(self.analysisfolder.settings.minReadDepthForVariantCalling)
                        insertion_read_depth_check = high_quality_insertions >= int(self.analysisfolder.settings.minReadDepthForVariantCalling)
                        
                        # add to coverage check dict to be able to say if all positions in target are covered enough to be called
                        if this_position_read_depth_check:
                            tmp_coverage_check[pileup_column.pos] = high_quality_bases_in_this_position
                            #print tmp_coverage_check
                        
                        # if position is not hetro add it to non reference or reference base dictionaries depending on include flag
                        if this_position_read_depth_check and not this_pos_hetro and most_frequent_base[1] > int(self.analysisfolder.settings.minFreqForSeqPosition):
                            
                            if most_frequent_base[0] != reference_base_in_this_position:
                                if include_homo_non_reference:
                                    entry['non_reference_positions'][pileup_column.pos] = {'position_readdepth':pileup_column.nsegments, 'reference_base':reference_base_in_this_position, 'bases':bases_in_this_position}
                                    if self.analysisfolder.settings.debug: print 'NON referencebase found!!  ref='+reference_base_in_this_position+' mostfreqbase='+most_frequent_base[0]
                        
                            if most_frequent_base[0] == reference_base_in_this_position:
                                if include_homo_reference:
                                    entry['homo_reference_positions'][pileup_column.pos] = {'position_readdepth':pileup_column.nsegments, 'reference_base':reference_base_in_this_position, 'bases':bases_in_this_position}
                                    #print ' Referencebase found!!  ref='+reference_base_in_this_position+' mostfreqbase='+most_frequent_base[0]
                        
                        # if hetozygousity was detected add position to entry['hetrozygous_positions']
                        if this_pos_hetro or insertion_hetro:
                            
                            # if the actual position was hetrozygous
                            if this_pos_hetro and this_position_read_depth_check:
                                entry['hetrozygous_positions'][pileup_column.pos] = {'position_readdepth':pileup_column.nsegments, 'reference_base':reference_base_in_this_position}
                                entry['hetrozygous_positions'][pileup_column.pos]['bases'] = bases_in_this_position
                                if self.analysisfolder.settings.debug: print 'HETRO detected!',entry['entry_name'],pileup_column.pos
                            
                            # if next position was a hetrozygous insertion
                            if insertion_hetro and insertion_read_depth_check and high_quality_insertions>=0.5*high_quality_bases_in_this_position:
                                if pileup_column.pos not in entry['hetrozygous_positions']: entry['hetrozygous_positions'][pileup_column.pos] = {'position_readdepth':pileup_column.nsegments, 'reference_base':reference_base_in_this_position}
                                entry['hetrozygous_positions'][pileup_column.pos]['insertion_in_next_position'] = True
                                entry['hetrozygous_positions'][pileup_column.pos]['insertions'] = inserted_bases_in_next_position
                                if self.analysisfolder.settings.debug: print 'HETRO detected!',entry['entry_name'],pileup_column.pos
                            else:
                                if pileup_column.pos not in entry['hetrozygous_positions']: entry['hetrozygous_positions'][pileup_column.pos] = {'position_readdepth':pileup_column.nsegments, 'reference_base':reference_base_in_this_position}
                                entry['hetrozygous_positions'][pileup_column.pos]['insertion_in_next_position'] = False
                        
                        # check for non hetrozygous insertions
                        if not insertion_hetro and most_frequent_insertion[1] > int(self.analysisfolder.settings.minFreqForSeqPosition) and insertion_read_depth_check and high_quality_insertions>=0.5*high_quality_bases_in_this_position:
                            if include_homo_non_reference:
                                if pileup_column.pos not in entry['non_reference_positions']: entry['non_reference_positions'][pileup_column.pos] = {'position_readdepth':pileup_column.nsegments, 'reference_base':reference_base_in_this_position}
                                entry['non_reference_positions'][pileup_column.pos]['insertion_in_next_position'] = True
                                entry['non_reference_positions'][pileup_column.pos]['insertions'] = inserted_bases_in_next_position
                                if self.analysisfolder.settings.debug: print 'NON reference insertion found!!  ref='+str(inserted_bases_in_next_position)+' mostfreqinsertion='+str(most_frequent_insertion[0])
            
                
            entry['no_coverage'] = True
            entry['complete_coverage'] = True
            
            if True:#self.high_quality_cluster:
                for tmp_position in xrange(entry['start_position'],entry['end_position']+1,1):
                    if tmp_position not in tmp_coverage_check:
                        self.high_quality_cluster = False
                        entry['complete_coverage'] = False
                        entry['missing_data'][tmp_position] = True
                        if self.analysisfolder.settings.debug: print entry['entry_name'],tmp_position,'do NOT pass read coverage check!!! <----- ATTENTION!!'
                        #break
                    else:
                        if self.analysisfolder.settings.debug: print entry['entry_name'],tmp_position,tmp_coverage_check[tmp_position],'pass read coverage check'
                        entry['no_coverage']=False

        # debugging message
        if self.analysisfolder.settings.debug:
            for entry in self.targetInfo:
                
                print entry['entry_name'],entry['start_position'],'-',entry['end_position']
                
                tmp_positions = sorted(list(set(entry['hetrozygous_positions'].keys() +entry['non_reference_positions'].keys() + entry['homo_reference_positions'].keys())))
                
                #for position, info_dictionary, tmp_hetro_flag, tmp_homo_flag, tmp_ref_flag print the result
                for position in tmp_positions:
                    info_dictionary = None
                    tmp_hetro_flag = False
                    tmp_homo_flag = False
                    tmp_ref_flag = False
                    
                    if position in entry['homo_reference_positions']:
                        tmp_ref_flag = True;
                        info_dictionary = entry['homo_reference_positions'][position];
                    if position in entry['hetrozygous_positions']:
                        info_dictionary = entry['hetrozygous_positions'][position];
                        tmp_hetro_flag = True;
                    if position in entry['non_reference_positions']:
                        info_dictionary = entry['non_reference_positions'][position];
                        tmp_homo_flag = True;
                    
                    if (tmp_hetro_flag and tmp_homo_flag) or (tmp_homo_flag and  tmp_ref_flag): print 'No acceptable!!! position',position,tmp_hetro_flag,tmp_homo_flag,tmp_ref_flag
                    
                #for position, info_dictionary in entry['hetrozygous_positions'].iteritems():
                    
                    if 'bases' in info_dictionary and tmp_hetro_flag and not tmp_ref_flag: print str(position)+'.H\t',info_dictionary['reference_base'],'\t',info_dictionary['position_readdepth'],'\t'.join([base+'='+str(count) for base,count in info_dictionary['bases'].iteritems() ])
                    if 'bases' in info_dictionary and tmp_homo_flag and not tmp_ref_flag: print str(position)+'.N\t',info_dictionary['reference_base'],'\t',info_dictionary['position_readdepth'],'\t'.join([base+'='+str(count) for base,count in info_dictionary['bases'].iteritems() ])
                    if 'bases' in info_dictionary and tmp_ref_flag: print str(position)+'.r\t',info_dictionary['reference_base'],'\t',info_dictionary['position_readdepth'],'\t'.join([base+'='+str(count) for base,count in info_dictionary['bases'].iteritems() ])
                    
                    if 'insertions' in info_dictionary:
                        if tmp_ref_flag:
                            print str(position)+'.r\t',entry['homo_reference_positions'][position]['reference_base'],'\t',entry['homo_reference_positions'][position]['position_readdepth'],'\t'.join([base+'='+str(count) for base,count in entry['homo_reference_positions'][position]['bases'].iteritems() ])
                        print str(position)+'.i','\t',info_dictionary['reference_base'],'\t',info_dictionary['position_readdepth'],'\t'.join([base+'='+str(count) for base,count in info_dictionary['insertions'].iteritems() ])
        
        # write to tablestr to use at clusterspecific web interface page
        tmp = ''
        for entry in self.targetInfo:
            tmp += '<br>'+entry['entry_name']+'<br>'
            for position, info_dictionary in entry['hetrozygous_positions'].iteritems():
                if 'bases' in info_dictionary:      tmp += str(position)+'\t'+str(info_dictionary['reference_base'])+'\t'+str(info_dictionary['position_readdepth'])+'\t'+'\t'.join([base+'='+str(count) for base,count in info_dictionary['bases'].iteritems() ])+'<br>'
                if 'insertions' in info_dictionary: tmp += str(position)+'.i'+'\t'+str(info_dictionary['reference_base'])+'\t'+str(info_dictionary['position_readdepth'])+'\t'+'\t'.join([base+'='+str(count) for base,count in info_dictionary['insertions'].iteritems() ])+'<br>'
        self.tableStr = tmp +'<br><br><br>'+ self.tableStr
        
        # set number of hetrozygous positions
        self.hetrozygous_positions = sum([ len(entry['hetrozygous_positions']) for entry in self.targetInfo ])
        
        if self.analysisfolder.settings.debug:
            print 'found ',self.hetrozygous_positions, 'hetrozygous positions in total. Flag for all callable=',self.high_quality_cluster

    @property
    def individual_id(self,):
        
        if 'individual_id_mem' in self.__dict__: return self.individual_id_mem
        #else: print '########################### ind id check started ##############################'

        from misc import percentage
        import operator
                
        if not self.info_loaded: self.loadClusterInfo()
        total_reads_with_id_info = sum([count for ind_id_number, count in self.individual_ID_dictionary.iteritems() if ind_id_number != 'other_exon'])
        if not total_reads_with_id_info:
            self.individual_id_mem = 'No info'
            return 'No info'
                
        if len(self.individual_ID_dictionary) == 2 and 'other_exon' in self.individual_ID_dictionary and 'unknown' in self.individual_ID_dictionary:
            self.individual_id_mem = 'unknown id'
            return 'unknown id'
        if len(self.individual_ID_dictionary) == 1 and 'unknown' in self.individual_ID_dictionary:
            self.individual_id_mem = 'unknown id'
            return 'unknown id'

        number_ids = len([count for ind_id_number, count in self.individual_ID_dictionary.iteritems() if ind_id_number != 'unknown' and ind_id_number != 'other_exon'])
        if number_ids >= 2:
            most_frequent,second_to_most_frequent = sorted([ count for ind_id_number, count in self.individual_ID_dictionary.iteritems() if ind_id_number != 'unknown' and ind_id_number != 'other_exon'],reverse=True)[:2]
            if second_to_most_frequent >= most_frequent*(2.0/3.0):
                self.individual_id_mem = 'Non clonal'
                return 'Non clonal'
        
        most_frequent_id, count = [(ind_id_number, count) for ind_id_number, count in sorted([ (ind_id_number, count) for ind_id_number, count in self.individual_ID_dictionary.iteritems() if ind_id_number != 'unknown' and ind_id_number != 'other_exon'], key=operator.itemgetter(1),reverse=True)][0]
        
        if percentage(count,total_reads_with_id_info) >= 90:
            self.individual_id_mem = most_frequent_id
            return most_frequent_id
        else:
            self.individual_id_mem = 'nosiy signal'
            return 'nosiy signal'

def revcomp(string):
    ''' Takes a sequence and reversecomplements it'''
    complementary = comp(string)
    return complementary[::-1]

def comp(string):
    ''' Takes a sequence and complements it'''
    complement = {'A':'T','T':'A',
                        'C':'G','G':'C',
                        'N':'N',
                        'R':'Y','Y':'R',
                        'K':'M','M':'K',
                        'B':'V','V':'B',
                        'D':'H','H':'D',
                        }
    compseq = "".join([complement.get(nt.upper(), '') for nt in string])
    return compseq

def strip3primN(string):
    
    while string and string[-1] == 'N': string = string[:-1]
    
    return string

def loadBEDfile(filename):
    """ Function that reads a BED file and returns the entries as list of dictionaries
    each dictrionary in the list will have the following keys corresponding to the columns in the bedfile:
        reference_name
        start_position
        end_position
        entry_name
        value
        strand
    """

    bedDictionary = []    
    
    try:
        bed_file = open(filename)
    
        for line in bed_file:
            reference_name, start_position, end_position, entry_name, value, strand = line.rstrip().split('\t')
            bedDictionary.append( {'reference_name':reference_name, 'start_position':int(start_position), 'end_position':int(end_position), 'entry_name':entry_name, 'value':value, 'strand':strand} )
    
    except TypeError as error: # this is if bedfile is None, this should be changed later on so that bedfile list is a clusterwide template copy pasted to each cluster by eg shutil deepcopy
        pass

    return bedDictionary 
   
def uipac(bases, back='uipac'): #U	Uracil NOT SUPPORTED!!!
    if back == 'uipac':
        if 'N' in bases: return 'N'
        uniqbases={}
        for i in bases:
            uniqbases[i]=True
        bases = uniqbases.keys()
        if 'U' in bases: sys.stderr.write('WARNING in function "uipac(bases)": Uracil NOT SUPPORTED!')
        if len(bases)==1:
            if 'A' in bases: return 'A' #A	Adenine
            if 'C' in bases: return 'C' #C	Cytosine
            if 'G' in bases: return 'G' #G	Guanine
            if 'T' in bases: return 'T' #T	Thymine
            #U	Uracil NOT SUPPORTED!!!
        if len(bases)==2:
            if 'A' in bases and 'G' in bases: return 'R' #R	Purine (A or G)
            if 'C' in bases and 'T' in bases: return 'Y' #Y	Pyrimidine (C, T, or U)
            if 'A' in bases and 'C' in bases: return 'M' #M	C or A
            if 'T' in bases and 'G' in bases: return 'K' #K	T, U, or G
            if 'A' in bases and 'T' in bases: return 'W' #W	T, U, or A
            if 'C' in bases and 'G' in bases: return 'S' #S	C or G
        if len(bases)==3:
            if 'C' in bases and 'T' in bases and 'G' in bases: return 'B' #B	C, T, U, or G (not A)
            if 'A' in bases and 'T' in bases and 'G' in bases: return 'D' #D	A, T, U, or G (not C)
            if 'A' in bases and 'T' in bases and 'C' in bases: return 'H' #H	A, T, U, or C (not G)
            if 'A' in bases and 'C' in bases and 'G' in bases: return 'V' #V	A, C, or G (not T, not U)
        if len(bases)==4:
            return 'N' #N	Any base (A, C, G, T, or U)
    elif back == 'bases':
        if   bases == 'R': return ['A','G'] 
        elif bases == 'Y': return ['C','T']
        elif bases == 'M': return ['A','C']
        elif bases == 'K': return ['G','T']
        elif bases == 'W': return ['A','T']
        elif bases == 'S': return ['C','G']
        elif bases == 'B': return ['C','T','G']
        elif bases == 'D': return ['A','T','G']
        elif bases == 'V': return ['A','C','G']
        elif bases == 'H': return ['A','C','T']
        elif bases == 'N': return ['A','G','T','C']

def UIPAC2REGEXP(string):
    return string.replace('R','[AG]').replace('Y','[CT]').replace('S','[GC]').replace('W','[AT]').replace('K','[GT]').replace('M','[AC]').replace('B','[CGT]').replace('D','[AGT]').replace('H','[ACT]').replace('V','[ACG]').replace('N','[AGTC]')

def bits(i,n): 
    return tuple((0,1)[i>>j & 1] for j in xrange(n-1,-1,-1))

class SamFlag():

    def __init__(self, flag):
        """ Function that takes a flag and gets the explanation"""
        ########################-Format Description-#########################
        #	Flag	Chr	Description											#
        #1	0x0001	p	the read is paired in sequencing					#
        #2	0x0002	P	the read is mapped in a proper pair					#
        #3	0x0004	u	the query sequence itself is unmapped				#
        #4	0x0008	U	the mate is unmapped								#
        #5	0x0010	r	strand of the query (1 for reverse)					#
        #6	0x0020	R	strand of the mate									#
        #7	0x0040	1	the read is the first read in a pair				#
        #8	0x0080	2	the read is the second read in a pair				#
        #9	0x0100	s	the alignment is not primary						#
        #10	0x0200	f	the read fails platform/vendor quality checks		#
        #11	0x0400	d	the read is either a PCR or an optical duplicate	#
        #####################################################################
  
        self.readtype = None
        self.properpair = None
        self.mapped = None
        self.matemapped = None
        self.strand = None
        self.mate_strand = None
        self.readnum = None
        self.primaryalignment = None
        self.passfilter = None
        self.pcrduplicate = None

        if flag == None:
            self.flag = flag
            return None
        self.flag = int(flag)
        binary = bits(self.flag,11)
        output = ''
        self.readnum = None
        try:
            if int(binary[-1]):	self.readtype = "PE"
            else:			self.readtype = 'SE'
            if int(binary[-2]):	self.properpair = True
            else:			self.properpair = False
            if int(binary[-3]):	self.mapped = False
            else:			self.mapped = True
            if int(binary[-4]):	self.matemapped = False
            else:			self.matemapped = True
            if int(binary[-5]):	self.strand = 'rev'
            else:			self.strand = 'fwd'
            if int(binary[-6]):	self.mate_strand = "rev"
            else:			self.mate_strand = "fwd"
            if int(binary[-7]):	self.readnum = 1
            else:			pass#self.read1 = False
            if int(binary[-8]):	self.readnum = 2
            else:			pass#self.read2 = False
            if int(binary[-9]):	self.primaryalignment = False;#self.output += 'not primary alignment\t'
            else:			self.primaryalignment = True
            if int(binary[-10]):	self.passfilter=False;#self.output += 'QC failed\t'
            else:			self.passfilter=True
            if int(binary[-11]):	self.pcrduplicate=True;#self.output += 'is PCR duplicate'
            else:			self.pcrduplicate=False;
        except ValueError:
            output += '.'
        return None

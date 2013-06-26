#!/usr/bin/python
import sys,getopt,os,subprocess,re

class doxyDoc:
	src = ''
	out = ''
	cliParams = ''
			
	def __init__(self):
		try:
			if os.getuid() != 0: 
				print '\n\tThis program requires root privileges. Run as root using "sudo"\n'
				sys.exit(1)
			opts,args = getopt.getopt(sys.argv[1:],'hs:o:',['help','src=','out='])			
			print '\n\t===============>Doxygen Documentation Generator Console<===============\n'
			self.cliParams = opts
			self.__cliParams(self.cliParams)
		except Exception,error:	
			print str(error)			
			sys.exit(1)	

	def __cliParams(self,cliParams):
		for opt,arg in cliParams:
			if opt in ('-h','--help'):
				self.usage()
				sys.exit(1)
			elif opt in ('-s','--src'):
				self.src = arg
				if (not os.path.exists(self.src)) and (not os.path.isdir(self.src)): 
					raise Exception('#### Error: Invalid source path ####')
			elif opt in ('-d','--out'):
				self.out = arg
				if (not os.path.exists(self.out)) and (not os.path.isdir(self.out)):
					raise Exception('#### Error: Invalid output path ####')
		if (not self.src) or (not self.out):
			raise Exception('#### Error: Required params missing ####')
		self.__runTimeParams()

	def __runTimeParams(self):
		print '\n\tProject name is single word or a sequence of words that should identify the project\n'	
		projectName = str(raw_input('Enter Project name: '))
		if not projectName: raise Exception('#### Project name is empty ####')
		inputDirectory = self.src
		outputDirectory = self.out
		print '\n\tDoxygen selects the parser to use depending on the extension of the files it parses. Extension map assign which parser to use for a given extension.\n\tExample: "module=PHP install=PHP inc=PHP js=Javascript"\n'
		extensionMap = str(raw_input('Enter Extensions map: '))
		if not extensionMap: raise Exception('#### Extensions were empty ####')
		print '\n\tFile patterns is to specify one or more wildcard pattern (like *.cpp and *.h) to filter out the source-files in the directories.\n\tExample: "*.php *.module *.install *.inc *.js"\n'
		filePatterns = raw_input('Enter File patterns: ')		
		if not filePatterns: raise Exception('#### File patterns were empty ####')		
		print '\n\tSpecify whether or not subdirectories should be searched recursively for input files. Possible values are YES and NO.\n'
		recursiveSearch = str(raw_input('Generate documentation recursively: '))
		if not recursiveSearch: raise Exception('#### Recursive directory search is empty ####')
		elif not re.match(r'YES|NO',recursiveSearch): raise Exception('#### Should be YES or NO')		
		self.__constructConfFile(pn=projectName,ind=inputDirectory,od=outputDirectory,em=extensionMap,fp=filePatterns,rs=recursiveSearch)
											
	def __constructConfFile(self,**params):				
		doxygenProgram = 'doxygen %s %s'
		doxygenConfFile = '/tmp/DoxyConf'
		doxygenConf = subprocess.Popen(doxygenProgram %('-g',doxygenConfFile),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		doxygenConf.wait()
		if doxygenConf.returncode:
			raise Exception('#### Error: Doxygen error ####')
		if not os.path.isfile(doxygenConfFile):
			raise Exception('#### Error: Doxygen config not created ####')
		fileRead = open(doxygenConfFile,'r').readlines()
		fileWrite = open(doxygenConfFile,'w')
		for line in fileRead:		
			if re.match(r'PROJECT_NAME[\s]+=.*',line):
				line = re.sub(r'PROJECT_NAME[\s]+=.*','PROJECT_NAME = '+params['pn'],line)
			elif re.match(r'INPUT[\s]+=.*',line):
				line = re.sub(r'INPUT[\s]+=.*','INPUT = '+params['ind'],line)															
			elif re.match(r'OUTPUT_DIRECTORY[\s]+=.*',line):
				line = re.sub(r'OUTPUT_DIRECTORY[\s]+=.*','OUTPUT_DIRECTORY = '+params['od'],line)
			elif re.match(r'EXTENSION_MAPPING[\s]+=.*',line):
				line = re.sub(r'EXTENSION_MAPPING[\s]+=.*','EXTENSION_MAPPING = '+params['em'],line)
			elif re.match(r'FILE_PATTERNS[\s]+=.*',line):
				line = re.sub(r'FILE_PATTERNS[\s]+=.*','FILE_PATTERNS = '+params['fp'],line)
			elif re.match(r'RECURSIVE[\s]+=.*',line):
				line = re.sub(r'RECURSIVE[\s]+=.*','RECURSIVE = '+params['rs'],line)
			else:
				pass
			fileWrite.write(line)
		fileWrite.close()
		self.__generateDocs(doxygenConfFile,params)

	def __generateDocs(self,doxygenConfFile,params):
		doxygenProgram = 'doxygen %s'
		doxygenGenerate = subprocess.Popen(doxygenProgram %(doxygenConfFile),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		doxygenGenerate.wait()
		if doxygenGenerate.returncode:
			raise Exception('#### Error: Doxygen error ####')
		else:
			print '\n\tSuccessfully generated documentation for the project "'+params['pn']+'"'
			os.system('rm %s' %(doxygenConfFile))
			sys.exit(1)

	def usage(self):
		print	'\n\t-s | --src    Source code directory, for which the documentation has to be generated\n\t-o | --out    Output directory where the generated documentaion has to be placed\n\n\tExample usage: sudo doxydoc --src /your/source/directory --out /your/output/directory\n'
		sys.exit(1)

	def __del__(self):
		self.src
		self.out
		self.cliParams

doxyDoc()

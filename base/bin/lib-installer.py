import requests,os,sys
from N4Tools.Design import ThreadAnimation,Color,Text,Square
from bs4 import BeautifulSoup as Soup
sys.path.append(os.path.abspath(__file__).split('/bin')[0])
TOOL_NAME = __file__.split('/')[-1].split('.')[0]
from shell import BaseShell
Namelib=input(Color().reader('[$LYELLOW]SearchLib[$GREEN]~[$LRED]/[$LWIHTE]$ [$WIHTE]'))

class Search_in_Pypi:
	def __init__(self,text):
		self.url=f'https://pypi.org/search/?q={Namelib.replace(" ","+")}&o='
		self.MainLink='https://pypi.org'
	
	def getcode(self):
		return Soup(requests.get(self.url).text,'html.parser')
	def GetNames(self):
		soup=self.getcode()
		data={}
		for Form in soup.find_all('a',{'class':'package-snippet'}):
			for Name in Form.find_all('span',{'class':'package-snippet__name'}):
				for Version in Form.find_all('span',{'class':'package-snippet__version'}):
					data[Name.text]={'verison':Version.text+' ','href':self.MainLink+Form.get('href')}
		if data:return data
		else:print (Color().reader(f"\r[$YELLOW]@[$LRED]Not Lib: [$LGREEN]'{Namelib}'"));sys.exit()
	def StyleData(self):
		data=self.GetNames()
		out=''	
		index=0
		options={}
		sq=Square()
		sq.SETTINGS['square']=['╭─', '┝[$CYAN]─', '╰─', '─', '╯', '┥', '╮', '─']
		sq.SETTINGS['color']="[$LCYAN]"
		M=max([len(k+v['verison'])for k,v in data.items()])
		for k,v in data.items():
			Num='0'+str(index+1) if index+1<=9 else str(index+1)
			out+=f"[$LRED]([$NORMAL]{Num}[$LRED])[$LYELLOW]{k}:[$LGREEN]{v['verison']}[$CYAN]{'─'*(M-len(k+v['verison']))}\n"
			options[int(Num)]=v['href']
			index+=1
		return([sq.base(Color().reader(out[:-1])),options])
	def Choices(self):
		@ThreadAnimation()
		def rcv(Thread):
			out=self.StyleData()
			Thread.kill=True
			return out
		return(rcv())
		
get=Search_in_Pypi(Namelib).Choices()
Choices=get[0]
options=get[1]
print(Choices)
class BaseCmd(BaseShell):
	ToolName=TOOL_NAME
	def do_choices(self,arg):
		print(Choices)
	def do_install(self,arg):
		try:
			command=(self.GetComand(options[int(arg)]))
			print(Color().reader('[$YELLOW]@[$LBLUE]Installing...[$NORMAL]'))
			os.system(command)
		except KeyError:
			print(f'Not Lib {arg}')
		except ValueError:
			print(f'Not Lib {arg}')
	def complete_install(self,arg,*args):
		all=list(options.keys())
		if not arg:return all
		else:return [x for x in all if x.startswith(arg)]
	def GetComand(self,arg):
		@ThreadAnimation()
		def Get(Thread):
			soup=Soup(requests.get(arg).text,'html.parser')
			for Form in soup.find_all('p',{'class':'package-header__pip-instructions'}):
				for Name in Form.find_all('span',{'id':'pip-command'}):
					Thread.kill=True
					return Name.text
		return Get()
		
	def do_main(self,arg):
		return True
BaseCmd().cmdloop()

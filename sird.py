from numpy import *
from matplotlib.pyplot import *
from random import *
from matplotlib.image import *
from matplotlib.colors import *
import PIL.Image as pil
"""
Mit der Klasse sird kann ein Autostereogramm, wahlweise als Zufallspunktbild oder mit festgelegten
Muster erzeugt werden. Beispieleingabe: s=sird(500,300,5)
Nach der Erzeugung eines sird-Objektes können dessen Attribute nicht mehr verändert werden, jedoch
kann der User sich diese ausgeben lassen. Optional kann eine Depthmap als Datei angegeben werden.
Wird diese Option nicht genutzt, wird eine sinusförmige Funktion als 3D-Bild benutzt. Die Option
deform=True bewirkt, dass der erste Streifen des Bildes deformiert wird, sodass die Deformation des
gesamten Bildes minimiert wird. Die mittleren Streifen sind dadurch am wenigsten deformiert, was
wünschenswert ist. Die plotflag und exportflag gibt an, ob das Bild geplottet/exportiert werden 
soll. Der Wert depthdiv reguliert, wie stark die Tiefe des Stereograms ausgeprägt sein soll. Dabei
bewirkt ein niedriger Wert eine starke Tiefe.
"""
class pixel:
	def __init__(self,x,y,col):
		self.x=x
		self.y=y
		self.col=col
class sird:
	def __init__(self,breite,hoehe,n,depthmap='',pattern='',deform=False,plotflag=False,exportflag=True,depthdiv=0,name=''):
		self.__n=int(abs(n))
		self.__breite=int(abs(breite))#Gesamtbreite des Bildes
		self.__hoehe=int(abs(hoehe))
		self.__stripe_width=self.breite/self.n-1
		self.__cm='Greys'
		self.__import_depth_map(depthmap)
		self.depthdiv=depthdiv
		self.__FULL(pattern)
		self.__deform(deform)
		self.__name=name
		self.__plotter2(plotflag,exportflag)
	@property
	def n(self):
		return self.__n
	@property
	def breite(self):
		return self.__breite
	@property
	def hoehe(self):
		return self.__hoehe
	@property
	def stripe_width(self):
		return self.__stripe_width
	@property
	def cm(self):
		return self.__cm
	@property
	def depthdiv(self):
		return self.__depthdiv
	@depthdiv.setter
	def depthdiv(self,value):
		if value<=255*self.n: #Überprüfe, ob die maximale Verschiebung die Streifenbreite überschreiten würde.
			if self.__dmgiven:#Wenn keine Depthmap gegeben wurde, wird eine andere Tiefe benötigt.
				self.__depthdiv=4000
			else:
				self.__depthdiv=10000
		else:
			self.__depthdiv=value
	def __FULL(self,pattern):
		if pattern=='':
			self.__full_bild()
		else:
			try:
				self.__full_bild2(pattern)
			except:
				print('Pattern '+pattern+' nicht gefunden. Erstelle Zufallspunktbild.')
				self.__full_bild()
	def __first_stripe2(self,pattern_image):#erzeugt ersten Streifen für gegebenes Muster
		#In self.__max_x wird für jeden y-Wert der jeweils größte x-Wert gespeichert.
		self.__set_max_x()
		#pattern-Bild laden und zu einer Liste konvertieren: 
		self.__pattern_name=pattern_image.split('.')[0]
		pattern=pil.open(pattern_image)
		scale_factor=(self.__stripe_width)/pattern.width
		pattern=pattern.resize((int(self.__stripe_width),int(pattern.height*scale_factor)))
		pattern=asarray(pattern)
		pattern=flipud(pattern)
		pattern=list(pattern)
		#Erstelle für jeden Pixel einen colormap-Eintrag und benutze den Index des 
		#Colormapeintrages für den Farbwert des Pixelobjektes. Dieses wird für das Bild verwendet.
		colors=[]
		bild=[]
		for index in range(self.hoehe):
			i=index%len(pattern)
			bild.append([])
			for j in range(len(pattern[i])):
				pixeli=[]
				for k in range(len(pattern[i][j])):
					pixeli.append(pattern[i][j][k]/255)
				colors.append(pixeli)
				p=pixel(j,index,len(colors)-1)
				bild[index].append(p)
		self.__cm=ListedColormap(colors)
		self.__bild=array(bild)
		self.__stripe=self.__bild
		self.__first_strip=self.__bild
	def depth_sin(self,T,amp,x,y):
		self.__depth='__SIN__'
		return amp*(sin(2*pi/T*x)+sin(2*pi/T*y))-2*amp
	def __set_max_x(self):
		self.__max_x=[]
		for i in range(self.hoehe):
			self.__max_x.append(self.__stripe_width)
	def __first_stripe(self):
		self.__set_max_x()
		#erstellt Koordinaten des ersten unverzerrten streifens für ein Zufallspunktbild
		#und speichert sie als array von Punkten.
		if self.breite/self.n==int(self.breite/self.n):
		#prüfe, ob die breite durch die Anzahl der Streifen n teilbar ist
			bild=[]
			for j in range(self.hoehe):
				bild.append([])			
				for i in range(int(self.breite/self.n)):
					if randint(0,1)==1:
						p=pixel(i,j,255)
					else:
						p=pixel(i,j,0)
					bild[j].append(p)
			self.__bild=array(bild)
			self.__stripe=self.__bild
			self.__first_strip=self.__bild
		else:
			print('schlechte Abmessungen')
	def __new_stripe(self):#erzeugt neuen Streifen in Abhängigkeit vom vorhergehenden Streifen.
		stripe=[]
		self.__png=array(self.__png)
		for i in range(len(self.__stripe)):
			stripe.append([])
			for j in range(len(self.__stripe[i])):
				q=self.__stripe[i][j]
				#Verschiebung der Punkte in Abhängigkeit von dem Wert der Depthmap an der jeweiligen
				#Position:
				hx=min(round(q.x),self.__png.shape[0]-2)
				hy=min(round(q.y),self.__png.shape[1]-2)
				normierung=(self.__stripe_width-2)/255 #Farbtiefe von 256 Farben bedeutet, dass Werte von 0 bis 255 angenommen werden können. Dies wird auf eine Zahl zwischen 0 und 1 normiert.
				h=(self.__png[hx][hy]-255)*self.breite/self.depthdiv
				#Um zu verhindern, dass bereits gedoppelte Pixel überdeckt werden wird folgendes Maximum gebildet:
				x=max(q.x+self.__stripe_width+h,self.__max_x[i])
				y=q.y
				col=q.col
				p=pixel(x,y,col)
				stripe[i].append(p)
		self.__stripe=array(stripe)
		#Streifen an Bild anfügen:
		self.__bild=concatenate((self.__bild,self.__stripe),1)
	def __full_bild(self):
	#Erzeugung der n Streifen für Zufallspunktbild:
		self.__first_stripe()
		for i in range(self.n-1):
			self.__new_stripe()
	def __full_bild2(self,pattern):
	#Erzeugung der n Streifen für Pattern-Autostereogramm:
		self.__first_stripe2(pattern)
		for i in range(self.n-1):
			self.__new_stripe()
	def __deform(self,defo):
	#Das bereits erstellte Bild wird ausgewertet. Es wird für jeden y-Wert der größte vorkommende
	#x-Wert gewählt und ein Deformationsskalar d in einer Liste gespeichert. Der erste Streifen wird
	#deformiert neu erzeugt und alle anderen Streifen in Abhängigkeit von diesem ebenfalls neu 
	#berechnet.
		if defo:
			self.__deformation=[]
			for i in range(len(self.__stripe)):
				d=-(self.__bild[i][-1].x-self.breite)/2
				self.__deformation.append(d)
			self.__bild=self.__first_strip
			for i in range(len(self.__bild)):
				for j in range(len(self.__bild[i])):
					self.__bild[i][j].x=self.__bild[i][j].x+self.__deformation[i]
			self.__stripe=self.__bild
			self.__first_strip=self.__bild
			for i in range(self.n-1):
				self.__new_stripe()
		else:
			pass
	def __import_depth_map(self,png):
		if png!='':
			try:
				self.__depth=png.split('.')[0]
				png=pil.open(png)
				png=png.resize((int(self.breite-self.__stripe_width),self.hoehe))
				png=asarray(png)
				if len(png.shape)>2:
					png=png[:,:,0]
				png=invert(png)
				self.__png=flipud(png)
				self.__png=self.__png.transpose()
				self.__dmgiven=True
				#außerhalb der depthmap default-wert.
			except:
				self.__dmgiven=False
				self.__default_depthmap()
				print('Depthmap '+png+' nicht gefunden. Verwende Default-Depthmap.')
		else:
			self.__dmgiven=False
			self.__default_depthmap()
	def __default_depthmap(self):
		#erzeugt depthmap, wenn mithilfe der Funktion depth_sin, falls keine brauchbare Depthmap 
		#vom user gegeben wurde.
		breite=int(self.breite-self.__stripe_width)
		self.__png=[]
		self.__depth='SIN'
		amp=100
		T=breite/3
		for i in range(self.hoehe):
			self.__png.append([])
			for j in range(breite):
				self.__png[i].append(self.depth_sin(T,amp,j,i))
	def __plotter2(self,plotflag,exportflag):
	#plottet das Bild, zeigt es gegebenenfalls an und/oder exportiert es.
		X=[]
		Y=[]
		C=[]
		for i in range(len(self.__bild)):
			X.append([])
			Y.append([])
		#	if i<len(self.__bild)-1:
			C.append([])
			for j in range(len(self.__bild[i])):
				p=self.__bild[i][j]
				X[i].append(p.x)
				Y[i].append(p.y)
		#		if i<len(self.__bild)-1 and j<len(self.__bild[i])-1:
				C[i].append(p.col)

		for i in range(len(X)):
			X[i].append(X[i][-1]+1)
		X.append(X[-1])
		for i in range(len(Y)):
			Y[i].append(Y[i][-1])
		Y.append(Y[-1])

		pcolormesh(X,Y,C,cmap=self.__cm)
		axis('square')
		axis('off')
		if exportflag:
			filename='sird_'+str(self.breite)+'x'+str(self.hoehe)+'_'+str(self.n)+'_'+self.__depth
			if self.__cm!='Greys':
				filename=filename+'_'+self.__pattern_name+self.__name+'.png'
			else:
				filename=filename+self.__name+'.png'
			savefig(filename,dpi=1200,bbox_inches='tight',pad_inches=0)
		if plotflag:
			show()	
		cla()

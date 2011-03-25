#!/usr/bin/python

import cv, os, sys
import write_arff
import commands
import math
import copy

'''
# BLEU VERT ROUGE !
bleu  = (255,0,0)
vert  = (0,255,0)
jaune = (0,255,255)
rose  = (255,186,185)
rouge = (0,0,255)

# NOIR ET BLANC
gris  = (128,128,128)
noir  = (0,0,0)
blanc = (255,255,255)
clair = (192,192,192)
sombre = (64,64,64)
'''

# Notre .arff est une variable global
arf = None

# taille en pixel : width et height des images normalisees
NORM_W = 128
NORM_H = 128

# chargement des paths
path = "../haarcascades/"
#image_path = "../../images/"
image_path = "../../temp/"
#norm_path = "../../norm/"
norm_path = "../../tempnorm/"
dnorm_path = "../../dnorm/"
result = "../../result/"
traitement_path = "../../traitement/"

# cascades recherchees :
frontal_face = "haarcascade_frontalface_default.xml"
eyes = "haarcascade_eye.xml";
eyes2 = "haarcascade_eye_tree_eyeglasses.xml";
mouth = "haarcascade_mcs_mouth.xml";
nose = "haarcascade_mcs_nose.xml";

face_path = cv.Load(path+frontal_face)
eye_path = cv.Load(path+eyes)
eye2_path = cv.Load(path+eyes2)
mouth_path = cv.Load(path+mouth)
nose_path = cv.Load(path+nose)

# cascade sourire
s_0 = "smileD/smiled_01.xml"
s_1 = "smileD/smiled_02.xml"
s_2 = "smileD/smiled_03.xml"
s_3 = "smileD/smiled_04.xml"
s_4 = "smileD/smiled_05.xml" 
all_s_file = [s_0, s_1, s_2, s_3, s_4]
smile_list = ["s_0", "s_1", "s_2", "s_3", "s_4"]
attr_list = ["eyes", "eyes2", "mouth"]
all_s = map( (lambda x : cv.Load(path+x)), all_s_file)

# Detection des yeux, nez et bouche
def detection_eye(img):
	eyes = cv.HaarDetectObjects(img, eye_path, cv.CreateMemStorage())
	return eyes
def detection_eye2(img):
	eyes2 = cv.HaarDetectObjects(img, eye2_path, cv.CreateMemStorage())
	return eyes2
def detection_nose(img):
	nose = cv.HaarDetectObjects(img, nose_path, cv.CreateMemStorage())
	return nose
def detection_mouth(img):
	mouth = cv.HaarDetectObjects(img, mouth_path, cv.CreateMemStorage())
	return mouth
def detection(img):
	res = dict()
	res['eyes'] = detection_eye(img)
	res['eyes2'] = detection_eye2(img)
	res['nose'] = detection_nose(img)
	res['mouth'] = detection_mouth(img)
	liste_s = sourires(img)
	for s in smile_list:
		res[s] = liste_s[s]
	return res

def sourires(src):
	res = dict()
	img = cv.GetSubRect(src, (src.width*1/7, src.height*2/3, src.width*5/7, src.height/3)) 
	cpt = 0
	for s,smiles in zip(all_s, smile_list) :
		res[smiles] = len(cv.HaarDetectObjects(img, s, cv.CreateMemStorage()))
	return res


# Retourne la liste des fichiers dans le path entre en parametres
def jpg_list(path):
	res = []
	liste = commands.getoutput("ls -d "+path+"* | grep .jpg")
	liste = liste.split('\n')
	for line in liste:
		line = line.split('/')
		path = line[len(line)-2]+"/"+line[len(line)-1]
		#print path
		res.append(path)
	return res

# Boucle d'appel pour le traitement des images :
def norm_loop(in_path, out_path="", save=False):
	res = []
	jpegs = jpg_list(in_path)
	print "NORMALISATION"
	cp = 0
	for image in jpegs:
		print "Normalisation de l'image "+str(image)+" en cours"
		normal = normalisation(image)
		if save:
			save(out_path, "small_."+img, normal)
			cp += 1
		res.append(temp)
	return res
	print "FIN NORMALISATION"

def treatment_loop(in_path, out_path="", save=False):
	res = []
	jpegs = jpg_list(in_path)
	print "TRAITEMENT"
	cp = 0
	for image in jpegs:
		print "Traitement de l'image "+str(image)+" en cours"
		modif = treatments(image)
		if save:
			save(out_path, "modif."+img, modif)
			cp += 1
		res.append(temp)
	return res
	print "FIN TRAITEMENT"

def traitement_loop(liste):
	for image in liste:

# Affichage et arff sont des booleans pour savoir si on affiche et si l'on cree le fichier arff
def arff_loop(in_path, file_name="fichier_arff", div=8):
	create_arff(file_name, "emotions", div)
	jpegs = jpg_list(in_path)
	for image in jpegs:
		after_norm(image_n, image_t, boolean_arff,div)
	arf.no_more_data()
	print "Ecriture et fermeture du fichier arff terminees"

def extracteur_de_sourires(nom, src):
	img = cv.GetSubRect(src, (src.width*1/7, src.height*2/3, src.width*5/7, src.height/3)) 
	cpt = 0
	for s in all_s :
		res = cv.HaarDetectObjects(img, s, cv.CreateMemStorage())
		if len(res) == 1 :
			cpt = cpt + 1     
		if cpt == len(all_s) :
			print "\tsourire vu dans "+nom
			cv.SaveImage(result+str(cpt)+"s_"+nom, img)

# Affichage des yeux, nez et bouche + correction 
def affichage_visage((x,y,w,h), img, a=0, b=0):
	cv.Rectangle(img, (x+a,y+b), (x+w+a,y+h+b), bleu)
def affichage_eyes(deyes, img, a=0, b=0):
	for (x,y,w,h),n in deyes:
		cv.Rectangle(img, (x+a,y+b), (x+w+a,y+h+b), vert)
def affichage_eyes2(deyes2, img, a=0, b=0):
	for (x,y,w,h),n in deyes2:
		cv.Rectangle(img, (x+a,y+b), (x+w+a,y+h+b), rouge)
def affichage_nose(dnose, img, a=0, b=0):
	for (x,y,w,h),n in dnose: 
		cv.Rectangle(img, (x+a,y+b), (x+w+a,y+h+b), rose)
def affichage_mouth(dmouth, img, a=0, b=0):
	for (x,y,w,h),n in dmouth: 
		cv.Rectangle(img, (x+a,y+b), (x+w+a,y+h+b), jaune)
def affichage_corners(dcorners, img, diametre):
	for (x,y) in dcorners:
		cv.Circle(img, (x,y), diametre, rouge, -1)
def affichage(src, deyes, deyes2, dnose, dmouth, a=0, b=0):
	affichage_eyes(deyes, src, a,b)
	affichage_eyes2(deyes2, src, a,b)
	affichage_nose(dnose, src, a,b)
	affichage_mouth(dmouth, src, a,b)

def save(path, nom, img):
	print "Sauvegarde de l'image:"
	print path+nom
	cv.SaveImage(path+nom, img)

def best_mouth(mouth):
	res = ((0,0,0,0),0) 
	if len(mouth) > 0:
		val = 0
		for (x,y,w,h),n in mouth:
			if y+h > val:
				val = y+h
				res = ((x,y,w,h),n)
	return [res]

# Permet l'extraction des visages sur n'importe quelle photo et redimensionnent les visages trouves en NORM_W x NORM_H
def normalisation(img, ) :

	print ""
	if(os.path.exists(norm_path+dossier+"small_0."+img)):
		print "L'image "+str(img)+" est deja normalisee"
	else:
		print image_path+img
		src = cv.LoadImage(image_path+img)

		# On fait une copie l'image pour le traitement (en gris)
		gris = cv.CreateImage( (src.width, src.height) , cv.IPL_DEPTH_8U, 1)
		normal = cv.CreateImage((NORM_W,NORM_H), cv.IPL_DEPTH_8U, 1)
		cv.CvtColor(src, gris, cv.CV_BGR2GRAY)		

		# On detecte les visages (objects) sur l'image copiee
		faces = cv.HaarDetectObjects(gris, face_path, cv.CreateMemStorage())

		cp = 0
		for (x,y,w,h),n in faces: 
			tmp = cv.CreateImage( (w,h) , cv.IPL_DEPTH_8U, 1)
			cv.GetRectSubPix(gris, tmp, (float(x + w/2), float(y + h/2)))

			cv.EqualizeHist(tmp, tmp)
			cv.Resize(tmp, normal)

			#Detection oeil nez bouche sur l'image source:
			d = detection(tmp)
			d['mouth2'] = best_mouth(d['mouth'])

			if( (len(d['eyes'])>=2 or len(d['eyes2'])>=1) and len(d['mouth'])>=1 and len(d['nose'])>=1 ): 

				print "Visage detecte dans la photo : "+img
				# ----- Affichage visage ----- #
				affichage_visage((x,y,w,h), src)
				# ----- Affichage de toute les bouches ----- #
				#affichage(src, d['eyes'], d['eyes2'], d['nose'], d['mouth'], x, y)
				# ----- Affichage de la bouche la plus basse (en general la bonne) ----- #
				#affichage(src, d['eyes'], d['eyes2'], d['nose'], d['mouth2'], x, y)

				save(norm_path, dossier+"small_"+str(cp)+"."+img, normal)
				save(result, dossier+"face_"+img, src)
				cp = cp +1

# Traitement apres la normalisation (cad sur les images de visages en NORM_W x NORM_H)
def after_norm(img_n,img_t, boolean_arff,div):

	src = cv.LoadImage(norm_path+img_n)

	# On copie l'image pour le traitement (en gris)
	gris = cv.CreateImage( (src.width, src.height) , cv.IPL_DEPTH_8U, 1)
	cv.CvtColor(src, gris, cv.CV_BGR2GRAY )		
	cv.EqualizeHist(gris, gris)

	#Detection oeil nez bouche sur l'image source:
	d = detection(gris)

	if boolean_arff:
		c = comptage_pixel(img_t,div)
		fill_arff(d, img_n, c, div)	
	else:	
		# ----- Affichage de la bouche la plus basse (en general la bonne) ----- #
		#d['mouth'] = best_mouth(d['mouth'])
		# ----- Affichage de toute les bouches ----- #
		affichage(src, d['eyes'], d['eyes2'], d['nose'], d['mouth'])
		save(dnorm_path, img_n, src)

def traitements(img):

	src = cv.LoadImageM(norm_path+img, 1)
	dst = cv.CreateImage(cv.GetSize(src), cv.IPL_DEPTH_16S, 3)

	# --- Corners --- #
	print "CORNERS"
	#eig_image = cv.CreateMat(src.rows, src.cols, cv.CV_32FC1)
	#temp_image = cv.CreateMat(src.rows, src.cols, cv.CV_32FC1)
	#corners = cv.GoodFeaturesToTrack(src, eig_image, temp_image, 100, 0.04, 1.0, useHarris = True)
	#affichage_corners(corners, src, 2) 
	#save(traitement_path, img, src)
	print "FIN CORNERS"

	# --- Seuil --- #
	print "SEUIL"
	src = cv.LoadImageM(norm_path+img, cv.CV_LOAD_IMAGE_GRAYSCALE)
	cv.AdaptiveThreshold(src,src,255, cv.CV_ADAPTIVE_THRESH_MEAN_C, cv.CV_THRESH_BINARY_INV, 7, 10)
	#cv.Erode(src,src,None,1)
	#cv.Dilate(src,src,None,1)
	print src[56,56]
	save(traitement_path, dossier+"seuil."+img, src)
	print "FIN SEUIL"

	'''
	print "LAPLACE"
	#cv.Laplace(src, dst)
	#save(traitement_path, dossier+"laplace."+fichier, dst)
	print "FIN LAPLACE"

	# --- Sobel --- #
	print "SOBEL"
	#cv.Sobel(src, dst, 1, 1)
	#save(traitement_path, dossier+"sobel."+fichier, dst)
	print "FIN SOBEL"
	'''

def comptage_pixel(img,div):

	res = []
	src = cv.LoadImageM(traitement_path+img, 1)
	largeur = NORM_W/div
	hauteur = NORM_H/div

	# div*div images de largeur NORM_W/div
	for l in range(0, NORM_W, largeur):
		for h in range(0, NORM_H, hauteur):
			nb_pixel = 0
			for l2 in range(largeur):
				for h2 in range(hauteur):
					# On prend le premier du pixel (niveau de gris => R=G=B
					#print src[l+l2,h+h2]
					if(src[l+l2,h+h2][0] > 128) : 
						nb_pixel += 1
			res.append(nb_pixel)
	return res

# Renvoie l'emotion associee au nom de fichier : -
# AN -> anger
# DI -> disgust
# FE -> fear
# HA -> happiness
# NE -> neutral
# SA -> sad
# SU -> surprise
def emotion(file_name):
	try:
		return file_name.split(".")[2][:2]
	except:
		return None

def create_arff(file_name, arff_name, div):
	global arf
	arf = write_arff.ArfFile(file_name, arff_name)
	arf.add_attribute_numeric("eyes")
	arf.add_attribute_numeric("eyes2")
	arf.add_attribute_numeric("mouth")
	arf.add_attribute_numeric("s_0")
	arf.add_attribute_numeric("s_1")
	arf.add_attribute_numeric("s_2")
	arf.add_attribute_numeric("s_3")
	arf.add_attribute_numeric("s_4")
	for i in range(div*div):
		arf.add_attribute_numeric("cpt_"+str(i))
	
	arf.add_attribute_enum("emotion", ["AN", "DI", "FE", "HA", "NE", "SA", "SU"])
	print "Ouverture du fichier "+file_name+" reussie"

def fill_arff(d, file_name, c_pixels, div):

	dic = dict()
	try:
		e = emotion(file_name)
		dic["emotion"] = e
	except: 
		print "Nom de fichier non annote ou incorrect"

	for a in attr_list:
		dic[a] = len(d[a])
	for s in smile_list:
		dic[s] = d[s]
	for i in range(div*div):
		dic["cpt_"+str(i)] = c_pixels[i]
	arf.add_instance(dic)        
	print file_name+" : "+e


# Renvoie l'emotion associee au nom de fichier : -
# AN -> anger
# DI -> disgust
# FE -> fear
# HA -> happiness
# NE -> neutral
# SA -> sad
# SU -> surprise
def emotion(file_name):
	try:
		return file_name.split(".")[2][:2]
	except:
		print "Erreur dans le nom du fichier (emotion incorrecte)"
		return None


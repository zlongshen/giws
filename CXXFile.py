#!/usr/bin/python -u
# Copyright or Copr. INRIA/Scilab - Sylvestre LEDRU
#
# Sylvestre LEDRU - <sylvestre.ledru@inria.fr> <sylvestre@ledru.info>
# 
# This software is a computer program whose purpose is to generate C++ wrapper 
# for Java objects/methods.
# 
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 
# 
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 
# 
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# 
# For more information, see the file COPYING
from classRepresentation.packageGiws import packageGiws
from outputWriter import outputWriter
from JNIFrameWork import JNIFrameWork
from licenseWrapper import licenseWrapper
""" Engine to create the C++ files """


class CXXFile:
	
	package=None
	
	def __init__(self, package):
		if isinstance(package,packageGiws):
			self.package=package
		else:
			raise Exception("The type must be a packageGiws object")


	def getDescriptionHeader(self, config):
		return """/* Generated by GIWS (version %s) */	"""%(config.getVersion())

	
	def __getFileNameForObjectDeclaration(self, config, typeFile, object):
		fileName=object.getName()
		if typeFile=="header":
			fileName+=config.getCPPHeaderExtension()
		else:
			fileName+=config.getCPPBodyExtension()
		return fileName
	
	def __getFileNameForPackageDeclaration(self, config, typeFile):
		fileName=self.package.getNameForCXX()
		if typeFile=="header":
			fileName+=config.getCPPHeaderExtension()
		else:
			fileName+=config.getCPPBodyExtension()
		return fileName

	def getObjectCXX(self, type="header"):
		i=1
		str=""
		for object in self.package.getObjects():
			if type=="header":
				str=str+object.generateCXXHeader(self.package.getNameForJNI())
			else:
				str=str+object.generateCXXBody()
			if len(self.package.getObjects())!=i:
				str+="""
				"""
			i=i+1
		return str

	def getCXXHeader(self, config, objectName=""):
		if config.getSplitPerObject()==True:
			# Split per object ... Then, the define is different for each header
			defineHeader=self.package.getNameForCXX()+"_"+objectName
		else:
			defineHeader=self.package.getNameForCXX()
		return """%s
		%s
		%s
		namespace %s {
		""" % (self.getDescriptionHeader(config), licenseWrapper().getLicense(),JNIFrameWork().getHeader(defineHeader),self.package.getNameForCXX())



	def generateCXXHeader(self,config):

		strCommonEnd="""
		}
		#endif
		"""
		str=""
		if config.getSplitPerObject()==True:
			for object in self.package.getObjects():
				fileName=self.__getFileNameForObjectDeclaration(config, "header",object)
				str=self.getCXXHeader(config,object.getName())+object.generateCXXHeader(self.package.getNameForJNI())+strCommonEnd
				outputWriter().writeIntoFile(config.getOutput(), fileName, str)
				print "%s generated ..."%fileName
		else:
			fileName=self.__getFileNameForPackageDeclaration(config, "header")
			str="""%s
			%s
			%s
			""" % (self.getCXXHeader(config), self.getObjectCXX("header"), strCommonEnd)
			
			outputWriter().writeIntoFile(config.getOutput(),fileName, str)
			print "%s generated ..."%fileName

	def generateCXXBody(self,config):
		strCommon="""%s
		%s
		namespace %s {
		"""%(self.getDescriptionHeader(config),licenseWrapper().getLicense(),  self.package.getNameForCXX())
		
		strCommonEnd="""
		}
		"""
		
		str=""
		
		if config.getSplitPerObject()==True:
			for object in self.package.getObjects():
				strInclude="""#include "%s"
				"""%(self.__getFileNameForObjectDeclaration(config, "header",object))
				
				fileName=self.__getFileNameForObjectDeclaration(config, "body",object)
				str=strInclude+strCommon+object.generateCXXBody()+strCommonEnd
				outputWriter().writeIntoFile(config.getOutput(),fileName, str)
				print "%s generated ..."%fileName
		else:
			strInclude="""#include "%s"
			"""%(self.__getFileNameForPackageDeclaration(config, "header"))
			fileName=self.__getFileNameForPackageDeclaration(config, "body")
			str="""%s
			%s
			%s
			%s
			""" % (strInclude, strCommon, self.getObjectCXX("body"), strCommonEnd)
			outputWriter().writeIntoFile(config.getOutput(),fileName, str)
			print "%s generated ..."%fileName


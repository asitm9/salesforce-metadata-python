# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# Written by: David Lanstein ( dlanstein gmail com )


import sys
import os.path
#import lib.config as config
#import lib.util as util
from suds.plugin import MessagePlugin
from suds.client import Client
from suds.transport.http import HttpTransport as SudsHttpTransport

#debug = config.logger.debug

from suds.cache import FileCache
import suds.sudsobject
from suds.sax.element import Element

class PrunePlugin(MessagePlugin):
	def marshalled(self, context):
		try:
			function_name = context.envelope[1].children[0].name
			if 'getUserInfo' not in function_name:
				#remove empty tags inside the Body element
				#context.envelope[0] is the SOAP-ENV:Header element
				context.envelope[1].prune()
		except:
			context.envelope[1].prune()
          
class SforceBaseClient(object):
	_sforce = None
	_sessionId = None
	_location = None
	_userId = None
	_metadataServerUrl = None
	_product = 'MetaData'
	_version = (0, 0, 6)
	_objectNamespace = None
	_strictResultTyping = False
	_apiVersion = None
	_allowFieldTruncationHeader = None
	_assignmentRuleHeader = None
	_callOptions = None
	_assignmentRuleHeader = None
	_emailHeader = None
	_localeOptions = None
	_loginScopeHeader = None
	_mruHeader = None
	_packageVersionHeader = None
	_queryOptions = None
	_sessionHeader = None
	_userTerritoryDeleteHeader = None
	
	def __init__(self, wsdl, cacheDuration = 0, **kwargs):
		if '://' not in wsdl:
			if os.path.isfile(wsdl):
				if 'darwin' in sys.platform or 'linux' in sys.platform:
					wsdl = 'file:///' + os.path.abspath(wsdl)
		if cacheDuration > 0:
			cache = FileCache()
			cache.setduration(seconds = cacheDuration)
		else:
			cache = None
		
		if 'sid' in kwargs:
			self._sessionId = kwargs['sid']
		if 'metadata_server_url' in kwargs:
			self._metadataServerUrl = kwargs['metadata_server_url']
		xml_response = False
		if 'retxml' in kwargs:
			xml_response = kwargs['retxml']
		self._sforce = Client(wsdl, cache=cache, plugins=[PrunePlugin()], retxml=xml_response, transport=WellBehavedHttpTransport())
		if 'server_url' in kwargs:
			self._setEndpoint(kwargs['server_url'])
		if 'apiVersion' in kwargs:
			if type(kwargs['apiVersion']) == str:
				api_version = float(kwargs['apiVersion'])
			else:
				api_version = kwargs['apiVersion']
			self._apiVersion = api_version
		else:
			self._apiVersion = 27.0
		headers = {u'User-Agent': u'MetaData'}
		self._sforce.set_options(headers = headers)
		
	
	def generateHeader(self, sObjectType):
		try:
			return self._sforce.factory.create(sObjectType)
		except:
			print 'There is not a SOAP header of type %s' % sObjectType
	
	def _setEndpoint(self,location):
		try:
			self._sforce.set_options(location = location)
		except:
			self._sforce.wsdl.service.setlocation(location)
		self._location = location
	
	def setSessionHeader(self, header):
		self._sessionHeader = header
		
	def login(self,username, password,token):
		#self._setHeaders('login')
		result = self._sforce.service.login(username, password + token)
		header = self.generateHeader('SessionHeader')
		header.sessionId = result['sessionId']
		self.setSessionHeader(header)
		self._sessionId = result['sessionId']
		self._userId = result['userId']
		self._setEndpoint(result['serverUrl'])
		self._metadataServerUrl = result['metadataServerUrl']
		
		return result
		

class WellBehavedHttpTransport(SudsHttpTransport):
	def u2handlers(self):
		return []
	
	

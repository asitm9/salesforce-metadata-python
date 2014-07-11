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
# Written by: Asit Mahato(asitm9@gmail.com)


from Sforce import SforceBaseClient
import time
import shutil
import os
import base64
from operator import itemgetter

class SforceMetadataClient(SforceBaseClient):
	
	def __init__(self, wsdl, *args, **kwargs):
		kwargs['isMetadata'] = True
		super(SforceMetadataClient, self).__init__(wsdl, *args, **kwargs)
		header = self.generateHeader('SessionHeader')
		header.sessionId = kwargs['sid']
		self.setSessionHeader(header)
		self._setEndpoint(kwargs['url'])
		#self._setHeaders()
		headers = {'SessionHeader': self._sessionHeader}
		self._sforce.set_options(soapheaders = headers)
	
	def retrievePkg(self,**kwargs):
		obj=self.._sforce.factory.create('RetrieveRequest')
		obj = { 'apiVersion': 29.0 }
		obj = { 'packageNames':  kwargs.get('pkg')}
		response = m._sforce.service.retrieve(obj)
		#return response.id
		self._waitForRequest(response.id)
		zipfile=kwargs.get('zipname','pck.zip')
		f=open(zipfile,'wb')
		res = m._sforce.service.checkRetrieveStatus(response.id)
		data = base64.b64decode(res.zipFile)
		f.write(data)
		f.close()
		
	#TODO
	def deploy(self, params={}, **kwargs):
		is_test = kwargs.get('is_test', False)
		if is_test:
			deploy_options['checkOnly']         = True
			deploy_options['runAllTests']       = False
			deploy_options['runTests']          = params.get('classes', [])
			deploy_options['rollbackOnError']   = params.get('rollback_on_error', True)
		else:
			deploy_options['checkOnly']         = params.get('check_only', False)
			deploy_options['rollbackOnError']   = params.get('rollback_on_error', True)
			deploy_options['runAllTests']       = params.get('run_tests', False)
			deploy_options['runTests']          = params.get('classes', [])
			deploy_options['purgeOnDelete']     = params.get('purge_on_delete', False)
			
		
	def _waitForRequest(self, id):
		finished = False
		checkStatusResponse = None
		while finished == False:
			time.sleep(1)
			checkStatusResponse = self._sforce.service.checkStatus(id)
			finished = checkStatusResponse[0].done


def login(**kwargs):
	partner_wsdl=kwargs.get('partner','partner.wsdl')
	meta_wsdl=kwargs.get('meta','metadata.wsdl')
	s=SforceBaseClient('partner.wsdl',0)
	uName=kwargs.get('u')
	passwd=kwargs.get('p')
	tkn=kwargs.get('t')
	result=s.login(uName,passwd,tkn)
	m=SforceMetadataClient(meta_wsdl,sid=result['sessionId'],url=result['metadataServerUrl'])
	return m
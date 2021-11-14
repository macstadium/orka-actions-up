import json
import os
import random
import requests
import string
import time

class SpinUpOrkaVM:
	def __init__(self):
		self.token = None
		self.vm_name = os.environ["VM_NAME"]
		orka_ip = '10.221.188.100'
		self.orka_address = f"http://{orka_ip}"
		self.orka_user = os.environ["INPUT_ORKA_USER"]
		self.orka_pass = os.environ["INPUT_ORKA_PASS"]
		self.orka_base_image = os.environ["INPUT_ORKA_BASE_IMAGE"]
		self.core_count = os.environ["INPUT_CORE_COUNT"]
		print(f"Core count: {self.core_count}")
		self.vcpu_count = os.environ["INPUT_VCPU_COUNT"]
		print(f"VCPU Count: {self.vcpu_count}")
		self.github_pat = os.environ["INPUT_GITHUB_PAT"]
		repo_and_user_name = os.environ["GITHUB_REPOSITORY"].split('/')
		self.github_repo_name = repo_and_user_name[1]
		self.github_user = repo_and_user_name[0]
		self.gh_session = requests.Session()
		self.gh_session.auth = (self.github_user, self.github_pat)

	def get_auth_token(self):
		data = {'email': self.orka_user, 'password': self.orka_pass}
		result = requests.post(self.orka_address+'/token', data=data)
		content = json.loads(result._content.decode('utf-8'))
		self.token = content['token']

	def create_vm_config(self):
		orka_address = f"{self.orka_address}/resources/vm/create"
		headers = {
			'Content-Type': 'application/json', 
			'Authorization': f"Bearer {self.token}"
			}
		data = {
			'orka_vm_name': self.vm_name,
			'orka_base_image': self.orka_base_image,
			'orka_image': self.vm_name,
			'orka_cpu_core': int(self.core_count),
			'vcpu_count': int(self.vcpu_count)
			}
		requests.post(orka_address, data=json.dumps(data), headers=headers)
        
	def deploy_vm_config(self):
		orka_address = f"{self.orka_address}/resources/vm/deploy"
		headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.token}"}
		data =  {
			'orka_vm_name': self.vm_name, 
			'vm_metadata': {
				"items":[
					{'key':'github_user', 'value':str(self.github_user)}, 
					{'key':'github_pat', 'value':str(self.github_pat)},
					{'key':'github_repo_name', 'value':str(self.github_repo_name)}
					]
				}
			}
		result = requests.post(orka_address, data=json.dumps(data), headers=headers)
		content = json.loads(result._content.decode('utf-8'))
		self.vm_ip = content['ip']
		self.vm_ssh_port = content['ssh_port']

	def revoke_orka_auth_token(self):
		url = f"{self.orka_address}/token"
		headers = {
            	'Content-Type': 'application/json',
            	'Authorization': f"Bearer {self.token}"
            	}
		requests.delete(url, headers=headers)

	def check_runner_status(self):
		url = f"https://api.github.com/repos/{self.github_user}/{self.github_repo_name}/actions/runners"
		result = self.gh_session.get(url)
		content = json.loads(result._content.decode('utf-8'))
		for item in content['runners']:
			if self.vm_name in item['name']:
				return True
		else:
			time.sleep(10)
			self.check_runner_status()

def main(spin_up):
	spin_up.get_auth_token()
	spin_up.create_vm_config()
	spin_up.deploy_vm_config()
	spin_up.revoke_orka_auth_token()
	time.sleep(20)
	spin_up.check_runner_status()
	
if __name__ == '__main__':
	spin_up = SpinUpOrkaVM()
	main(spin_up)
	
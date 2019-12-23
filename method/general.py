import psutil

psutil.getloadavg()

class network:
	network_mask = {
		'255.255.255.0': 24,
		'255.255.255.255': 32,
		'255.255.0.0': 16,
		'255.0.0.0': 8
	}
	@staticmethod
	def get_network_mask(mask: str) -> str:
		if mask in network.network_mask.keys():
			return '/{}'.format(network.network_mask[mask])
		if mask is None:
			return ''
		return '\n     Netmask: {}'.format(mask)
	@staticmethod
	def _get_sub_network_info(info) -> str:
		if info.family == -1:
			return f'Mac address: {info.address}'
		return 'IP address: {}{}'.format(info.address, network.get_network_mask(info.netmask))
	@staticmethod
	def get_sub_network_info(infos) -> str:
		i = 0
		z = []
		for x in infos:
			z.append(f'[{i}]: {network._get_sub_network_info(x)}')
			i += 1
		return '\n'.join(z)
	@staticmethod
	def get_network_infos() -> str:
		addrs = psutil.net_if_addrs()
		infos = []
		for name, info in addrs.items():
			infos.append('Name: {}\nAddress Infos:\n{}'.format(name, network.get_sub_network_info(info)))
		return '\n\n'.join(infos)

if __name__ == "__main__":
	print(network.get_network_infos())
#-*- coding: utf-8 -*-
import _pickle
import xlrd
import csv

def sumdict(a,b):
	if a=='Skip' or b=='Skip':
		return 'Skip'
	if not a:
		return b
	if not b:
		return a

	result = dict()
	for key in a.keys():
		result[key] = a[key]

	for key in b.keys():
		if key in a.keys():
			return 'Skip'
		else:
			result[key]=b[key]

	return result

class Preprocessor:
	def __init__(self):
		pass

	def loaddata(self):
		raise NotImplementedError()

	def process(self):
		raise NotImplementedError()

	def save(self):
		raise NotImplementedError()

class PreprocessorK:
	def __init__(self, predatapath, postdatapath):
		self.predatapath = predatapath
		self.postdatapath = postdatapath

	def loaddata(self):
		wb = xlrd.open_workbook(self.predatapath)
		sheet = wb.sheet_by_name('Sheet1')
		
		#listize.
		nrow = sheet.nrows
		self.predata = [sheet.row_values(index) for index in range(nrow)]
		print('Data loaded.')

	def process(self):
		predata = list(self.predata)

		#remove 1st row (legend)
		predata = predata[1:]
		postdata = list()

		for row_idx, row in enumerate(predata):
			newrow = list(row[:-1])
			newrow.append(self._deal_str(row_idx, row[-1]))

			postdata.append(newrow)

		self.postdata = postdata
		
	def postprocess(self):
		key_list = []

		key_mod_map = {}

		for row in self.postdata:
			dic = row[-1]
			if not dic:
				continue
			keys = list(dic.keys())
			for key in keys:
				#modify key
				origkey = key
				
				key = key.split('(')[0]

				key = key.lower()
				key = key.strip()

				cont = dic[origkey]
				dic.pop(origkey)
				dic[key]=cont

	def stat(self):
		empty_count=0
		key_list={}

		for row in self.postdata:
			dic = row[-1]
			if not dic:
				empty_count+=1
			else:
				keys = list(dic.keys())
				for key in keys:
					if key not in key_list.keys():
						key_list[key]=1
					else:
						key_list[key] += 1

		key_lists = list(key_list.keys())
		key_lists.sort()
		for key in key_lists:
			print(key)
			#print(key_list[key], key)
		print('Key counts:',len(key_list))

		print('Empty count:',empty_count)

	def _deal_str(self, idx, string):
		#1. listize each lines.
		lines = string.split('\n')
		lines = [line.strip() for line in lines]

		#1-1. if ----- is improper, insert it.
		for i, line in enumerate(lines):
			if not line.startswith('-') and '-----' in line:
				lines[i]=line[:line.index('-----')]
				lines.insert(i+1, '---------------------------------')


		#2. count number of =====.
		isdoubleline = [line.startswith('=') for line in lines]
		issingleline = [line.startswith('-') for line in lines]
		gubuns = isdoubleline.count(True)
		if gubuns==0:
			first_process = self._deal_exceptions1(idx, lines)
			if first_process == 'Skip':
				return None
			elif first_process == 'Failed':
				return None
			else:
				return first_process

		elif gubuns==1:
			center_index, upline_index, downline_index = self._extract_lineindices(isdoubleline,issingleline,1)
			
			dictized = self._deal_table(idx, lines, upline_index, center_index, downline_index)
			if dictized=='Skip':
				return None
			return dictized

		elif gubuns==2:
			center_index, upline_index, downline_index = self._extract_lineindices(isdoubleline,issingleline,1)			
			dictized1 = self._deal_table(idx, lines, upline_index, center_index, downline_index)

			center_index, upline_index, downline_index = self._extract_lineindices(isdoubleline,issingleline,2)			
			dictized2 = self._deal_table(idx, lines, upline_index, center_index, downline_index)

			dictized = sumdict(dictized1, dictized2)
			if dictized=='Skip':
				return None
			return dictized

		elif gubuns == 3:
			center_index, upline_index, downline_index = self._extract_lineindices(isdoubleline,issingleline,1)			
			dictized1 = self._deal_table(idx, lines, upline_index, center_index, downline_index)

			center_index, upline_index, downline_index = self._extract_lineindices(isdoubleline,issingleline,2)			
			dictized2 = self._deal_table(idx, lines, upline_index, center_index, downline_index)

			center_index, upline_index, downline_index = self._extract_lineindices(isdoubleline,issingleline,3)			
			dictized3 = self._deal_table(idx, lines, upline_index, center_index, downline_index)

			dictized = sumdict(dictized1, dictized2)
			dictized = sumdict(dictized, dictized3)
			if dictized=='Skip':
				return None
			return dictized


	def _extract_lineindices(self, isdoubleline, issingleline, th):
		center_index=0
		for i in range(th):
			center_index = isdoubleline.index(True, center_index)
			

		upline_index = (len(issingleline[:center_index]) - 1) - issingleline[:center_index][::-1].index(True)
		downline_index = issingleline.index(True, center_index)
		return center_index, upline_index, downline_index

	def _deal_table(self, idx, lines, upline_idx, centerline_idx, downline_idx):
		uselines = lines[upline_idx+1:downline_idx]
		#when more than two columns exist.
		gubs = uselines[0].count('|')
		if gubs!=1:
			return 'Skip'

		one = uselines[0].split('|')[0].strip()
		two = uselines[0].split('|')[1].strip()

		#do nothing.
		if two != 'Result': 
			pass

		centerline_idx -= (upline_idx+1)
		if centerline_idx == 2:
			#when legend is two => multiple columns exist.
			return 'Skip'
				
		uselines = list(filter(lambda line:line, uselines))
		
		#when | is not proper..
		num_imp = 0
		for index in range(2, len(uselines)):
			line = uselines[index].strip()

			bar_count = line.count('|')
			if bar_count==1:
				continue #proper.
			elif bar_count==0:
				return 'Skip' # possibly properable.
			else:
				return 'Skip'

		# finally, add to dict!
		result = dict()

		lastleft = None

		for index in range(2, len(uselines)):
			line = uselines[index].strip()
			left = line.split('|')[0].strip()
			right = line.split('|')[1].strip()

			#if second line of legend,
			if left.startswith('(') or left.startswith('#') or left.startswith('6') or len(left)==0:
				if not lastleft:
					continue
				lastright = result[lastleft]
				result.pop(lastleft)
				newleft = lastleft+left
				lastleft = newleft
				result[newleft] = lastright+right

			else:
				lastleft = left
				result[left] = right
			
		return result

		
		


	def _deal_exceptions1(self, idx, lines):
		emptys = [3857, 3858, 4669, 5063, 5064, 5790, 5791, 7353, 7443, 7444, 7445, 7446, 7447, 7448, 8179]
		skips = [2780, 7500, 7501, 7502, 7522, 7523]
		exceptions = {
			131:{'SMA' : 'negative in tumor nests'},
			4418:{'CK' : 'No isolated tumor cells in sentinel node'},
			4419:{'CK' : 'No isolated tumor cells in sentinel node'},
			4420:{'CK' : 'No isolated tumor cells in sentinel node'},
			7941:{'SMA' : 'Positive in salpingeal muscle'},
			10943:{'ER' : 'negative', 'PR':'negative', 'c-erbB2':'3+'},
			10944:{'ER' : 'negative', 'PR':'negative', 'c-erbB2':'3+'},
			10945:{'ER' : 'negative', 'PR':'negative', 'c-erbB2':'3+'}
			}



		if idx in emptys:
			return None
		elif idx in skips:
			return 'Skip'
		elif idx in exceptions.keys():
			return exceptions[idx]
		else:
			return 'Failed'

	def _deal_exceptions2(self, idx, lines):
		pass
	
	def save(self):
		fieldnames = self.predata[0][:-1]
		keys_list = []
		for row in self.postdata:
			if row[-1]:
				keys_list += list(row[-1].keys())
		keys_list = list(set(keys_list))
		keys_list.sort()
		fieldnames+=keys_list
		dictized_rows = []
		for row in self.postdata:
			row_dict = dict()
			for idx, item in enumerate(row[:-1]):
				row_dict[fieldnames[idx]] = item
			if not row[-1]:
				continue
			else:
				for key in row[-1].keys():
					row_dict[key] = row[-1][key]
			dictized_rows.append(row_dict)


		with open(self.postdatapath, 'w') as f:
			writer= csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
			writer.writeheader()
			writer.writerows(dictized_rows)


		return

		with open(self.postdatapath, 'wb') as f:
			_pickle.dump(self.postdata, f)

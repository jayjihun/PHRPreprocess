#-*- coding: utf-8 -*-
import _pickle
import xlrd

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
			if first_process != 'Failed':
				return first_process
			else:
				#unimplemented exceptions!
				print('Undealt Gubun0 : ',idx)

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
			if line.count('|') != 1:
				num_imp+=1
				#return 'Skip'

		if num_imp == 1:
			print(idx)




		
		


	def _deal_exceptions1(self, idx, lines):
		emptys = [3857, 3858, 5063, 5064, 5790, 5791, 7353, 7443, 7444, 7445, 7446, 7447, 7448, 8179]
		if idx in emptys:
			return None
		else:
			return 'Failed'

	def _deal_exceptions2(self, idx, lines):
		pass
	
	def save(self):
		with open(self.postdatapath, 'wb') as f:
			_pickle.dump(self.postdata, f)

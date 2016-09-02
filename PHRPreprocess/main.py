#<encoding:utf-8>
from Preprocessors import PreprocessorK

def main():
	proc = PreprocessorK(
		r'D:\Datasets\PHR/K_pre.xlsx',
		r'D:\Datasets\PHR/K_processed.pkl'
		)
	proc.loaddata()
	proc.process()
	#proc.save()

if __name__=='__main__':
	main()
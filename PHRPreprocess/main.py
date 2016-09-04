#<encoding:utf-8>
from Preprocessors import PreprocessorK

def main():
	proc = PreprocessorK(
		r'E:\Datasets\PHRPreprocess/K_pre.xlsx',
		r'E:\Datasets\PHRPreprocess/K_processed.csv'
		#r'D:\Datasets\PHR/K_pre.xlsx',
		#r'D:\Datasets\PHR/K_processed.pkl'
		)
	proc.loaddata()
	proc.process()
	proc.postprocess()
	proc.stat()
	proc.save()

if __name__=='__main__':
	main()
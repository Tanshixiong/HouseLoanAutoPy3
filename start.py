# coding:utf-8
import os
import time
import unittest

import yaml

import config
import report
from cases.IntoCases import test_done_task_list, test_fallback, test_into_case, test_special_approval
from cases.baseProcess import (
	test_entry_random_product, test_eyt_input_data, test_gqt_input_data, test_part_raise,
	test_suite_cwd, test_xhd_input_data
	)
from cases.contract_sigining import test_add_contract, test_more_person_sign
from cases.message_authentication import test_contract_message_auth
from cases.others import test_query_house_products
from cases.upload_image_data import test_upload_image_file
from cases.warrantManage import test_warrant_manage
# from lib.HTMLTestRunner import HTMLTestRunner
from lib.HTMLTestRunnerCN import HTMLTestRunner


def set_reporter_path():
	# 定义报告存放路径以及格式
	r_dir = report.__path__[0]
	path = os.path.join(r_dir, 'index.html')
	return path


# 执行用例
def run_case(element, case):
	if element is not None:
		for i in temp[element]:
			suite.addTest(case(i))


if __name__ == "__main__":
	
	# 按照一定格式获取当前时间
	now = time.strftime("%Y-%m-%d %H_%M_%S")
	PT = set_reporter_path()
	# print("path:", PT)
	fp = open(PT, 'wb')
	
	# 创建测试套
	suite = unittest.TestSuite()
	
	suite_list = [
		'cwd',  # 车位贷
		'eyt',  # E押通
		'xhd',  # 循环贷
		'gqt',  # 过桥通
		'IntoCase',  # 申请录入进件场景
		'fallback',  # 回退场景
		'contract',  # 合同签约
		'AddContract',  # 添加拆借人签约
		"SPA",  # 特批
		"PartRaise",  # 部分募资
		"WarrantManage",  # 权证请款
		"UploadImageData",  # 上传影像资料
		"Message",  # 电子签约短信验证
		"DoneList",
		"RandomProduct",  # 随机产品
		"QueryProdcut",  # 查询房贷产品
		]
	
	try:
		rdir = config.__path__[0]
		f1 = os.path.join(rdir, 'caseNumber.yaml')
		with open(f1, 'r', encoding='utf-8') as f:
			temp = yaml.load(f)
			for e in suite_list:
				if e == 'cwd':
					run_case(e, test_suite_cwd.CWD)
				elif e == 'eyt':
					time.sleep(1)
					run_case(e, test_eyt_input_data.EYT)
				elif e == 'xhd':
					run_case(e, test_xhd_input_data.XHD)
				elif e == 'gqt':
					run_case(e, test_gqt_input_data.GQT)
				elif e == 'IntoCase':
					run_case(e, test_into_case.IntoCase)
				elif e == 'fallback':
					run_case(e, test_fallback.FallBack)
				elif e == 'contract':
					run_case(e, test_more_person_sign.ContractSign)
				elif e == 'SPA':
					run_case(e, test_special_approval.SPA)
				elif e == 'AddContract':
					run_case(e, test_add_contract.AddContract)
				elif e == 'PartRaise':
					run_case(e, test_part_raise.PartRaise)
				elif e == 'WarrantManage':
					run_case(e, test_warrant_manage.WarrantManage)
				elif e == 'UploadImageData':
					run_case(e, test_upload_image_file.UploadImageData)
				elif e == 'Message':
					run_case(e, test_contract_message_auth.ElectronicContract)
				elif e == 'DoneList':
					run_case(e, test_done_task_list.DoneList)
				elif e == 'RandomProduct':
					run_case(e, test_entry_random_product.EntryRandomProduct)
				elif e == 'QueryProdcut':
					run_case(e, test_query_house_products.QueryProdcut)
			print("f1:", f1)
	except Exception as e:
		print("Error: can't load file")
		raise e
	
	# 定义测试报告
	runner = HTMLTestRunner(stream=fp, title='测试报告', description='用例执行情况:')
	runner.run(suite)
	
	fp.close()  # 关闭测试报告

# coding:utf-8
import datetime
import time
import unittest

from cases import SET, v_l
from com import custom, base
from com.login import Login
from com.pobj.ContractSign import ContractSign as Cts
from config import product


class CWD(unittest.TestCase, base.Base, SET):
	"""车位贷募资流程"""
	
	# Todo: 这个方法构造函数的第二个参数取值有问题
	# def __init__(self, a=None, env_file="env.json", data_file="data_cwd.json"):
	# 	base.Base.__init__(self,env_file, data_file)
	
	def setUp(self):
		self.env_file = "env.json"
		self.data_file = "data_cwd.json"
		base.Base.__init__(self, self.env_file, self.data_file)
		SET.__init__(self)
		self.se = SET()
		self.se.start_run()
	
	def tearDown(self):
		self.end_time = time.clock()
		self.case_using_time(self.begin_time, self.end_time)
		print(self.using_time)
		v_l.append({
			"name":       self.case_name,
			"apply_code": self.apply_code,
			"result":     self.run_result,
			"u_time":     self.using_time,
			"s_time":     self.s_time,
			"e_time":     str(datetime.datetime.now()).split('.')[0]
			})
		self.se.end_run(v_l)
		self.page.driver.quit()
	
	def skipTest(self, reason):
		pass
	
	def test_cwd_01_base_info(self):
		"""客户基本信息录入"""
		try:
			self.case_name = custom.get_current_function_name()
			custom.print_product_info(self.product_info)
			if self.company['branchName'] not in product.product_city:
				# 非渠道城市进件
				self.HAE.input_customer_base_info(self.page, self.data['applyVo'])
			else:
				# 渠道城市新产品
				self.HAE.input_customer_base_info(self.page, self.data['applyVo'], True)
			self.log.info("客户基本信息录入结束")
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_cwd_02_borrowr_info(self):
		"""借款人/共贷人/担保人信息"""
		
		self.test_cwd_01_base_info()
		self.case_name = custom.get_current_function_name()
		try:
			res = self.HAE.input_customer_borrow_info(self.page, self.data['custInfoVo'][0])
			if res:
				self.log.info("录入借款人信息结束")
		except Exception as e:
			self.log.error("Error:", e)
			self.run_result = False
			raise e
	
	def test_cwd_03_Property_info(self):
		"""物业信息录入"""
		
		self.test_cwd_02_borrowr_info()
		self.case_name = custom.get_current_function_name()
		try:
			res = self.HAE.input_all_bbi_property_info(
				self.page,
				self.data['applyPropertyInfoVo'][0],
				self.data['applyCustCreditInfoVo'][0],
				self.cust_name,
				True
				)
			if res:
				self.log.info("录入物业信息结束")
			else:
				self.log.error('进件失败：录入物业信息出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_cwd_04_applydata(self):
		"""申请件录入,提交"""
		try:
			self.test_cwd_03_Property_info()
			self.case_name = custom.get_current_function_name()
			# 提交
			self.HAE.submit(self.page)
			self.log.info("申请件录入完成提交")
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_cwd_05_get_applyCode(self):
		"""申请件查询"""
		
		self.test_cwd_04_applydata()
		self.case_name = custom.get_current_function_name()
		applycode = self.AQ.get_applycode(self.page, self.cust_name)
		if applycode:
			self.log.info("申请件查询完成")
			self.apply_code = applycode
		else:
			self.run_result = False
			raise ValueError("申请件查询失败")
	
	def test_cwd_06_show_task(self):
		"""查看待处理任务列表"""
		
		self.test_cwd_05_get_applyCode()
		self.case_name = custom.get_current_function_name()
		next_id = self.PM.process_monitor(self.page, self.apply_code)
		if next_id:
			self.log.info("下一个处理人:" + next_id)
			self.next_user_id = next_id
		else:
			self.run_result = False
			raise ValueError("没有找到下一个处理人！")
		self.page.driver.quit()
		
		page = Login(self.next_user_id)
		
		res = self.PT.query_task(page, self.apply_code)
		if res:
			self.log.info("查询待处理任务成功")
		else:
			self.log.error("查询待处理任务失败！")
			raise ValueError("查询待处理任务失败")
	
	def test_cwd_07_process_monitor(self):
		"""流程监控"""
		
		self.test_cwd_05_get_applyCode()  # 申请件查询
		self.case_name = custom.get_current_function_name()
		res = self.PM.process_monitor(self.page, self.apply_code)  # l流程监控
		
		if not res:
			self.run_result = False
			raise ValueError("流程监控查询出错！")
		else:
			self.page.user_info['auth']["username"] = res  # 更新下一个登录人
			self.next_user_id = res
			self.log.info("下一个处理人:" + self.next_user_id)
			self.log.info("完成流程监控查询")
		self.page.driver.quit()
	
	def test_cwd_08_branch_supervisor_approval(self):
		"""分公司主管审批"""
		
		# 获取分公司登录ID
		self.test_cwd_07_process_monitor()
		self.case_name = custom.get_current_function_name()
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		# 审批审核
		res = self.PT.approval_to_review(page, self.apply_code, u'分公司主管同意审批')
		if not res:
			self.run_result = False
			self.log.error("can't find applycode")
			raise ValueError("can't find applycode")
		else:
			self.log.info("风控审批-分公司主管审批结束")
		
		# 查看下一步处理人
		next_id = self.PM.process_monitor(page, self.apply_code)
		if not res:
			self.run_result = False
			raise ValueError("查询下一步处理人出错！")
		else:
			self.next_user_id = next_id
			self.log.info("下一个处理人：" + self.next_user_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_cwd_09_branch_manager_approval(self):
		"""分公司经理审批"""
		
		# 获取分公司经理登录ID
		self.test_cwd_08_branch_supervisor_approval()
		self.case_name = custom.get_current_function_name()
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		# 审批审核
		res = self.PT.approval_to_review(page, self.apply_code, u'分公司经理同意审批')
		if not res:
			self.run_result = False
			raise ValueError("can't find applycode")
		else:
			self.log.info("风控审批-分公司经理审批结束")
		
		# 查看下一步处理人
		res = self.PM.process_monitor(page, self.apply_code)
		if not res:
			self.run_result = False
			raise ValueError("查询下一步处理人出错！")
		else:
			self.next_user_id = res
			self.log.info("下一个处理人：" + self.next_user_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_cwd_10_regional_prereview(self):
		"""区域预复核审批"""
		
		# 获取区域预复核员ID
		self.test_cwd_09_branch_manager_approval()
		self.case_name = custom.get_current_function_name()
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		# 审批审核
		res = self.PT.approval_to_review(page, self.apply_code, u'区域预复核通过')
		if not res:
			self.run_result = False
			self.log.error("can't find applycode")
			raise ValueError("can't find applycode")
		else:
			self.log.info("区域预复核审批结束")
		
		# 查看下一步处理人
		res = self.PM.process_monitor(page, self.apply_code)
		if not res:
			self.run_result = False
			self.log.error("Can't found next user!")
			raise ValueError("没有找到下一个处理人")
		else:
			self.next_user_id = res
			self.log.info("下一步处理人：" + self.next_user_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_cwd_11_manager_approval(self):
		"""高级审批经理审批"""
		
		# 获取审批经理ID
		self.test_cwd_10_regional_prereview()
		self.case_name = custom.get_current_function_name()
		if self.next_user_id != self.senior_manager:
			return
		else:
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 审批审核
			res = self.PT.approval_to_review(page, self.apply_code, u'审批经理审批')
			if not res:
				self.run_result = False
				self.log.ERROR("can't find applycode")
				raise ValueError("can't find applycode")
			else:
				self.log.info("风控审批-审批经理审批结束")
			
			# 查看下一步处理人
			res = self.PM.process_monitor(page, self.apply_code)
			if not res:
				self.run_result = False
				self.log.error("Can't found next user!")
			else:
				self.next_user_id = res
				self.log.info("下一个处理人：" + self.next_user_id)
				# 当前用户退出系统
				self.page.driver.quit()
	
	def test_cwd_12_contract_signing(self):
		"""签约"""
		
		rec_bank_info = dict(
			recBankNum=self.data['houseCommonLoanInfoList'][0]['recBankNum'],
			recPhone=self.data['houseCommonLoanInfoList'][0]['recPhone'],
			recBankProvince=self.data['houseCommonLoanInfoList'][0]['recBankProvince'],
			recBankDistrict=self.data['houseCommonLoanInfoList'][0]['recBankDistrict'],
			recBank=self.data['houseCommonLoanInfoList'][0]['recBank'],
			recBankBranch=self.data['houseCommonLoanInfoList'][0]['recBankBranch'],
			)
		
		# 获取合同打印专员ID
		self.test_cwd_11_manager_approval()
		self.case_name = custom.get_current_function_name()
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		# 签约
		rc = Cts.ContractSign(page, self.apply_code, rec_bank_info)
		res = rc.execute_enter_borroers_bank_info()
		if res:
			rc.contract_submit()
		
		# 查看下一步处理人
		res = self.PM.process_monitor(page, self.apply_code)
		if not res:
			self.run_result = False
			self.log.error("Can't found next User!")
		else:
			self.next_user_id = res
			self.log.info("合同打印完成")
			self.log.info("Next deal User:" + self.next_user_id)
			# 当前用户退出系统
			self.page.driver.quit()
	
	def test_cwd_13_compliance_audit(self):
		"""合规审查"""
		
		# 获取下一步合同登录ID
		self.test_cwd_12_contract_signing()
		self.case_name = custom.get_current_function_name()
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		# 合规审查
		res = self.PT.compliance_audit(page, self.apply_code)
		if res:
			self.log.info("合规审批结束")
			page.driver.quit()
		else:
			self.run_result = False
			raise ValueError("合规审查失败")
	
	def test_cwd_14_authority_card_member_transact(self):
		"""权证办理"""
		
		# 合规审查
		self.test_cwd_13_compliance_audit()
		self.case_name = custom.get_current_function_name()
		# 权证员登录
		page = Login(self.company["authority_member"]["user"])
		# 权证员上传权证信息
		self.WM.authority_card_transact(page, self.apply_code, self.env)
		# 查看下一步处理人
		res = self.PM.process_monitor(page, self.apply_code)
		if not res:
			self.run_result = False
			self.log.error("上传权证资料失败")
			raise ValueError("上传权证资料失败")
		else:
			self.log.info("权证办理完成")
			self.next_user_id = res
			self.log.info("Next deal user:" + self.next_user_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_cwd_15_warrant_apply(self):
		"""权证请款-原件请款"""
		
		# 获取合同打印专员ID
		self.test_cwd_14_authority_card_member_transact()
		self.case_name = custom.get_current_function_name()
		page = Login(self.next_user_id)
		# 权证请款
		res = self.WM.warrant_apply(page, self.apply_code)
		if not res:
			self.run_result = False
			raise ValueError("权证请款失败！")
		else:
			self.log.info("完成权证请款")
			page.driver.quit()
	
	def test_cwd_16_finace_transact(self):
		"""财务办理"""
		
		# 权证请款
		self.test_cwd_15_warrant_apply()
		self.case_name = custom.get_current_function_name()
		# 业务助理登录
		page = Login(self.company["business_assistant"]["user"])
		self.FA.finace_transact(page, self.apply_code)
		self.log.info("完成财务办理")
		
		# 查看下一步处理人
		res = self.PM.process_monitor(page, self.apply_code, 1)
		if not res:
			self.run_result = False
			raise ValueError("Can't found Next User!")
		else:
			self.next_user_id = res
			self.log.info("Next deal User:" + self.next_user_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_cwd_17_finace_approval_branch_manager(self):
		"""财务分公司经理审批"""
		
		remark = u"财务分公司经理审批"
		
		# 下一个处理人
		self.test_cwd_16_finace_transact()
		self.case_name = custom.get_current_function_name()
		page = Login(self.next_user_id)
		result = self.FA.finace_approval(page, self.apply_code, remark)
		
		if not result:
			self.run_result = False
			raise result
		else:
			self.log.info("财务流程-分公司经理审批结束")
			# 查看下一步处理人
			res = self.PM.process_monitor(page, self.apply_code, 1)
			if not res:
				self.run_result = False
				raise ValueError("Can't found Next User!")
			else:
				self.next_user_id = res
				self.log.info("Next deal User:" + self.next_user_id)
				# 当前用户退出系统
				page.driver.quit()
	
	def test_cwd_18_finace_approval_risk_control_manager(self):
		"""财务风控经理审批"""
		
		remark = u'风控经理审批'
		
		self.test_cwd_17_finace_approval_branch_manager()
		self.case_name = custom.get_current_function_name()
		page = Login(self.next_user_id)
		rs = self.FA.finace_approval(page, self.apply_code, remark)
		if rs:
			self.log.info("财务流程-风控经理审批结束")
		else:
			self.run_result = False
			raise ValueError("风控经理审批出错！")
		
		# 查看下一步处理人
		res = self.PM.process_monitor(page, self.apply_code, 1)
		if not res:
			self.run_result = False
			raise ValueError("can't found Next User！")
		else:
			self.next_user_id = res
			self.log.info("nextId:" + self.next_user_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_cwd_19_finace_approval_financial_accounting(self):
		"""财务会计审批"""
		
		remark = u'财务会计审批'
		
		self.test_cwd_18_finace_approval_risk_control_manager()
		self.case_name = custom.get_current_function_name()
		page = Login(self.next_user_id)
		self.FA.finace_approval(page, self.apply_code, remark)
		
		# 查看下一步处理人
		res = self.PM.process_monitor(page, self.apply_code, 1)
		if not res:
			self.run_result = False
			raise ValueError("Can't found next User!")
		else:
			self.log.info("财务流程-财务会计审批结束")
			self.next_user_id = res
			self.log.info("nextId:" + self.next_user_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_cwd_20_finace_approval_financial_manager(self):
		"""财务经理审批"""
		
		remark = u'财务经理审批'
		
		self.test_cwd_19_finace_approval_financial_accounting()
		self.case_name = custom.get_current_function_name()
		page = Login(self.next_user_id)
		res = self.FA.finace_approval(page, self.apply_code, remark)
		if res:
			self.log.info("财务流程-财务经理审批结束")
			page.driver.quit()
		else:
			self.run_result = False
			raise ValueError("财务经理审批出错")
	
	def test_cwd_21_funds_raise(self):
		"""资金主管募资审批"""
		
		remark = u'资金主管审批'
		
		self.test_cwd_20_finace_approval_financial_manager()
		self.case_name = custom.get_current_function_name()
		page = Login(self.treasurer)
		res = self.RA.funds_raise(page, self.apply_code, remark)
		if res:
			self.log.info("募资流程-资金主管审批结束")
			page.driver.quit()
		else:
			self.run_result = False
			raise ValueError("募资流程出错")

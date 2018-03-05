# coding:utf-8
"""
	部分募资
"""

import unittest
import json
import os
from com import common
from com.login import Login
from com.custom import Log, enviroment_change, print_env


class PartRaise(unittest.TestCase):
	"""部分请款募资"""
	
	def setUp(self):
		try:
			import config
			rootdir = config.__path__[0]
			config_env = os.path.join(rootdir, 'env.json')
			print("config_env:" + config_env)
			with open(config_env, 'r', encoding='utf-8') as f:
				self.da = json.load(f)
				self.number = self.da["number"]
				self.env = self.da["enviroment"]
			
			filename = "data_cwd.json"
			data, company = enviroment_change(filename, self.number, self.env)
			self.page = Login()
			self.log = Log()
			f.close()
			# 录入的源数据
			self.data = data
			# 分公司选择
			self.company = company
			print_env(self.env, self.company)
		except Exception as e:
			self.log.error('load config error:', str(e))
			raise e
	
	def risk_approval_result(self, res, mark, page, apply_code):
		"""
		校验风控审批结果
		:param res: 返回值传入
		:param page: 页面对象
		:param apply_code: 申请件code
		:return:
		"""
		if not res:
			self.log.error(mark + ",审批失败")
			raise ValueError(mark + ",审批失败")
		else:
			self.log.info(mark + ",审批通过")
			self.next_user_id = common.get_next_user(page, apply_code)
	
	def tearDown(self):
		self.page.driver.quit()
	
	def test_01_part_receipt_director_approval(self):
		"""400000元部分请款，回执分公司主管审批"""
		
		# ---------------------------------------------------------------------------------
		#                   1. 申请录入
		# ---------------------------------------------------------------------------------
		
		self.data['applyVo']['applyAmount'] = 400000
		# 1 客户信息-业务基本信息
		if common.input_customer_base_info(self.page, self.data['applyVo']):
			self.log.info("录入基本信息完成")
		
		# 2 客户基本信息 - 借款人/共贷人/担保人信息
		self.custName = common.input_customer_borrow_info(self.page, self.data['custInfoVo'][0])[1]
		
		# 3 物业信息
		common.input_cwd_bbi_property_info(
				self.page, self.data['applyPropertyInfoVo'][0],
				self.data['applyCustCreditInfoVo'][0]
				)
		# 提交
		common.submit(self.page)
		self.log.info("申请件录入完成提交")
		
		apply_code = common.get_applycode(self.page, self.custName)
		if apply_code:
			self.apply_code = apply_code
			self.log.info("申请件查询完成")
			print("apply_code:" + self.apply_code)
		# 流程监控
		result = common.process_monitor(self.page, apply_code)
		if result is not None:
			self.next_user_id = result
			self.log.info("完成流程监控查询")
		else:
			raise ValueError("流程监控查询出错！")
		
		# ---------------------------------------------------------------------------------------
		# 	                        2. 风控审批流程
		# ---------------------------------------------------------------------------------------
		
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		list_mark = [
			"分公司主管审批",
			"分公司经理审批",
			"区域预复核审批",
			"高级审批经理审批"
			]
		
		for e in list_mark:
			res = common.approval_to_review(page, apply_code, e, 0)
			self.risk_approval_result(res, e, page, apply_code)
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
		
		# -----------------------------------------------------------------------------
		# 	                        3. 合同打印
		# -----------------------------------------------------------------------------
		
		rec_bank_info = dict(
				recBankNum=self.data['houseCommonLoanInfoList'][0]['recBankNum'],
				recPhone=self.data['houseCommonLoanInfoList'][0]['recPhone'],
				recBankProvince=self.data['houseCommonLoanInfoList'][0]['recBankProvince'],
				recBankDistrict=self.data['houseCommonLoanInfoList'][0]['recBankDistrict'],
				recBank=self.data['houseCommonLoanInfoList'][0]['recBank'],
				recBankBranch=self.data['houseCommonLoanInfoList'][0]['recBankBranch'],
				)
		# next transcat person
		self.next_user_id = common.get_next_user(page, self.apply_code)
		
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		# 两个人签约
		res = common.make_signing(page, self.apply_code, rec_bank_info, 2)
		if res:
			self.log.info("合同打印完成！")
			# 查看下一步处理人
			self.next_user_id = common.get_next_user(page, apply_code)
		
		# -----------------------------------------------------------------------------
		#                                合规审查
		# -----------------------------------------------------------------------------
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		
		# 合规审查
		res = common.compliance_audit(page, self.apply_code)
		if res:
			self.log.info("合规审批结束")
			page.driver.quit()
		else:
			self.log.error("合规审查失败")
			raise ValueError("合规审查失败")
		
		# -----------------------------------------------------------------------------
		#                                权证办理
		# -----------------------------------------------------------------------------
		page = Login(self.company["authority_member"]["user"])
		# 权证员上传权证信息
		res = common.authority_card_transact(page, self.apply_code, self.env)
		if not res:
			self.log.error("上传权证资料失败")
			raise ValueError("上传权证资料失败")
		else:
			self.log.info("权证办理完成")
			self.next_user_id = common.get_next_user(page, self.apply_code)
		
		# -----------------------------------------------------------------------------
		#                                权证请款
		# -----------------------------------------------------------------------------
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		# 部分请款
		res = common.part_warrant_apply(page, self.apply_code)
		if not res:
			self.log.error("权证请款失败！")
			raise ValueError('权证请款失败！')
		else:
			self.log.info("完成权证请款")
			self.next_user_id = common.get_next_user(page, self.apply_code)
		
		# -----------------------------------------------------------------------------
		#                                回执提放审批审核，回执分公司主管审批
		# -----------------------------------------------------------------------------
		page = Login(self.next_user_id)
		rec = common.receipt_return(page, self.apply_code)
		if not rec:
			self.log.error("回执分公司主管审批失败")
			raise ValueError('失败')
		else:
			self.log.info("回执分公司主管审批通过")
			self.next_user_id = common.get_next_user(page, self.apply_code)
	
	def test_02_part_receipt_manage_approval(self):
		"""回执分公司经理审批"""
		self.test_01_part_receipt_director_approval()
		
		page = Login(self.next_user_id)
		rec = common.receipt_return(page, self.apply_code)
		if not rec:
			self.log.error("回执审批经理审批失败")
			raise ValueError('失败')
		else:
			self.log.info("回执审批经理审批通过")
			self.next_user_id = common.get_next_user(page, self.apply_code)
	
	def test_03_receipt_first_approval(self):
		"""第一次回执放款申请"""
		self.test_02_part_receipt_manage_approval()
		
		page = Login(self.next_user_id)
		rec = common.receipt_return(page, self.apply_code)
		if not rec:
			self.log.error("第一次回执放款申请失败")
			raise ValueError('失败')
		else:
			self.log.info("第一次回执放款申请通过")
			self.next_user_id = common.get_next_user(page, self.apply_code)
	
	def test_04_part_finace_transact(self):
		"""部分请款-财务办理"""
		
		# 权证请款
		self.test_03_receipt_first_approval()
		# 业务助理登录
		page = Login(self.company["business_assistant"]["user"])
		rs = common.finace_transact(page, self.apply_code)
		if not rs:
			self.log.error("财务办理失败")
			raise AssertionError('财务办理失败')
		else:
			self.log.info("财务办理结束！")
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 1)
	
	def test_05_part_finace_branch_manage_aproval(self):
		"""财务分公司经理审批"""
		remark = u"财务分公司经理审批"
		
		self.test_04_part_finace_transact()
		page = Login(self.next_user_id)
		result = common.finace_approve(page, self.apply_code, remark)
		if not result:
			Log().error("财务流程-分公司经理审批失败")
			raise AssertionError('财务流程-分公司经理审批失败')
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 1)
	
	def test_06_part_finace_approve_risk_control_manager(self):
		"""财务风控经理审批"""
		
		remark = u'风控经理审批'
		
		self.test_05_part_finace_branch_manage_aproval()
		page = Login(self.next_user_id)
		result = common.finace_approve(page, self.apply_code, remark)
		if not result:
			Log().error("财务流程-风控经理审批出错")
			raise AssertionError('财务流程-风控经理审批出错')
		else:
			Log().info("财务流程-风控经理审批完成")
		
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 1)
	
	def test_07_part_finace_approve_financial_accounting(self):
		"""财务会计审批"""
		
		remark = u'财务会计审批'
		
		self.test_06_part_finace_approve_risk_control_manager()
		page = Login(self.next_user_id)
		rs = common.finace_approve(page, self.apply_code, remark)
		if not rs:
			Log().error("财务流程-财务会计审批失败")
			raise AssertionError('财务流程-财务会计审批失败')
		else:
			Log().info("财务流程-财务会计审批完成")
		
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 1)
	
	def test_08_part_finace_approve_financial_manager(self):
		"""财务经理审批"""
		
		remark = u'财务经理审批'
		
		self.test_07_part_finace_approve_financial_accounting()
		page = Login(self.next_user_id)
		res = common.finace_approve(page, self.apply_code, remark)
		if not res:
			Log().error("财务流程-财务经理审批失败")
			raise AssertionError('财务流程-财务经理审批失败')
		else:
			Log().info("财务流程-财务经理审批完成")
			self.page.driver.quit()
	
	def test_09_part_funds_raise(self):
		"""资金主管募资审批"""
		
		remark = u'资金主管审批'
		
		self.test_08_part_finace_approve_financial_manager()
		page = Login('xn0007533')
		res = common.funds_raise(page, self.apply_code, remark)
		if not res:
			Log().error("募资-资金主管审批失败")
			raise AssertionError('募资-资金主管审批失败')
		else:
			Log().info("募资-资金主管审批完成!")
			self.page.driver.quit()
	
	def test_10_part_authority_card_second_deal(self):
		"""第二次权证办理"""
		self.test_09_part_funds_raise()
		page = Login(self.company["authority_member"]["user"])
		# 权证员上传权证信息
		res = common.authority_card_transact(page, self.apply_code, self.env)
		if not res:
			self.log.error("上传权证资料失败")
			raise ValueError("上传权证资料失败")
		else:
			self.log.info("权证办理完成")
			self.next_user_id = common.get_next_user(page, self.apply_code)
	
	def test_11_part_warrent_request_money(self):
		"""第二次权证请款"""
		
		self.test_10_part_authority_card_second_deal()
		# 下一个处理人重新登录
		page = Login(self.next_user_id)
		# 部分请款
		res = common.part_warrant_apply(page, self.apply_code, 1)
		if not res:
			self.log.error("权证请款失败！")
			raise ValueError('权证请款失败！')
		else:
			self.log.info("完成权证请款")
			self.next_user_id = common.get_next_user(page, self.apply_code)
	
	def test_12_part_finace_transact_second(self):
		"""第二次财务办理"""
		
		self.test_11_part_warrent_request_money()
		# 业务助理登录
		page = Login(self.company["business_assistant"]["user"])
		rs = common.finace_transact(page, self.apply_code)
		if not rs:
			self.log.error("财务办理失败")
			raise AssertionError('财务办理失败')
		else:
			self.log.info("财务办理结束！")
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 2)
	
	def test_13_part_finace_branch_manage_aproval_second(self):
		"""第二次财务分公司主管审批"""
		remark = u"财务分公司经理审批"
		
		self.test_12_part_finace_transact_second()
		page = Login(self.next_user_id)
		result = common.finace_approve(page, self.apply_code, remark)
		if not result:
			Log().error("财务流程-分公司经理审批失败")
			raise AssertionError('财务流程-分公司经理审批失败')
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 2)
	
	def test_14_part_finace_approve_risk_control_manager(self):
		"""第二次财务风控经理审批"""
		remark = u'风控经理审批'
		
		self.test_13_part_finace_branch_manage_aproval_second()
		page = Login(self.next_user_id)
		result = common.finace_approve(page, self.apply_code, remark)
		if not result:
			Log().error("财务流程-风控经理审批出错")
			raise AssertionError('财务流程-风控经理审批出错')
		else:
			Log().info("财务流程-风控经理审批完成")
		
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 2)
	
	def test_15_part_finace_approve_financial_accounting_second(self):
		"""第二次财务会计审批"""
		
		remark = u'财务会计审批'
		
		self.test_14_part_finace_approve_risk_control_manager()
		page = Login(self.next_user_id)
		rs = common.finace_approve(page, self.apply_code, remark)
		if not rs:
			Log().error("财务流程-财务会计审批失败")
			raise AssertionError('财务流程-财务会计审批失败')
		else:
			Log().info("财务流程-财务会计审批完成")
		
		# 查看下一步处理人
		self.next_user_id = common.get_next_user(page, self.apply_code, 2)
	
	def test_16_finace_approve_financial_manager_second(self):
		"""财务经理审批"""
		
		remark = u'财务经理审批'
		
		self.test_15_part_finace_approve_financial_accounting_second()
		page = Login(self.next_user_id)
		res = common.finace_approve(page, self.apply_code, remark)
		if not res:
			Log().error("财务流程-财务经理审批失败")
			raise AssertionError('财务流程-财务经理审批失败')
		else:
			Log().info("财务流程-财务经理审批完成")
			self.page.driver.quit()
	
	def test_17_part_funds_raise_second(self):
		"""第二次募资发起"""
		
		remark = u'资金主管审批'
		
		self.test_16_finace_approve_financial_manager_second()
		page = Login('xn0007533')
		res = common.funds_raise(page, self.apply_code, remark)
		if not res:
			Log().error("募资-资金主管审批失败")
			raise AssertionError('募资-资金主管审批失败')
		else:
			Log().info("募资-资金主管审批完成!")
			self.page.driver.quit()